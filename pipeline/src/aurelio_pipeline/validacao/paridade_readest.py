"""Validação independente do artefato do Readest (RF-05, D-12; tolerância zero).

Independência é o valor do gate: este módulo não importa o agrupamento nem o
escritor. Ele recalcula, a partir de headwords, mapa de formas e lemas
frequentes, qual página cada chave deve abrir (RN-02 a RN-06) e confere o
artefato imitando a busca do Readest: `.idx` primeiro, depois `.syn`, com a
comparação do `cmpAscii` (minúsculas por unidades UTF-16). Cada página é
recortada no divisor `<hr>` e cada artigo é identificado pelo `<b>lema</b>`
que o abre.

Relatório integral, sem parada precoce: todos os checks rodam e as falhas
são contadas por check; o detalhe nominal guarda até 50 por check.
"""

import bisect
import gzip
import hashlib
import html as html_stdlib
import logging
import random
import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Callable, Collection, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path

from aurelio_pipeline.validacao.leitor_stardict import LeitorStarDict
from aurelio_pipeline.validacao.paridade import (
    ParityReport,
    normalizar_texto,
    texto_de_html,
)

log = logging.getLogger("aurelio.paridade_readest")

SEED_CONTEUDO_PADRAO = 20261015
AMOSTRA_PADRAO = 500
LIMITE_DETALHES = 50
BOOKNAME_ESPERADO = "Aurélio (uso pessoal, Readest)"
DIVISOR = "<hr>"
CHECKS = (
    "ordem-idx",
    "ordem-syn",
    "unicidade-cruzada",
    "nfc",
    "pagina-artigos",
    "chaves-inesperadas",
    "acesso-isolado-sem-copia",
    "metadados-ifo",
    "amostra-conteudo",
)

_LETRA = re.compile(r"[^\W\d_]")
_ABERTURA = re.compile(r"<b>(.*?)</b>", re.S)


def _comparacao(texto: str) -> bytes:
    """`cmpAscii` do Readest: `toLowerCase()` e comparação por unidades UTF-16."""
    return texto.lower().encode("utf-16-be")


def _dobrado(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c)).lower()


def paginas_esperadas(
    headwords: Sequence[str],
    mapa: Mapping[str, Sequence[str]],
    frequentes: Collection[str],
) -> tuple[dict[str, tuple[str, ...]], set[str]]:
    """Recalcula, sem o agrupamento, a página de cada chave e o conjunto das chaves de lema."""
    por_chave: dict[str, set[str]] = defaultdict(set)
    chaves_de_lema: set[str] = set()
    for lema in headwords:
        por_chave[lema.lower()].add(lema)
        chaves_de_lema.add(lema.lower())
    for lema, formas in mapa.items():
        for forma in formas:
            if _LETRA.search(forma):
                por_chave[forma.lower()].add(lema)

    def posicao(chave: str, lema: str) -> tuple:
        if lema.lower() == chave:
            return (0, lema != chave, _dobrado(lema), lema)
        return (1, lema not in frequentes, _dobrado(lema), lema)

    esperadas = {
        chave: tuple(sorted(lemas, key=lambda lema: posicao(chave, lema)))
        for chave, lemas in por_chave.items()
    }
    return esperadas, chaves_de_lema


class _Divergencias:
    def __init__(self) -> None:
        self.detalhes: list[dict[str, str]] = []
        self.contagem: Counter[str] = Counter()

    def __call__(self, check: str, detalhe: str) -> None:
        self.contagem[check] += 1
        if self.contagem[check] <= LIMITE_DETALHES:
            self.detalhes.append({"check": check, "detalhe": detalhe})
            log.warning("divergencia check=%s detalhe=%s", check, detalhe)


def _lemas_da_pagina(pagina: str) -> list[str] | None:
    lemas = []
    for artigo in pagina.split(DIVISOR):
        abertura = _ABERTURA.match(artigo)
        if abertura is None:
            return None
        lemas.append(html_stdlib.unescape(abertura.group(1)))
    return lemas


def executar_validacao_readest(
    diretorio: Path,
    *,
    headwords: Sequence[str],
    mapa: Mapping[str, Sequence[str]],
    frequentes: Collection[str],
    textos_definicoes: Callable[[str], Sequence[str]],
    data: str,
    amostra: int = AMOSTRA_PADRAO,
    seed: int = SEED_CONTEUDO_PADRAO,
    gerado_em: str | None = None,
) -> ParityReport:
    diretorio = Path(diretorio)
    leitor = LeitorStarDict(diretorio)
    reprovar = _Divergencias()

    palavras_idx = [palavra for palavra, _, _ in leitor.entradas]
    palavras_syn = [forma for forma, _ in leitor.sinonimos]
    chaves_idx = [_comparacao(p) for p in palavras_idx]
    chaves_syn = [_comparacao(p) for p in palavras_syn]

    # ---- ordem estrita na comparação do Readest (RF-04)
    for check, palavras, chaves in (
        ("ordem-idx", palavras_idx, chaves_idx),
        ("ordem-syn", palavras_syn, chaves_syn),
    ):
        for i in range(1, len(chaves)):
            if not chaves[i - 1] < chaves[i]:
                reprovar(
                    check,
                    f"posição {i}: {palavras[i - 1]!r} não precede {palavras[i]!r}",
                )

    # ---- cada chave uma vez entre os dois índices; grafias em NFC
    for chave in sorted(set(chaves_idx) & set(chaves_syn)):
        reprovar("unicidade-cruzada", f"chave={chave.decode('utf-16-be')} no .idx e no .syn")
    for palavra in palavras_idx + palavras_syn:
        if not unicodedata.is_normalized("NFC", palavra):
            reprovar("nfc", f"grafia fora de NFC: {palavra!r}")

    # ---- busca simulada do Readest: .idx, depois .syn → índice da entrada do .idx
    def buscar(chave: str) -> int | None:
        alvo = _comparacao(chave)
        i = bisect.bisect_left(chaves_idx, alvo)
        if i < len(chaves_idx) and chaves_idx[i] == alvo:
            return i
        j = bisect.bisect_left(chaves_syn, alvo)
        if j < len(chaves_syn) and chaves_syn[j] == alvo:
            return leitor.sinonimos[j][1]
        return None

    lemas_por_entrada: dict[int, list[str] | None] = {}

    def lemas_da_entrada(i: int) -> list[str] | None:
        if i not in lemas_por_entrada:
            lemas_por_entrada[i] = _lemas_da_pagina(leitor.artigo(i))
        return lemas_por_entrada[i]

    # ---- todas as páginas (RF-05): exatamente os artigos esperados, na ordem
    esperadas, chaves_de_lema = paginas_esperadas(headwords, mapa, frequentes)
    paginas_ok = 0
    entrada_da_chave: dict[str, int] = {}
    for chave in sorted(esperadas, key=_comparacao):
        esperado = esperadas[chave]
        i = buscar(chave)
        if i is None:
            reprovar("pagina-artigos", f"chave={chave} não encontrada pela busca do Readest")
            continue
        entrada_da_chave[chave] = i
        obtido = lemas_da_entrada(i)
        if obtido is None:
            reprovar("pagina-artigos", f"chave={chave} com artigo sem <b>lema</b> de abertura")
            continue
        if tuple(obtido) == esperado:
            paginas_ok += 1
            continue
        faltam, sobram = set(esperado) - set(obtido), set(obtido) - set(esperado)
        if faltam or sobram or len(obtido) != len(esperado):
            reprovar(
                "pagina-artigos",
                f"chave={chave} faltam={sorted(faltam)} sobram={sorted(sobram)} "
                f"artigos={len(obtido)} esperados={len(esperado)}",
            )
        else:
            reprovar(
                "pagina-artigos",
                f"chave={chave} ordem esperada={list(esperado)} obtida={obtido}",
            )

    esperadas_cmp = {_comparacao(chave) for chave in esperadas}
    for palavra in palavras_idx + palavras_syn:
        if _comparacao(palavra) not in esperadas_cmp:
            reprovar("chaves-inesperadas", f"chave sem página esperada: {palavra!r}")

    # ---- acesso isolado (RF-03): forma de um só lema aponta para dentro da página do lema
    for chave, esperado in esperadas.items():
        if chave in chaves_de_lema or len(esperado) != 1 or chave not in entrada_da_chave:
            continue
        pagina_do_lema = entrada_da_chave.get(esperado[0].lower())
        if pagina_do_lema is None:
            continue
        _, offset, tamanho = leitor.entradas[entrada_da_chave[chave]]
        _, inicio, extensao = leitor.entradas[pagina_do_lema]
        if not (inicio <= offset and offset + tamanho <= inicio + extensao):
            reprovar(
                "acesso-isolado-sem-copia",
                f"chave={chave} trecho=({offset}, {tamanho}) fora da página de "
                f"{esperado[0]} ({inicio}, {extensao})",
            )

    # ---- metadados do .ifo (D-11)
    basename = sorted(diretorio.glob("*.ifo"))[0].stem
    hasher = hashlib.sha256()
    hasher.update((diretorio / f"{basename}.idx").read_bytes())
    hasher.update((diretorio / f"{basename}.syn").read_bytes())
    hasher.update(gzip.decompress((diretorio / f"{basename}.dict.dz").read_bytes()))
    impressao = hasher.hexdigest()[:16]
    declarados = {
        "wordcount": str(len(leitor.entradas)),
        "synwordcount": str(len(leitor.sinonimos)),
        "idxfilesize": str(leitor.idx_bytes),
        "version": "3.0.0",
        "bookname": BOOKNAME_ESPERADO,
        "sametypesequence": "h",
        "date": data,
    }
    for campo, esperado_ifo in declarados.items():
        if leitor.ifo.get(campo) != esperado_ifo:
            reprovar(
                "metadados-ifo",
                f"{campo}: declarado={leitor.ifo.get(campo)} esperado={esperado_ifo}",
            )
    if not leitor.ifo.get("description", "").endswith(f"conteúdo {impressao}"):
        reprovar("metadados-ifo", f"description sem a impressão digital do conteúdo {impressao}")

    # ---- amostra de conteúdo (RF-05): definições do banco na página do lema
    populacao = sorted(set(headwords))
    sorteio = random.Random(seed).sample(populacao, min(amostra, len(populacao)))
    conteudo_ok = 0
    for lema in sorteio:
        i = entrada_da_chave.get(lema.lower())
        if i is None:
            reprovar("amostra-conteudo", f"lema={lema} sem página")
            continue
        texto = texto_de_html(leitor.artigo(i))
        ausentes = [t for t in textos_definicoes(lema) if normalizar_texto(t) not in texto]
        for ausente in ausentes:
            reprovar("amostra-conteudo", f"lema={lema} definição ausente: {ausente[:120]}")
        if not ausentes:
            conteudo_ok += 1

    contagens = {
        "chaves_esperadas": len(esperadas),
        "chaves_idx": len(palavras_idx),
        "chaves_syn": len(palavras_syn),
        "paginas_ok": paginas_ok,
        "wordcount_ifo": int(leitor.ifo.get("wordcount", -1)),
        "synwordcount_ifo": int(leitor.ifo.get("synwordcount", -1)),
    }
    contagens.update({f"falhas_{check}": reprovar.contagem[check] for check in CHECKS})
    relatorio = ParityReport(
        veredito="aprovado" if not reprovar.contagem else "reprovado",
        gerado_em=gerado_em or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        seeds={"conteudo": seed},
        contagens=contagens,
        amostras={"conteudo_ok": conteudo_ok},
        divergencias=reprovar.detalhes,
    )
    log.info(
        "validacao_readest veredito=%s falhas=%d paginas_ok=%d chaves=%d conteudo_ok=%d",
        relatorio.veredito,
        sum(reprovar.contagem.values()),
        paginas_ok,
        len(esperadas),
        conteudo_ok,
    )
    return relatorio
