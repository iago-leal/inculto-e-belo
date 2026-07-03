"""CLI única do pipeline (RF-07): ingestão → índice → conversão → paridade numa execução.

Rodar build e validação no mesmo processo elimina por construção a dessincronia
banco↔artefato (EC-06 da spec de paridade). Exceções nomeadas viram mensagem e
exit code ≠ 0; a paridade reprovada também (RN-04: gate por construção).
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from aurelio_pipeline.dominio.indice_flexoes import construir_mapa
from aurelio_pipeline.dominio.renderizacao import renderizar_artigo
from aurelio_pipeline.erros import ErroPipeline
from aurelio_pipeline.infra.escrita_stardict import EscritorStarDict
from aurelio_pipeline.infra.repositorio import RepositorioAurelio
from aurelio_pipeline.validacao.leitor_stardict import LeitorStarDict
from aurelio_pipeline.validacao.paridade import executar_paridade, gravar_relatorio

log = logging.getLogger("aurelio.cli")

PIPELINE_DIR = Path(__file__).resolve().parents[2]
RAIZ_REPO = PIPELINE_DIR.parent
DB_PADRAO = RAIZ_REPO / "aurelio_normalized.db"
MANIFESTO_PADRAO = PIPELINE_DIR / "manifesto-integridade.json"
DIST_PADRAO = RAIZ_REPO / "dist"
BASENAME = "aurelio-stardict"


def _artigos_com_formas(repositorio, mapa, advertir):
    for lemma, verbetes in repositorio.artigos():
        yield (
            lemma,
            renderizar_artigo(lemma, verbetes, advertir=advertir),
            mapa.get(lemma, []),
        )


def executar(db: Path, manifesto: Path, dist: Path, cobertura: str) -> int:
    inicio = time.monotonic()
    repositorio = RepositorioAurelio(db, manifesto)

    log.info("etapa=ingestao db=%s manifesto=%s", db, manifesto)
    repositorio.validar()

    log.info("etapa=indice cobertura=%s", cobertura)
    fontes = {"flexions": repositorio.flexoes()}
    if cobertura == "total":
        fontes["conjugations"] = repositorio.conjugacoes()
    headwords = repositorio.headwords()
    mapa, relatorio_cobertura = construir_mapa(
        fontes,
        set(headwords),
        progresso=lambda n: log.info("progresso pares_processados=%d", n),
    )
    log.info(
        "indice_ok gravadas=%d orfas=%d descartes=%s",
        relatorio_cobertura.gravadas,
        len(relatorio_cobertura.orfas),
        relatorio_cobertura.descartes,
    )

    log.info("etapa=conversao dist=%s", dist)
    escritor = EscritorStarDict(dist, basename=BASENAME)
    resultado = escritor.escrever(
        _artigos_com_formas(repositorio, mapa, advertir=log.warning),
        data=time.strftime("%Y-%m-%d"),
    )

    destino = dist / BASENAME
    (destino / "relatorio-cobertura.json").write_text(
        json.dumps(relatorio_cobertura.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    log.info("etapa=paridade artefato=%s", destino)
    relatorio_paridade = executar_paridade(
        LeitorStarDict(destino),
        headwords_esperados=headwords,
        syn_esperado=relatorio_cobertura.gravadas,
        mapa=mapa,
        textos_definicoes=repositorio.textos_definicoes,
    )
    caminho_relatorio = destino / "parity-report.json"
    gravar_relatorio(relatorio_paridade, caminho_relatorio)
    repositorio.close()

    log.info(
        "pipeline_fim veredito=%s headwords=%d sinonimos=%d duracao_s=%.1f relatorio=%s",
        relatorio_paridade.veredito,
        resultado.headwords,
        resultado.sinonimos,
        time.monotonic() - inicio,
        caminho_relatorio,
    )
    if relatorio_paridade.veredito != "aprovado":
        log.error(
            "ARTEFATO REPROVADO — não instale; divergências em %s", caminho_relatorio
        )
        return 3
    return 0


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    parser = argparse.ArgumentParser(
        prog="aurelio-pipeline",
        description="Gera e valida o dicionário StarDict do Aurélio para o KOReader.",
    )
    parser.add_argument(
        "--db", type=Path, default=DB_PADRAO, help="caminho do aurelio_normalized.db"
    )
    parser.add_argument(
        "--manifesto",
        type=Path,
        default=MANIFESTO_PADRAO,
        help="manifesto de integridade",
    )
    parser.add_argument(
        "--dist", type=Path, default=DIST_PADRAO, help="diretório de saída"
    )
    parser.add_argument(
        "--cobertura",
        choices=["total", "flexions-somente"],
        default="total",
        help="'flexions-somente' corta as conjugações do .syn (1º fallback de RN-05 do spike)",
    )
    args = parser.parse_args()
    try:
        sys.exit(executar(args.db, args.manifesto, args.dist, args.cobertura))
    except ErroPipeline as exc:
        log.error("%s: %s", type(exc).__name__, exc)
        sys.exit(2)


if __name__ == "__main__":
    main()
