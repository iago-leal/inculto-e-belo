"""Testes da validação independente do alvo Readest (T008; RF-05, D-12).

O artefato correto sai do escritor real; cada defeito é fabricado alterando o
plano entregue ao escritor ou os bytes gravados, e precisa reprovar com a
divergência nominal do check correspondente.
"""

import dataclasses
import gzip
import html
import struct
import subprocess
import sys
import unicodedata

import pytest

from aurelio_pipeline.dominio.agrupamento_readest import agrupar, ordem_readest
from aurelio_pipeline.dominio.modelos import PlanoPaginas
from aurelio_pipeline.infra.escrita_readest import BASENAME, EscritorReadest
from aurelio_pipeline.validacao.paridade_readest import executar_validacao_readest

HEADWORDS = [
    "era", "ser", "erar", "ir", "fossar", "vir", "ver", "a", "A", "bretão",
    "à", "cantar", "&",
]
MAPA = {
    "ser": ["era", "foi", "fosse", "é", "fora"],
    "erar": ["era"],
    "ir": ["foi", "fosse", "vá", "fora"],
    "fossar": ["fosse"],
    "vir": ["vieram"],
    "ver": ["vir", "viram"],
    "bretão": ["a"],
    "A": ["As"],
    "cantar": ["cantávamos"],
}
FREQUENTES = frozenset({"ser", "ir", "ver"})
DATA = "2026-07-03"


def _esc(texto):
    return html.escape(texto, quote=False)


ARTIGOS = {lema: f"<b>{_esc(lema)}</b><p>definição de {_esc(lema)}</p>" for lema in HEADWORDS}


def _textos(lema):
    return [f"definição de {lema}"]


def _plano():
    plano, _ = agrupar(HEADWORDS, MAPA, FREQUENTES)
    return plano


def _escrever(tmp_path, plano=None):
    plano = plano or _plano()
    return EscritorReadest(tmp_path / "dist").escrever(plano, ARTIGOS, data=DATA).artefato


def _validar(diretorio, **kwargs):
    parametros = dict(
        headwords=HEADWORDS,
        mapa=MAPA,
        frequentes=FREQUENTES,
        textos_definicoes=_textos,
        data=DATA,
        gerado_em="2026-10-15T00:00:00Z",
    )
    parametros.update(kwargs)
    return executar_validacao_readest(diretorio, **parametros)


def _checks(relatorio):
    return {d["check"] for d in relatorio.divergencias}


def _trocar_pagina(plano, chave, lemas):
    return PlanoPaginas(
        [
            dataclasses.replace(p, lemas=lemas) if p.chave == chave else p
            for p in plano.paginas
        ]
    )


def _registros(dados, largura):
    pos, saida = 0, []
    while pos < len(dados):
        fim = dados.index(b"\0", pos)
        saida.append((dados[pos:fim], dados[fim + 1 : fim + 1 + largura]))
        pos = fim + 1 + largura
    return saida


def _gravar_registros(registros):
    return b"".join(palavra + b"\0" + extra for palavra, extra in registros)


class TestAprovacao:
    def test_artefato_correto_aprova(self, tmp_path):
        relatorio = _validar(_escrever(tmp_path))
        assert relatorio.veredito == "aprovado", relatorio.divergencias
        assert relatorio.divergencias == []
        assert relatorio.contagens["chaves_esperadas"] == len(_plano().paginas)
        assert relatorio.contagens["paginas_ok"] == relatorio.contagens["chaves_esperadas"]
        assert relatorio.amostras["conteudo_ok"] == len(HEADWORDS)

    def test_relatorio_reproduzivel(self, tmp_path):
        diretorio = _escrever(tmp_path)
        assert _validar(diretorio).to_dict() == _validar(diretorio).to_dict()


class TestPaginas:
    @pytest.mark.parametrize(
        ("lemas", "trecho"),
        [
            (("ir",), "faltam=['ser']"),
            (("ir", "ser", "vir"), "sobram=['vir']"),
            (("ser", "ir"), "ordem"),
        ],
    )
    def test_pagina_divergente_reprova_com_a_chave(self, tmp_path, lemas, trecho):
        plano = _trocar_pagina(_plano(), "foi", lemas)
        relatorio = _validar(_escrever(tmp_path, plano))
        assert relatorio.veredito == "reprovado"
        detalhes = [d["detalhe"] for d in relatorio.divergencias if d["check"] == "pagina-artigos"]
        assert any("chave=foi" in d and trecho in d for d in detalhes), detalhes

    def test_acesso_isolado_com_copia_reprova(self, tmp_path):
        diretorio = _escrever(tmp_path)
        idx_path = diretorio / f"{BASENAME}.idx"
        dz_path = diretorio / f"{BASENAME}.dict.dz"
        corpo = gzip.decompress(dz_path.read_bytes())
        copia = ARTIGOS["vir"].encode("utf-8")
        registros = _registros(idx_path.read_bytes(), 8)
        registros = [
            (p, struct.pack(">II", len(corpo), len(copia)) if p == b"vieram" else e)
            for p, e in registros
        ]
        idx_path.write_bytes(_gravar_registros(registros))
        dz_path.write_bytes(gzip.compress(corpo + copia))
        relatorio = _validar(diretorio)
        assert "acesso-isolado-sem-copia" in _checks(relatorio)
        assert any(
            "chave=vieram" in d["detalhe"]
            for d in relatorio.divergencias
            if d["check"] == "acesso-isolado-sem-copia"
        )


class TestIndices:
    def test_chave_fora_de_ordem(self, tmp_path):
        diretorio = _escrever(tmp_path)
        idx_path = diretorio / f"{BASENAME}.idx"
        registros = _registros(idx_path.read_bytes(), 8)
        registros[0], registros[1] = registros[1], registros[0]
        idx_path.write_bytes(_gravar_registros(registros))
        assert "ordem-idx" in _checks(_validar(diretorio))

    def test_chave_repetida_entre_idx_e_syn(self, tmp_path):
        diretorio = _escrever(tmp_path)
        syn_path = diretorio / f"{BASENAME}.syn"
        registros = _registros(syn_path.read_bytes(), 4)
        registros.append((b"foi", struct.pack(">I", 0)))
        registros.sort(key=lambda r: ordem_readest(r[0].decode("utf-8")))
        syn_path.write_bytes(_gravar_registros(registros))
        relatorio = _validar(diretorio)
        assert "unicidade-cruzada" in _checks(relatorio)

    def test_chave_fora_de_nfc(self, tmp_path):
        plano = _plano()
        nfd = unicodedata.normalize("NFD", "à")
        plano = PlanoPaginas(
            [
                dataclasses.replace(p, grafia=nfd) if p.chave == "à" else p
                for p in plano.paginas
            ]
        )
        relatorio = _validar(_escrever(tmp_path, plano))
        assert "nfc" in _checks(relatorio)


class TestMetadados:
    def test_wordcount_divergente(self, tmp_path):
        diretorio = _escrever(tmp_path)
        ifo = diretorio / f"{BASENAME}.ifo"
        linhas = [
            f"wordcount={int(linha.split('=')[1]) + 1}" if linha.startswith("wordcount=") else linha
            for linha in ifo.read_text(encoding="utf-8").splitlines()
        ]
        ifo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        relatorio = _validar(diretorio)
        assert any(
            d["check"] == "metadados-ifo" and "wordcount" in d["detalhe"]
            for d in relatorio.divergencias
        )

    def test_data_divergente(self, tmp_path):
        relatorio = _validar(_escrever(tmp_path), data="2030-01-01")
        assert "metadados-ifo" in _checks(relatorio)


class TestAmostra:
    def test_definicao_ausente_reprova(self, tmp_path):
        def textos(lema):
            return ["texto que não está no artigo"] if lema == "cantar" else _textos(lema)

        relatorio = _validar(_escrever(tmp_path), textos_definicoes=textos)
        assert relatorio.veredito == "reprovado"
        assert any(
            d["check"] == "amostra-conteudo" and "lema=cantar" in d["detalhe"]
            for d in relatorio.divergencias
        )


def test_validacao_nao_importa_agrupamento_nem_pyglossary():
    codigo = (
        "import sys; "
        "import aurelio_pipeline.validacao.paridade_readest; "
        "proibidos = [m for m in sys.modules "
        "if m.split('.')[0] == 'pyglossary' or m.endswith('agrupamento_readest') "
        "or m.endswith('escrita_readest')]; "
        "assert not proibidos, proibidos"
    )
    resultado = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True)
    assert resultado.returncode == 0, resultado.stderr
