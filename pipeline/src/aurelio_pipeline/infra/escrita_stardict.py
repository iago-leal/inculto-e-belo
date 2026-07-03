"""Adaptador PyGlossary (spec conversao-formato §8): único ponto de acoplamento à biblioteca.

Formas flexionadas entram como chaves alternativas (l_word) e o PyGlossary
materializa o .syn (D-04). Escrita atômica: diretório temporário + rename,
substituindo a versão anterior sem retenção (requirements §9). A ausência do
python-idzip degradaria silenciosamente o .dict.dz — por isso a verificação
pós-build é obrigatória (D-05).
"""

import logging
import os
import shutil
import tempfile
import time
from collections.abc import Iterable, Sequence
from pathlib import Path

from aurelio_pipeline.dominio.modelos import ResultadoBuild
from aurelio_pipeline.erros import FalhaGeracaoError

log = logging.getLogger("aurelio.escrita")

INTERVALO_PROGRESSO = 10_000

DESCRICAO_PADRAO = (
    "Aurélio completo com índice de flexões. "
    "Conteúdo sob direitos autorais — uso estritamente pessoal (RN-05)."
)


class EscritorStarDict:
    def __init__(
        self,
        dist_dir: Path,
        basename: str = "aurelio-stardict",
        bookname: str = "Aurélio (uso pessoal)",
        descricao: str = DESCRICAO_PADRAO,
    ):
        self._dist_dir = Path(dist_dir)
        self._basename = basename
        self._bookname = bookname
        self._descricao = descricao

    def escrever(
        self,
        artigos: Iterable[tuple[str, str, Sequence[str]]],
        data: str,
    ) -> ResultadoBuild:
        """Grava o artefato a partir de (headword, html, formas). Retorna totais e tamanhos."""
        inicio = time.monotonic()
        try:
            from pyglossary.glossary_v2 import Glossary
        except ImportError as exc:
            raise FalhaGeracaoError(
                f"PyGlossary indisponível ({exc}) — rode `uv sync` em pipeline/"
            ) from exc

        Glossary.init()
        glossario = Glossary()
        glossario.setInfo("name", self._bookname)
        glossario.setInfo("bookname", self._bookname)
        glossario.setInfo("description", self._descricao)
        glossario.setInfo("date", data)

        headwords = 0
        sinonimos = 0
        for headword, html, formas in artigos:
            glossario.addEntry(
                glossario.newEntry([headword, *formas], html, defiFormat="h")
            )
            headwords += 1
            sinonimos += len(formas)
            if headwords % INTERVALO_PROGRESSO == 0:
                log.info("progresso verbetes_adicionados=%d", headwords)

        destino = self._dist_dir / self._basename
        self._dist_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=self._dist_dir) as tmp:
            alvo_tmp = Path(tmp) / self._basename
            alvo_tmp.mkdir()
            try:
                glossario.write(
                    str(alvo_tmp / f"{self._basename}.ifo"),
                    formatName="Stardict",
                    dictzip=True,
                    sametypesequence="h",
                )
            except Exception as exc:  # noqa: BLE001 — reembalagem deliberada (EC-03)
                raise FalhaGeracaoError(
                    f"falha do PyGlossary na escrita: {exc}"
                ) from exc

            faltantes = [
                sufixo
                for sufixo in (".ifo", ".idx", ".dict.dz", ".syn")
                if not (alvo_tmp / f"{self._basename}{sufixo}").exists()
            ]
            if faltantes:
                raise FalhaGeracaoError(
                    f"artefato incompleto após a escrita, faltam: {', '.join(faltantes)} — "
                    "se faltou .dict.dz, confira o python-idzip no ambiente (D-05)"
                )

            anterior = None
            if destino.exists():
                anterior = destino.with_name(
                    f".{self._basename}.anterior-{os.getpid()}"
                )
                os.rename(destino, anterior)
            os.rename(alvo_tmp, destino)
            if anterior is not None:
                shutil.rmtree(anterior)

        duracao = time.monotonic() - inicio
        arquivos = {p.name: p.stat().st_size for p in sorted(destino.iterdir())}
        log.info(
            "escrita_ok headwords=%d sinonimos=%d duracao_s=%.1f %s",
            headwords,
            sinonimos,
            duracao,
            " ".join(f"bytes_{nome}={tam}" for nome, tam in arquivos.items()),
        )
        return ResultadoBuild(
            headwords=headwords,
            sinonimos=sinonimos,
            duracao_s=round(duracao, 1),
            arquivos=arquivos,
        )
