"""Mapeamento forma flexionada → headword (spec indice-de-flexoes; domínio puro).

Recebe pares brutos das tabelas de origem e o conjunto de headwords válidos;
devolve o mapa que materializa o .syn e o relatório auditável de descartes.
Sem I/O: a leitura vem da ingestão, a gravação do relatório fica na borda.
"""

import re
from collections.abc import Callable, Collection, Iterable, Mapping

from aurelio_pipeline.dominio.modelos import RelatorioCobertura
from aurelio_pipeline.erros import FormaAnomalaError

# RB-14: múltiplas formas numa linha de flexions.flexion, separadas por "," ou " ou "
SEPARADORES = re.compile(r",| ou ")

INTERVALO_PROGRESSO = 100_000


def dividir_formas(bruta: str | None, tabela: str, rowid: int) -> list[str]:
    """Valida (EC-04: falha barulhenta com o id) e divide (RB-14) o campo de forma."""
    if bruta is None or not bruta.strip():
        raise FormaAnomalaError(f"forma vazia ou só espaços em {tabela}.id={rowid}")
    partes = [parte.strip() for parte in SEPARADORES.split(bruta)]
    if any(not parte for parte in partes):
        raise FormaAnomalaError(
            f"fragmento vazio após split RB-14 em {tabela}.id={rowid}: {bruta!r}"
        )
    return partes


def construir_mapa(
    fontes: Mapping[str, Iterable[tuple[int, str, str]]],
    headwords: Collection[str],
    progresso: Callable[[int], None] | None = None,
) -> tuple[dict[str, list[str]], RelatorioCobertura]:
    """Constrói o mapa headword → formas com descartes classificados (RF-03).

    fontes: nome da tabela → iterável de (id, head, forma_bruta).
    Descartes: 'orfa' (head fora de headwords), 'identica' (forma == head,
    comparação exata sensível a diacríticos, EC-06) e 'duplicada' (par repetido).
    Invariante: Σ entrada_formas == gravadas + Σ descartes.
    """
    mapa: dict[str, set[str]] = {}
    vistos: set[tuple[str, str]] = set()
    entrada_linhas = {tabela: 0 for tabela in fontes}
    entrada_formas = {tabela: 0 for tabela in fontes}
    descartes = {"orfa": 0, "duplicada": 0, "identica": 0}
    orfas: set[str] = set()
    conjunto_headwords = (
        headwords if isinstance(headwords, (set, frozenset, dict)) else set(headwords)
    )
    processadas = 0

    for tabela, pares in fontes.items():
        for rowid, head, forma_bruta in pares:
            entrada_linhas[tabela] += 1
            for forma in dividir_formas(forma_bruta, tabela, rowid):
                entrada_formas[tabela] += 1
                processadas += 1
                if progresso and processadas % INTERVALO_PROGRESSO == 0:
                    progresso(processadas)
                if head not in conjunto_headwords:
                    descartes["orfa"] += 1
                    orfas.add(head)
                    continue
                if forma == head:
                    descartes["identica"] += 1
                    continue
                if (forma, head) in vistos:
                    descartes["duplicada"] += 1
                    continue
                vistos.add((forma, head))
                mapa.setdefault(head, set()).add(forma)

    gravadas = len(vistos)
    total_entrada = sum(entrada_formas.values())
    assert total_entrada == gravadas + sum(descartes.values()), (
        f"invariante violada: {total_entrada} != {gravadas} + {descartes}"
    )
    relatorio = RelatorioCobertura(
        entrada_linhas=entrada_linhas,
        entrada_formas=entrada_formas,
        gravadas=gravadas,
        descartes=descartes,
        orfas=sorted(orfas),
        headwords_com_formas=len(mapa),
    )
    return {head: sorted(formas) for head, formas in sorted(mapa.items())}, relatorio
