"""Testes do leitor StarDict próprio e dos checks de paridade (T007; RF-06, D-07..D-09)."""

import gzip
import struct
import subprocess
import sys
from pathlib import Path

import pytest

from aurelio_pipeline.erros import ArtefatoAusenteError, ArtefatoCorrompidoError
from aurelio_pipeline.validacao.leitor_stardict import LeitorStarDict
from aurelio_pipeline.validacao.paridade import (
    executar_paridade,
    normalizar_texto,
    texto_de_html,
)

BASENAME = "teste"

ENTRADAS = [
    ("bela", "<b>bela</b> <ul><li>Mulher bela</li></ul>"),
    (
        "belo",
        "<b>belo</b> <ul><li>Que tem beleza</li><li>Agradável aos olhos</li></ul>",
    ),
]
SINONIMOS = [("belas", 0), ("belas", 1), ("belos", 1)]
MAPA = {"bela": ["belas"], "belo": ["belas", "belos"]}
TEXTOS = {
    "bela": ["Mulher bela"],
    "belo": ["Que tem beleza", "Agradável aos olhos"],
}


def _grava_artefato(
    diretorio: Path,
    entradas=None,
    sinonimos=None,
    wordcount=None,
    synwordcount=None,
    truncar_idx=False,
    estourar_offset=False,
) -> Path:
    entradas = ENTRADAS if entradas is None else entradas
    sinonimos = SINONIMOS if sinonimos is None else sinonimos
    diretorio.mkdir(parents=True, exist_ok=True)

    corpo = b""
    idx = b""
    for palavra, html in entradas:
        dados = html.encode("utf-8")
        tamanho = len(dados) + (10_000_000 if estourar_offset else 0)
        idx += palavra.encode("utf-8") + b"\0" + struct.pack(">II", len(corpo), tamanho)
        corpo += dados
    if truncar_idx:
        idx = idx[:-2]

    syn = b""
    for forma, indice in sinonimos:
        syn += forma.encode("utf-8") + b"\0" + struct.pack(">I", indice)

    (diretorio / f"{BASENAME}.idx").write_bytes(idx)
    (diretorio / f"{BASENAME}.syn").write_bytes(syn)
    (diretorio / f"{BASENAME}.dict.dz").write_bytes(gzip.compress(corpo))
    (diretorio / f"{BASENAME}.ifo").write_text(
        "StarDict's dict ifo file\n"
        "version=2.4.2\n"
        f"wordcount={len(entradas) if wordcount is None else wordcount}\n"
        f"synwordcount={len(sinonimos) if synwordcount is None else synwordcount}\n"
        f"idxfilesize={len(idx)}\n"
        "bookname=Artefato de teste\n"
        "sametypesequence=h\n",
        encoding="utf-8",
    )
    return diretorio


def _paridade(leitor, **kwargs):
    parametros = dict(
        headwords_esperados=["bela", "belo"],
        syn_esperado=3,
        mapa=MAPA,
        textos_definicoes=lambda lemma: TEXTOS[lemma],
        amostra=500,
        gerado_em="2026-07-03T00:00:00Z",
    )
    parametros.update(kwargs)
    return executar_paridade(leitor, **parametros)


class TestLeitor:
    def test_parse_ok(self, tmp_path):
        leitor = LeitorStarDict(_grava_artefato(tmp_path / "a"))
        assert leitor.headwords == ["bela", "belo"]
        assert leitor.sinonimos == SINONIMOS
        assert leitor.ifo["sametypesequence"] == "h"
        assert "Que tem beleza" in leitor.artigo(1)

    def test_arquivo_faltante(self, tmp_path):
        pasta = _grava_artefato(tmp_path / "a")
        (pasta / f"{BASENAME}.syn").unlink()
        with pytest.raises(ArtefatoAusenteError, match=r"\.syn"):
            LeitorStarDict(pasta)

    def test_idx_truncado(self, tmp_path):
        pasta = _grava_artefato(tmp_path / "a", truncar_idx=True)
        with pytest.raises(ArtefatoCorrompidoError, match=r"byte"):
            LeitorStarDict(pasta)

    def test_offset_fora_do_dict(self, tmp_path):
        pasta = _grava_artefato(tmp_path / "a", estourar_offset=True)
        with pytest.raises(ArtefatoCorrompidoError):
            LeitorStarDict(pasta)

    def test_syn_apontando_indice_inexistente(self, tmp_path):
        pasta = _grava_artefato(tmp_path / "a", sinonimos=[("belas", 7)])
        with pytest.raises(ArtefatoCorrompidoError):
            LeitorStarDict(pasta)


class TestNormalizacao:
    def test_normalizar_texto_colapsa_whitespace(self):
        assert normalizar_texto("a\n  b\t c ") == "a b c"

    def test_texto_de_html_remove_tags_e_entidades(self):
        assert texto_de_html("<ul><li><b>a&amp;b</b>\n c</li></ul>") == "a&b c"


class TestParidade:
    def test_aprovada(self, tmp_path):
        relatorio = _paridade(LeitorStarDict(_grava_artefato(tmp_path / "a")))
        assert relatorio.veredito == "aprovado"
        assert relatorio.divergencias == []
        assert relatorio.amostras == {"verbetes_ok": 2, "flexoes_ok": 3}

    def test_headword_a_menos_reprova(self, tmp_path):
        leitor = LeitorStarDict(_grava_artefato(tmp_path / "a"))
        relatorio = _paridade(leitor, headwords_esperados=["bela", "belo", "zebra"])
        assert relatorio.veredito == "reprovado"
        assert any("headword" in d["check"] for d in relatorio.divergencias)

    def test_syn_menor_que_esperado_reprova(self, tmp_path):
        relatorio = _paridade(
            LeitorStarDict(_grava_artefato(tmp_path / "a")), syn_esperado=4
        )
        assert relatorio.veredito == "reprovado"

    def test_wordcount_do_ifo_divergente_reprova(self, tmp_path):
        leitor = LeitorStarDict(_grava_artefato(tmp_path / "a", wordcount=99))
        relatorio = _paridade(leitor)
        assert relatorio.veredito == "reprovado"
        assert any("metadados" in d["check"] for d in relatorio.divergencias)

    def test_definicao_ausente_no_artigo_reprova(self, tmp_path):
        leitor = LeitorStarDict(_grava_artefato(tmp_path / "a"))
        textos = {"bela": ["Mulher bela"], "belo": ["Definição fantasma"]}
        relatorio = _paridade(leitor, textos_definicoes=lambda lemma: textos[lemma])
        assert relatorio.veredito == "reprovado"
        assert any("Definição fantasma" in d["detalhe"] for d in relatorio.divergencias)

    def test_syn_com_destino_errado_reprova(self, tmp_path):
        leitor = LeitorStarDict(_grava_artefato(tmp_path / "a"))
        relatorio = _paridade(leitor, mapa={"bela": ["belos"], "belo": ["belas"]})
        assert relatorio.veredito == "reprovado"
        assert any("belos" in d["detalhe"] for d in relatorio.divergencias)

    def test_relatorio_integral_sem_parada_precoce(self, tmp_path):
        leitor = LeitorStarDict(_grava_artefato(tmp_path / "a", wordcount=99))
        relatorio = _paridade(leitor, syn_esperado=4)
        assert len(relatorio.divergencias) >= 2

    def test_seeds_fixas_dao_relatorio_identico(self, tmp_path):
        leitor = LeitorStarDict(_grava_artefato(tmp_path / "a"))
        r1 = _paridade(leitor).to_dict()
        r2 = _paridade(leitor).to_dict()
        assert r1 == r2
        assert r1["seeds"] == r2["seeds"]


def test_validacao_nao_importa_pyglossary():
    codigo = (
        "import sys; "
        "import aurelio_pipeline.validacao.leitor_stardict, "
        "aurelio_pipeline.validacao.paridade; "
        "assert not any(m.split('.')[0] == 'pyglossary' for m in sys.modules), "
        "'pyglossary importado pela validacao'"
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo], capture_output=True, text=True
    )
    assert resultado.returncode == 0, resultado.stderr
