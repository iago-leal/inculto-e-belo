"""Leitor StarDict próprio em stdlib pura (RF-01 da spec validacao-paridade, D-07).

Independência do PyGlossary é o valor central do gate: este módulo não importa
nada além de gzip e struct. dictzip é gzip válido com campo extra, então o
módulo gzip descomprime o .dict.dz inteiro — para ~500 extrações por build,
fatiar o buffer por offset/size é mais simples que acesso randômico por chunks.
"""

import gzip
import struct
from pathlib import Path

from aurelio_pipeline.erros import ArtefatoAusenteError, ArtefatoCorrompidoError

SUFIXOS_OBRIGATORIOS = (".ifo", ".idx", ".syn", ".dict.dz")


def _registros(dados: bytes, largura_extra: int, arquivo: str):
    """Itera registros `string\\0` + `largura_extra` bytes, com checagem estrutural."""
    pos = 0
    while pos < len(dados):
        fim = dados.find(b"\0", pos)
        if fim == -1:
            raise ArtefatoCorrompidoError(
                f"{arquivo}: registro sem terminador NUL a partir do byte {pos}"
            )
        if fim + 1 + largura_extra > len(dados):
            raise ArtefatoCorrompidoError(
                f"{arquivo}: registro truncado no byte {fim + 1} "
                f"(esperados {largura_extra} bytes após a string)"
            )
        try:
            palavra = dados[pos:fim].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ArtefatoCorrompidoError(
                f"{arquivo}: string inválida em UTF-8 no byte {pos}: {exc}"
            ) from exc
        extra = dados[fim + 1 : fim + 1 + largura_extra]
        yield palavra, extra
        pos = fim + 1 + largura_extra


class LeitorStarDict:
    def __init__(self, diretorio: Path):
        diretorio = Path(diretorio)
        ifos = sorted(diretorio.glob("*.ifo"))
        if not ifos:
            raise ArtefatoAusenteError(
                f"nenhum .ifo em {diretorio} — rode o build antes"
            )
        basename = ifos[0].stem

        faltantes = [
            sufixo
            for sufixo in SUFIXOS_OBRIGATORIOS
            if not (diretorio / f"{basename}{sufixo}").exists()
        ]
        if faltantes:
            raise ArtefatoAusenteError(
                f"artefato incompleto em {diretorio}, faltam: "
                + ", ".join(f"{basename}{s}" for s in faltantes)
            )

        self.ifo = self._parse_ifo(diretorio / f"{basename}.ifo")

        dz = (diretorio / f"{basename}.dict.dz").read_bytes()
        try:
            self._dict = gzip.decompress(dz)
        except (gzip.BadGzipFile, EOFError, OSError) as exc:
            raise ArtefatoCorrompidoError(
                f"{basename}.dict.dz: falha de descompressão gzip/dictzip: {exc}"
            ) from exc

        idx_bytes = (diretorio / f"{basename}.idx").read_bytes()
        self.idx_bytes = len(idx_bytes)
        self.entradas: list[tuple[str, int, int]] = []
        for palavra, extra in _registros(idx_bytes, 8, f"{basename}.idx"):
            offset, tamanho = struct.unpack(">II", extra)
            if offset + tamanho > len(self._dict):
                raise ArtefatoCorrompidoError(
                    f"{basename}.idx: entrada '{palavra}' aponta além do .dict "
                    f"(offset={offset} size={tamanho} dict={len(self._dict)})"
                )
            self.entradas.append((palavra, offset, tamanho))

        syn_bytes = (diretorio / f"{basename}.syn").read_bytes()
        self.sinonimos: list[tuple[str, int]] = []
        for forma, extra in _registros(syn_bytes, 4, f"{basename}.syn"):
            (indice,) = struct.unpack(">I", extra)
            if indice >= len(self.entradas):
                raise ArtefatoCorrompidoError(
                    f"{basename}.syn: forma '{forma}' aponta ao índice {indice}, "
                    f"mas o .idx tem {len(self.entradas)} entradas"
                )
            self.sinonimos.append((forma, indice))

    @staticmethod
    def _parse_ifo(caminho: Path) -> dict[str, str]:
        ifo: dict[str, str] = {}
        for linha in caminho.read_text(encoding="utf-8").splitlines()[1:]:
            if "=" in linha:
                chave, valor = linha.split("=", 1)
                ifo[chave.strip()] = valor.strip()
        return ifo

    @property
    def headwords(self) -> list[str]:
        return [palavra for palavra, _, _ in self.entradas]

    def artigo(self, indice: int) -> str:
        _, offset, tamanho = self.entradas[indice]
        return self._dict[offset : offset + tamanho].decode("utf-8")
