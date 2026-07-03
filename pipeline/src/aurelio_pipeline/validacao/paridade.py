"""Checks de paridade banco ↔ artefato (spec validacao-paridade §6).

Tolerância zero: qualquer divergência reprova. Relatório integral, sem parada
precoce — uma execução reprovada dá o quadro completo. Amostragens com seed
fixa registrada tornam o veredito reproduzível (D-09). A comparação de conteúdo
normaliza whitespace dos dois lados (decisão em requirements §9, D-08).
"""

import html as html_stdlib
import json
import logging
import random
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from aurelio_pipeline.validacao.leitor_stardict import LeitorStarDict

log = logging.getLogger("aurelio.paridade")

SEED_VERBETES_PADRAO = 20260703
SEED_FLEXOES_PADRAO = 20260704
AMOSTRA_PADRAO = 500

_TAGS = re.compile(r"<[^>]+>")


def normalizar_texto(texto: str) -> str:
    return " ".join(texto.split())


def texto_de_html(conteudo: str) -> str:
    # Tags inline saem por string vazia — mesma derivação usada pelo banco para
    # content_text (RB-03); trocar por espaço criaria "sucuri ." ≠ "sucuri.".
    return normalizar_texto(html_stdlib.unescape(_TAGS.sub("", conteudo)))


@dataclass
class ParityReport:
    veredito: str
    gerado_em: str
    seeds: dict[str, int]
    contagens: dict[str, int]
    amostras: dict[str, int]
    divergencias: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "veredito": self.veredito,
            "gerado_em": self.gerado_em,
            "seeds": dict(self.seeds),
            "contagens": dict(self.contagens),
            "amostras": dict(self.amostras),
            "divergencias": [dict(d) for d in self.divergencias],
        }


def executar_paridade(
    leitor: LeitorStarDict,
    *,
    headwords_esperados: Sequence[str],
    syn_esperado: int,
    mapa: Mapping[str, Sequence[str]],
    textos_definicoes: Callable[[str], Sequence[str]],
    amostra: int = AMOSTRA_PADRAO,
    seed_verbetes: int = SEED_VERBETES_PADRAO,
    seed_flexoes: int = SEED_FLEXOES_PADRAO,
    gerado_em: str | None = None,
) -> ParityReport:
    divergencias: list[dict[str, str]] = []

    def reprovar(check: str, detalhe: str) -> None:
        divergencias.append({"check": check, "detalhe": detalhe})
        log.warning("divergencia check=%s detalhe=%s", check, detalhe)

    # ---- contagens integrais (RF-02, RF-03)
    obtidos = leitor.headwords
    if len(obtidos) != len(headwords_esperados):
        reprovar(
            "contagem-headwords",
            f"esperado={len(headwords_esperados)} obtido={len(obtidos)}",
        )
    else:
        faltam = sorted(set(headwords_esperados) - set(obtidos))[:5]
        sobram = sorted(set(obtidos) - set(headwords_esperados))[:5]
        if faltam or sobram:
            reprovar(
                "contagem-headwords",
                f"contagem igual mas conjuntos diferem; faltam={faltam} sobram={sobram}",
            )

    if len(leitor.sinonimos) != syn_esperado:
        reprovar(
            "contagem-syn",
            f"esperado={syn_esperado} obtido={len(leitor.sinonimos)}",
        )

    # ---- metadados do .ifo coerentes com o conteúdo real (RF-02/RF-03, EC-05)
    declarados = {
        "wordcount": len(leitor.entradas),
        "synwordcount": len(leitor.sinonimos),
        "idxfilesize": leitor.idx_bytes,
    }
    for chave, real in declarados.items():
        declarado = int(leitor.ifo.get(chave, -1))
        if declarado != real:
            reprovar("metadados-ifo", f"{chave}: declarado={declarado} real={real}")

    # ---- amostra de conteúdo dos verbetes (RF-04)
    indice_por_headword = {palavra: i for i, palavra in enumerate(obtidos)}
    populacao_verbetes = sorted(headwords_esperados)
    k_verbetes = min(amostra, len(populacao_verbetes))
    sorteio_verbetes = random.Random(seed_verbetes).sample(
        populacao_verbetes, k_verbetes
    )
    verbetes_ok = 0
    for lemma in sorteio_verbetes:
        posicao = indice_por_headword.get(lemma)
        if posicao is None:
            reprovar("amostra-verbetes", f"lemma={lemma} ausente do .idx")
            continue
        texto_artigo = texto_de_html(leitor.artigo(posicao))
        ausentes = [
            texto
            for texto in textos_definicoes(lemma)
            if normalizar_texto(texto) not in texto_artigo
        ]
        if ausentes:
            for texto in ausentes:
                reprovar(
                    "amostra-verbetes",
                    f"lemma={lemma} definição ausente no artigo: {texto[:120]}",
                )
        else:
            verbetes_ok += 1

    # ---- amostra de destinos do .syn (RF-05)
    pares = sorted(
        (forma, headword) for headword, formas in mapa.items() for forma in formas
    )
    k_flexoes = min(amostra, len(pares))
    sorteio_flexoes = random.Random(seed_flexoes).sample(pares, k_flexoes)
    destinos = {(forma, obtidos[i]) for forma, i in leitor.sinonimos}
    flexoes_ok = 0
    for forma, headword in sorteio_flexoes:
        if (forma, headword) in destinos:
            flexoes_ok += 1
        else:
            reprovar(
                "amostra-flexoes",
                f"forma={forma} sem entrada no .syn com destino esperado={headword}",
            )

    relatorio = ParityReport(
        veredito="aprovado" if not divergencias else "reprovado",
        gerado_em=gerado_em
        or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        seeds={"verbetes": seed_verbetes, "flexoes": seed_flexoes},
        contagens={
            "headwords_idx": len(obtidos),
            "headwords_esperado": len(headwords_esperados),
            "syn": len(leitor.sinonimos),
            "syn_esperado": syn_esperado,
            "wordcount_ifo": int(leitor.ifo.get("wordcount", -1)),
            "synwordcount_ifo": int(leitor.ifo.get("synwordcount", -1)),
        },
        amostras={"verbetes_ok": verbetes_ok, "flexoes_ok": flexoes_ok},
        divergencias=divergencias,
    )
    log.info(
        "paridade veredito=%s divergencias=%d verbetes_ok=%d flexoes_ok=%d",
        relatorio.veredito,
        len(divergencias),
        verbetes_ok,
        flexoes_ok,
    )
    return relatorio


def gravar_relatorio(relatorio: ParityReport, caminho: Path) -> None:
    caminho.write_text(
        json.dumps(relatorio.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
