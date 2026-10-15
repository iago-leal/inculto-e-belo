"""Escritor StarDict próprio do alvo Readest (D-01; stdlib + python-idzip) e promoção condicionada.

O PyGlossary grava um corpo por entrada e ordena pelo critério canônico do
formato; o Readest precisa de índices na ordem do `cmpAscii` (D-03) e de
entradas que apontam para um trecho de página já gravada (D-08). Daí este
escritor, que recebe o plano do agrupamento e os artigos já renderizados.

O artefato nasce num diretório de preparo dentro de `dist/` e só sobe para
`dist/readest/` quando a validação e a conferência aprovam (D-15, D-16).
"""

import hashlib
import io
import logging
import os
import shutil
import struct
import tempfile
import time
from collections.abc import Mapping
from pathlib import Path

from aurelio_pipeline.dominio.agrupamento_readest import chave_readest
from aurelio_pipeline.dominio.modelos import PlanoPaginas, ResultadoEscritaReadest
from aurelio_pipeline.erros import FalhaGeracaoError

log = logging.getLogger("aurelio.escrita_readest")

BASENAME = "aurelio-readest"
BOOKNAME = "Aurélio (uso pessoal, Readest)"
DESCRICAO_PADRAO = (
    "Aurélio completo, uma página por palavra com todos os verbetes correspondentes. "
    "Conteúdo sob direitos autorais, uso estritamente pessoal (RN-08)."
)
DIVISOR = b"<hr>"  # D-10: ausente do renderizador e do HTML do banco (RB-03)
PREFIXO_PREPARO = ".readest-preparo-"
NOME_EXPECTATIVA = "expectativa-conferencia.tsv"
DESTINO_APROVADO = "readest"
DESTINO_REPROVADO = "readest.reprovado"
MTIME_FIXO = 0  # cabeçalho gzip sem data de build (RN-09)


class EscritorReadest:
    def __init__(
        self,
        dist_dir: Path,
        basename: str = BASENAME,
        bookname: str = BOOKNAME,
        descricao: str = DESCRICAO_PADRAO,
    ):
        self._dist_dir = Path(dist_dir)
        self._basename = basename
        self._bookname = bookname
        self._descricao = descricao

    def escrever(
        self, plano: PlanoPaginas, artigos: Mapping[str, str], data: str
    ) -> ResultadoEscritaReadest:
        """Grava o artefato e a expectativa da conferência num diretório de preparo novo."""
        inicio = time.monotonic()
        self._conferir_entrada(plano, artigos)
        self._dist_dir.mkdir(parents=True, exist_ok=True)
        preparo = Path(tempfile.mkdtemp(prefix=PREFIXO_PREPARO, dir=self._dist_dir))
        try:
            os.chmod(preparo, 0o755)
            resultado = self._gravar(plano, artigos, data, preparo)
        except BaseException:
            shutil.rmtree(preparo, ignore_errors=True)
            raise
        resultado.duracao_s = round(time.monotonic() - inicio, 1)
        log.info(
            "escrita_readest_ok idx=%d syn=%d trechos=%d bytes_corpo=%d conteudo=%s "
            "duracao_s=%.1f %s",
            resultado.idx,
            resultado.syn,
            resultado.trechos,
            resultado.bytes_corpo,
            resultado.impressao_digital,
            resultado.duracao_s,
            " ".join(f"bytes_{nome}={tam}" for nome, tam in resultado.arquivos.items()),
        )
        return resultado

    @staticmethod
    def _conferir_entrada(plano: PlanoPaginas, artigos: Mapping[str, str]) -> None:
        proibidas = [p.grafia for p in plano.paginas if any(c in p.grafia for c in "\t\n\r\0")]
        if proibidas:
            raise FalhaGeracaoError(
                f"grafia com tabulação, quebra de linha ou NUL não cabe no índice nem na "
                f"expectativa: {proibidas[:5]!r}"
            )
        sem_artigo = sorted({lema for p in plano.paginas for lema in p.lemas} - artigos.keys())
        if sem_artigo:
            raise FalhaGeracaoError(
                f"{len(sem_artigo)} lema(s) do plano sem artigo renderizado: {sem_artigo[:5]}"
            )

    def _gravar(
        self, plano: PlanoPaginas, artigos: Mapping[str, str], data: str, preparo: Path
    ) -> ResultadoEscritaReadest:
        corpo = bytearray()
        trechos: dict[tuple[str, ...], tuple[int, int]] = {}
        artigo_na_pagina: dict[str, tuple[int, int]] = {}

        def gravar_pagina(lemas: tuple[str, ...], chave_de_lema: str | None) -> None:
            inicio = len(corpo)
            for i, lema in enumerate(lemas):
                if i:
                    corpo.extend(DIVISOR)
                dados = artigos[lema].encode("utf-8")
                if chave_de_lema is not None and chave_readest(lema) == chave_de_lema:
                    artigo_na_pagina[lema] = (len(corpo), len(dados))
                corpo.extend(dados)
            trechos[lemas] = (inicio, len(corpo) - inicio)

        # D-08: páginas de lema em ordem de índice, depois as demais combinadas, uma vez cada
        for pagina in plano.paginas:
            if pagina.destino == "idx-lema":
                gravar_pagina(pagina.lemas, pagina.chave)
        for pagina in plano.paginas:
            if pagina.destino == "idx-forma-combinada" and pagina.lemas not in trechos:
                gravar_pagina(pagina.lemas, None)

        idx_paginas = plano.do_idx()
        entradas_idx: list[tuple[str, int, int]] = []
        posicao_no_idx: dict[str, int] = {}
        for i, pagina in enumerate(idx_paginas):
            if pagina.destino == "idx-forma-direta":
                offset, tamanho = artigo_na_pagina[pagina.lemas[0]]
            else:
                offset, tamanho = trechos[pagina.lemas]
            entradas_idx.append((pagina.grafia, offset, tamanho))
            posicao_no_idx[pagina.chave] = i

        entradas_syn: list[tuple[str, int]] = []
        for pagina in plano.do_syn():
            destino = posicao_no_idx[chave_readest(pagina.lemas[0])]
            if idx_paginas[destino].lemas != pagina.lemas:
                raise FalhaGeracaoError(
                    f"forma do .syn apontaria para página com artigo alheio: "
                    f"{pagina.grafia} → {idx_paginas[destino].lemas}"
                )
            entradas_syn.append((pagina.grafia, destino))

        idx = b"".join(
            grafia.encode("utf-8") + b"\0" + struct.pack(">II", offset, tamanho)
            for grafia, offset, tamanho in entradas_idx
        )
        syn = b"".join(
            grafia.encode("utf-8") + b"\0" + struct.pack(">I", destino)
            for grafia, destino in entradas_syn
        )
        impressao = hashlib.sha256(idx + syn + corpo).hexdigest()[:16]

        artefato = preparo / self._basename
        artefato.mkdir()
        base = artefato / self._basename
        base.with_name(f"{self._basename}.idx").write_bytes(idx)
        base.with_name(f"{self._basename}.syn").write_bytes(syn)
        self._comprimir(bytes(corpo), base.with_name(f"{self._basename}.dict.dz"))
        base.with_name(f"{self._basename}.ifo").write_text(
            "StarDict's dict ifo file\n"
            "version=3.0.0\n"
            f"bookname={self._bookname}\n"
            f"wordcount={len(entradas_idx)}\n"
            f"synwordcount={len(entradas_syn)}\n"
            f"idxfilesize={len(idx)}\n"
            "sametypesequence=h\n"
            f"date={data}\n"
            f"description={self._descricao} Versão do conteúdo {impressao}\n",
            encoding="utf-8",
        )

        expectativa = preparo / NOME_EXPECTATIVA
        with expectativa.open("w", encoding="utf-8", newline="\n") as saida:
            for grafia, offset, tamanho in entradas_idx:
                saida.write(f"{grafia}\t{offset}\t{tamanho}\n")
            for grafia, destino in entradas_syn:
                _, offset, tamanho = entradas_idx[destino]
                saida.write(f"{grafia}\t{offset}\t{tamanho}\n")

        return ResultadoEscritaReadest(
            idx=len(entradas_idx),
            syn=len(entradas_syn),
            trechos=len(trechos),
            bytes_corpo=len(corpo),
            impressao_digital=impressao,
            preparo=preparo,
            artefato=artefato,
            expectativa=expectativa,
            duracao_s=0.0,
            arquivos={p.name: p.stat().st_size for p in sorted(artefato.iterdir())},
        )

    def _comprimir(self, corpo: bytes, destino: Path) -> None:
        try:
            from idzip import compressor
        except ImportError as exc:
            raise FalhaGeracaoError(
                f"python-idzip indisponível ({exc}) — rode `uv sync` em pipeline/"
            ) from exc
        try:
            with destino.open("wb") as saida:
                compressor.compress(
                    io.BytesIO(corpo),
                    len(corpo),
                    saida,
                    basename=f"{self._basename}.dict",
                    mtime=MTIME_FIXO,
                )
        except Exception as exc:  # noqa: BLE001 — reembalagem deliberada
            raise FalhaGeracaoError(f"falha na compressão dictzip: {exc}") from exc


# --- promoção condicionada (D-15) ---------------------------------------------


def _substituir(origem: Path, destino: Path) -> None:
    anterior = None
    if destino.exists():
        anterior = destino.with_name(f".readest-anterior-{os.getpid()}")
        os.rename(destino, anterior)
    os.rename(origem, destino)
    if anterior is not None:
        shutil.rmtree(anterior)


def promover(resultado: ResultadoEscritaReadest, dist_dir: Path) -> Path:
    """Aprovado nas duas etapas: a expectativa sai e o preparo vira `dist/readest/`."""
    destino = Path(dist_dir) / DESTINO_APROVADO
    resultado.expectativa.unlink(missing_ok=True)
    _substituir(resultado.preparo, destino)
    return destino


def reprovar(resultado: ResultadoEscritaReadest, dist_dir: Path) -> Path:
    """Reprovado: vai inteiro para `dist/readest.reprovado/`; a versão aprovada fica intacta."""
    destino = Path(dist_dir) / DESTINO_REPROVADO
    _substituir(resultado.preparo, destino)
    return destino


def descartar(resultado: ResultadoEscritaReadest) -> None:
    """Erro de ambiente ou de execução: nada é promovido nem guardado."""
    shutil.rmtree(resultado.preparo, ignore_errors=True)
