"""Agrupamento por chave do alvo Readest (RF-02, RF-03, RF-04; domínio puro, sem I/O).

O Readest devolve um único resultado por consulta e compara palavras em
minúsculas, por unidades UTF-16 (`cmpAscii` de `stardictReader.ts`). Para que
ele mostre o mesmo que o KOReader, cada chave pesquisável abre uma página com
todos os artigos a que corresponde (RN-02), e só eles (RN-03). Este módulo
decide quais artigos cada página tem, em que ordem e em que índice a chave
entra; a escrita dos bytes fica em `infra/escrita_readest.py`.
"""

import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Collection, Iterable, Mapping, Sequence

from aurelio_pipeline.dominio.modelos import (
    PaginaReadest,
    PlanoPaginas,
    RelatorioAgrupamento,
)

# Letra = caractere de palavra que não é dígito nem sublinhado (D-04)
_LETRA = re.compile(r"[^\W\d_]")


def chave_readest(texto: str) -> str:
    """Duas grafias com a mesma chave são, para o Readest, a mesma palavra."""
    return texto.lower()


def ordem_readest(texto: str) -> bytes:
    """Ordenação idêntica ao `cmpAscii` do Readest: minúsculas por unidades UTF-16 (D-03).

    Bytes UTF-16-BE comparam como sequências de unidades de 16 bits; a ordem de
    código do Python diverge dela fora do plano multilíngue básico.
    """
    return texto.lower().encode("utf-16-be")


def tem_letra(texto: str) -> bool:
    return _LETRA.search(texto) is not None


def _dobrar(texto: str) -> str:
    """Comparação «alfabética» de D-07: sem diacríticos e sem caixa."""
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c)).lower()


def _ordem_na_pagina(chave: str, lema: str, frequentes: Collection[str]) -> tuple:
    """RN-04: lemas coincidentes primeiro (grafia exata à frente, D-05/D-06);
    depois vocabulário frequente; desempate alfabético (D-07) e pela grafia."""
    if chave_readest(lema) == chave:
        return (0, 0 if lema == chave else 1, _dobrar(lema), lema)
    return (1, 0 if lema in frequentes else 1, _dobrar(lema), lema)


def _grafia_de_forma(chave: str, grafias: set[str]) -> str:
    return chave if chave in grafias else min(grafias)


def agrupar(
    headwords: Iterable[str],
    mapa: Mapping[str, Sequence[str]],
    frequentes: Collection[str],
) -> tuple[PlanoPaginas, RelatorioAgrupamento]:
    """Decide a página de cada chave pesquisável (D-02 a D-09).

    headwords: lemas do banco; mapa: lema → formas (saída de `construir_mapa`);
    frequentes: lemas de vocabulário frequente (`lemas_frequentes()`).
    """
    lemas_por_chave: dict[str, set[str]] = defaultdict(set)
    chaves_de_lema: set[str] = set()
    for lema in headwords:
        chave = chave_readest(lema)
        lemas_por_chave[chave].add(lema)
        chaves_de_lema.add(chave)

    grafias_de_forma: dict[str, set[str]] = defaultdict(set)
    descartadas: list[dict[str, str]] = []
    for lema, formas in mapa.items():
        for forma in formas:
            if not tem_letra(forma):  # RN-06: lemas nunca são descartados
                descartadas.append({"forma": forma, "lema": lema})
                continue
            chave = chave_readest(forma)
            lemas_por_chave[chave].add(lema)
            grafias_de_forma[chave].add(forma)

    sequencias = {
        chave: tuple(
            sorted(lemas, key=lambda lema: _ordem_na_pagina(chave, lema, frequentes))
        )
        for chave, lemas in lemas_por_chave.items()
    }

    paginas: list[PaginaReadest] = []
    for chave in sorted(sequencias, key=ordem_readest):
        lemas = sequencias[chave]
        if chave in chaves_de_lema:
            destino, grafia = "idx-lema", lemas[0]
        else:
            grafia = _grafia_de_forma(chave, grafias_de_forma[chave])
            if len(lemas) > 1:
                destino = "idx-forma-combinada"
            elif len(sequencias[chave_readest(lemas[0])]) > 1:
                destino = "idx-forma-direta"  # RN-03: só o artigo, dentro da página do lema
            else:
                destino = "syn"
        paginas.append(PaginaReadest(chave, grafia, lemas, destino))

    por_destino = Counter(p.destino for p in paginas)
    combinadas = [p for p in paginas if p.combinada]
    relatorio = RelatorioAgrupamento(
        chaves=len(paginas),
        paginas_simples=len(paginas) - len(combinadas),
        paginas_combinadas=len(combinadas),
        sequencias_distintas=len({p.lemas for p in combinadas}),
        descartes_sem_letra=len(descartadas),
        formas_descartadas=sorted(descartadas, key=lambda d: (d["forma"], d["lema"])),
        artigos_por_pagina=dict(Counter(len(p.lemas) for p in paginas)),
        indice={
            "idx": len(paginas) - por_destino["syn"],
            "syn": por_destino["syn"],
            "idx_lemas": por_destino["idx-lema"],
            "idx_formas_combinadas": por_destino["idx-forma-combinada"],
            "idx_formas_diretas": por_destino["idx-forma-direta"],
        },
    )
    assert relatorio.chaves == relatorio.indice["idx"] + relatorio.indice["syn"], (
        f"invariante violada: {relatorio.chaves} != {relatorio.indice}"
    )
    return PlanoPaginas(paginas), relatorio
