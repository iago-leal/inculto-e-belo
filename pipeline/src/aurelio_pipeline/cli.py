"""CLI única do pipeline (RF-07 das features 002 e 003): ingestão → índice → alvos.

Rodar build e validação no mesmo processo elimina por construção a dessincronia
banco↔artefato (EC-06 da spec de paridade). Ingestão e índice de flexões rodam
uma vez por execução e alimentam os alvos pedidos em `--alvo`: o KOReader
(padrão, comportamento da feature 002) e o Readest (feature 003), este com gate
de duas etapas e promoção condicionada (D-15). Exceções nomeadas viram mensagem
e exit code 2; reprovação de qualquer alvo, exit code 3 (RN-04 da 002, RN-07 da 003).
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from aurelio_pipeline.dominio.agrupamento_readest import agrupar
from aurelio_pipeline.dominio.indice_flexoes import construir_mapa
from aurelio_pipeline.dominio.renderizacao import renderizar_artigo
from aurelio_pipeline.erros import ErroPipeline, ManifestoAusenteError
from aurelio_pipeline.infra.conferencia_readest import ConferenciaReadest
from aurelio_pipeline.infra.escrita_readest import (
    BASENAME as BASENAME_READEST,
    EscritorReadest,
    descartar,
    promover,
    reprovar,
)
from aurelio_pipeline.infra.escrita_stardict import EscritorStarDict
from aurelio_pipeline.infra.repositorio import RepositorioAurelio
from aurelio_pipeline.validacao.leitor_stardict import LeitorStarDict
from aurelio_pipeline.validacao.paridade import executar_paridade, gravar_relatorio
from aurelio_pipeline.validacao.paridade_readest import executar_validacao_readest

log = logging.getLogger("aurelio.cli")

PIPELINE_DIR = Path(__file__).resolve().parents[2]
RAIZ_REPO = PIPELINE_DIR.parent
DB_PADRAO = RAIZ_REPO / "aurelio_normalized.db"
MANIFESTO_PADRAO = PIPELINE_DIR / "manifesto-integridade.json"
DIST_PADRAO = RAIZ_REPO / "dist"
BASENAME = "aurelio-stardict"
ALVOS = {
    "koreader": ("koreader",),
    "readest": ("readest",),
    "ambos": ("koreader", "readest"),
}


def _artigos_com_formas(repositorio, mapa, advertir, artigos=None):
    if artigos is not None:  # já renderizados para o Readest: mesma ordem de artigos()
        for lemma, html in artigos.items():
            yield lemma, html, mapa.get(lemma, [])
        return
    for lemma, verbetes in repositorio.artigos():
        yield (
            lemma,
            renderizar_artigo(lemma, verbetes, advertir=advertir),
            mapa.get(lemma, []),
        )


def _data_referencia(manifesto: Path) -> str:
    """Data do banco no manifesto: estável enquanto o banco não muda (D-11 da 003)."""
    try:
        return str(json.loads(manifesto.read_text(encoding="utf-8"))["gerado_em"])
    except (OSError, ValueError, KeyError) as exc:
        raise ManifestoAusenteError(
            f"manifesto sem data de referência (gerado_em) em {manifesto}: {exc}"
        ) from exc


def _gravar_json(dados: dict, caminho: Path) -> None:
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def _alvo_koreader(repositorio, mapa, relatorio_cobertura, headwords, dist, artigos) -> int:
    inicio = time.monotonic()
    log.info("etapa=conversao alvo=koreader dist=%s", dist)
    escritor = EscritorStarDict(dist, basename=BASENAME)
    resultado = escritor.escrever(
        _artigos_com_formas(repositorio, mapa, advertir=log.warning, artigos=artigos),
        data=time.strftime("%Y-%m-%d"),
    )

    destino = dist / BASENAME
    _gravar_json(relatorio_cobertura.to_dict(), destino / "relatorio-cobertura.json")

    log.info("etapa=paridade alvo=koreader artefato=%s", destino)
    relatorio_paridade = executar_paridade(
        LeitorStarDict(destino),
        headwords_esperados=headwords,
        syn_esperado=relatorio_cobertura.gravadas,
        mapa=mapa,
        textos_definicoes=repositorio.textos_definicoes,
    )
    caminho_relatorio = destino / "parity-report.json"
    gravar_relatorio(relatorio_paridade, caminho_relatorio)

    log.info(
        "alvo_fim alvo=koreader veredito=%s headwords=%d sinonimos=%d duracao_s=%.1f relatorio=%s",
        relatorio_paridade.veredito,
        resultado.headwords,
        resultado.sinonimos,
        time.monotonic() - inicio,
        caminho_relatorio,
    )
    if relatorio_paridade.veredito != "aprovado":
        log.error(
            "ARTEFATO DO KOREADER REPROVADO — não instale; divergências em %s",
            caminho_relatorio,
        )
        return 3
    return 0


def _alvo_readest(
    repositorio, mapa, headwords, dist, artigos, conferencia, manifesto
) -> int:
    inicio = time.monotonic()
    frequentes = repositorio.lemas_frequentes()
    log.info("etapa=agrupamento alvo=readest lemas_frequentes=%d", len(frequentes))
    plano, relatorio_agrupamento = agrupar(headwords, mapa, frequentes)
    log.info(
        "agrupamento_ok chaves=%d paginas_combinadas=%d sequencias_distintas=%d "
        "descartes_sem_letra=%d idx=%d syn=%d",
        relatorio_agrupamento.chaves,
        relatorio_agrupamento.paginas_combinadas,
        relatorio_agrupamento.sequencias_distintas,
        relatorio_agrupamento.descartes_sem_letra,
        relatorio_agrupamento.indice["idx"],
        relatorio_agrupamento.indice["syn"],
    )

    data = _data_referencia(manifesto)
    log.info("etapa=conversao alvo=readest dist=%s data=%s", dist, data)
    resultado = EscritorReadest(dist).escrever(plano, artigos, data=data)
    try:
        relatorios = resultado.preparo / "relatorios"
        relatorios.mkdir()
        _gravar_json(relatorio_agrupamento.to_dict(), relatorios / "relatorio-agrupamento.json")

        log.info("etapa=validacao alvo=readest artefato=%s", resultado.artefato)
        validacao = executar_validacao_readest(
            resultado.artefato,
            headwords=headwords,
            mapa=mapa,
            frequentes=frequentes,
            textos_definicoes=repositorio.textos_definicoes,
            data=data,
        )
        gravar_relatorio(validacao, relatorios / "validacao-readest.json")

        log.info("etapa=conferencia alvo=readest readest=%s", conferencia.fonte["tag"])
        conferido = conferencia.conferir(
            resultado.artefato, BASENAME_READEST, resultado.expectativa
        )
        _gravar_json(conferido, relatorios / "conferencia-readest.json")
    except BaseException:
        descartar(resultado)
        raise

    aprovado = validacao.veredito == "aprovado" and conferido["veredito"] == "aprovado"
    destino = promover(resultado, dist) if aprovado else reprovar(resultado, dist)
    log.info(
        "alvo_fim alvo=readest validacao=%s conferencia=%s chaves=%d idx=%d syn=%d "
        "paginas_combinadas=%d descartes_sem_letra=%d conteudo=%s duracao_s=%.1f "
        "artefato=%s relatorios=%s",
        validacao.veredito,
        conferido["veredito"],
        relatorio_agrupamento.chaves,
        resultado.idx,
        resultado.syn,
        relatorio_agrupamento.paginas_combinadas,
        relatorio_agrupamento.descartes_sem_letra,
        resultado.impressao_digital,
        time.monotonic() - inicio,
        destino / BASENAME_READEST,
        destino / "relatorios",
    )
    if not aprovado:
        log.error(
            "ARTEFATO DO READEST REPROVADO — não importe; a versão aprovada anterior "
            "segue em %s; diagnóstico em %s",
            dist / "readest",
            destino / "relatorios",
        )
        return 3
    return 0


def executar(
    db: Path, manifesto: Path, dist: Path, cobertura: str, alvo: str = "koreader"
) -> int:
    inicio = time.monotonic()
    alvos = ALVOS[alvo]

    conferencia = None
    if "readest" in alvos:
        # D-14: ambiente da conferência verificado antes de gastar o build
        log.info("etapa=pre-verificacao alvo=readest")
        conferencia = ConferenciaReadest()
        conferencia.preparar()

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

    artigos = None
    if "readest" in alvos:
        # D-18: acesso aleatório aos artigos pelo leiaute de páginas do Readest
        log.info("etapa=renderizacao em_memoria=sim")
        artigos = {
            lemma: renderizar_artigo(lemma, verbetes, advertir=log.warning)
            for lemma, verbetes in repositorio.artigos()
        }

    codigos = []
    try:
        if "koreader" in alvos:
            codigos.append(
                _alvo_koreader(
                    repositorio, mapa, relatorio_cobertura, headwords, dist, artigos
                )
            )
        if "readest" in alvos:
            codigos.append(
                _alvo_readest(
                    repositorio, mapa, headwords, dist, artigos, conferencia, manifesto
                )
            )
    finally:
        repositorio.close()

    codigo = max(codigos)
    log.info(
        "pipeline_fim alvo=%s exit=%d duracao_s=%.1f",
        alvo,
        codigo,
        time.monotonic() - inicio,
    )
    return codigo


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    parser = argparse.ArgumentParser(
        prog="aurelio-pipeline",
        description="Gera e valida o dicionário StarDict do Aurélio para o KOReader e o Readest.",
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
    parser.add_argument(
        "--alvo",
        choices=sorted(ALVOS),
        default="koreader",
        help="leitor de destino: koreader (padrão), readest ou ambos",
    )
    args = parser.parse_args()
    try:
        sys.exit(executar(args.db, args.manifesto, args.dist, args.cobertura, args.alvo))
    except ErroPipeline as exc:
        log.error("%s: %s", type(exc).__name__, exc)
        sys.exit(2)


if __name__ == "__main__":
    main()
