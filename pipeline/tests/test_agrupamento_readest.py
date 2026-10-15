"""Testes do agrupamento do alvo Readest (T006; RF-02, RF-03, RF-04, D-02 a D-09).

Dados sintéticos (RN-08: nenhum conteúdo do Aurélio no repositório). Os casos
reproduzem a forma das páginas medidas no banco real: «era» (lema que é forma
de outros), «foi» (forma de dois lemas), «fosse» (frequente diante de raro),
«a»/«A» (colisão de caixa), «à» (inalcançável na ordem canônica), «/» (forma
sem letra de verbo defectivo) e «vieram» (forma de um só lema cujo lema abre
página combinada).
"""

import random

import pytest

from aurelio_pipeline.dominio.agrupamento_readest import (
    agrupar,
    chave_readest,
    ordem_readest,
    tem_letra,
)

HEADWORDS = [
    "era", "ser", "erar", "ir", "fossar", "boa", "bom", "boar", "vir", "ver",
    "a", "A", "bretão", "à", "cantar", "defectivo", "abacate", "zebra", "&",
]
MAPA = {
    "ser": ["era", "foi", "fosse", "é", "fora"],
    "erar": ["era"],
    "ir": ["foi", "fosse", "vá", "fora"],
    "fossar": ["fosse"],
    "bom": ["boa"],
    "boar": ["boa"],
    "vir": ["vieram"],
    "ver": ["vir", "viram"],
    "bretão": ["a"],
    "A": ["As"],
    "cantar": ["cantávamos"],
    "defectivo": ["/", "defectivas"],
    "abacate": ["xis"],
    "zebra": ["xis"],
}
FREQUENTES = frozenset({"ser", "ir", "bom", "ver", "zebra"})


@pytest.fixture(scope="module")
def resultado():
    return agrupar(HEADWORDS, MAPA, FREQUENTES)


def _paginas(plano):
    return {p.chave: p for p in plano.paginas}


class TestChave:
    def test_chave_e_minusculas(self):
        assert chave_readest("Foi") == "foi"
        assert chave_readest("Å") == "å"

    def test_ordem_por_unidades_utf16_e_nao_por_codigo(self):
        # U+1D49C (par substituto D835 DC9C) vem antes de U+FB00 em UTF-16,
        # ao contrário da ordem de código do Python — é a ordem do cmpAscii.
        assert ordem_readest("𝒜") < ordem_readest("ﬀ")
        assert "𝒜" > "ﬀ"

    def test_ordem_ignora_caixa(self):
        assert ordem_readest("Abacate") == ordem_readest("abacate")

    @pytest.mark.parametrize(
        ("texto", "esperado"),
        [("/", False), ("123", False), ("_-", False), ("à", True), ("a1", True)],
    )
    def test_tem_letra(self, texto, esperado):
        assert tem_letra(texto) is esperado


class TestPaginas:
    @pytest.mark.parametrize(
        ("chave", "lemas"),
        [
            ("era", ("era", "ser", "erar")),
            ("foi", ("ir", "ser")),
            ("fosse", ("ir", "ser", "fossar")),
            ("boa", ("boa", "bom", "boar")),
            ("vir", ("vir", "ver")),
            ("a", ("a", "A", "bretão")),
            ("à", ("à",)),
            ("vieram", ("vir",)),
            ("cantávamos", ("cantar",)),
            ("xis", ("zebra", "abacate")),
            ("&", ("&",)),
        ],
    )
    def test_artigos_e_ordem_da_pagina(self, resultado, chave, lemas):
        plano, _ = resultado
        assert _paginas(plano)[chave].lemas == lemas

    def test_lema_sem_chave_propria_por_colisao_de_caixa(self, resultado):
        plano, _ = resultado
        paginas = _paginas(plano)
        assert "A" not in {p.grafia for p in plano.paginas}
        assert paginas["a"].grafia == "a"
        assert paginas["as"].lemas == ("A",)

    def test_lema_so_maiusculo_grava_a_propria_grafia(self):
        plano, _ = agrupar(["Å", "ångström"], {}, frozenset())
        assert _paginas(plano)["å"].grafia == "Å"

    def test_grafia_da_forma_prefere_minusculas(self):
        plano, _ = agrupar(["ir", "ser"], {"ir": ["Foi"], "ser": ["foi"]}, frozenset())
        assert _paginas(plano)["foi"].grafia == "foi"
        plano, _ = agrupar(["ir"], {"ir": ["Foi"]}, frozenset())
        assert _paginas(plano)["foi"].grafia == "Foi"

    def test_formas_sem_letra_descartadas_e_lemas_mantidos(self, resultado):
        plano, relatorio = resultado
        chaves = {p.chave for p in plano.paginas}
        assert "/" not in chaves
        assert "&" in chaves
        assert relatorio.descartes_sem_letra == 1
        assert relatorio.formas_descartadas == [{"forma": "/", "lema": "defectivo"}]

    def test_cada_chave_aparece_uma_vez(self, resultado):
        plano, _ = resultado
        chaves = [p.chave for p in plano.paginas]
        assert len(chaves) == len(set(chaves))


class TestDestinos:
    @pytest.mark.parametrize(
        ("chave", "destino"),
        [
            ("era", "idx-lema"),
            ("vir", "idx-lema"),
            ("à", "idx-lema"),
            ("foi", "idx-forma-combinada"),
            ("xis", "idx-forma-combinada"),
            ("vieram", "idx-forma-direta"),
            ("as", "idx-forma-direta"),
            ("cantávamos", "syn"),
            ("viram", "syn"),
            ("é", "syn"),
        ],
    )
    def test_destino_no_indice(self, resultado, chave, destino):
        plano, _ = resultado
        assert _paginas(plano)[chave].destino == destino

    def test_paginas_em_ordem_estrita_do_readest(self, resultado):
        plano, _ = resultado
        for lista in (plano.do_idx(), plano.do_syn()):
            ordens = [ordem_readest(p.chave) for p in lista]
            assert all(a < b for a, b in zip(ordens, ordens[1:]))

    def test_a_vem_antes_de_a_crase_e_ambos_presentes(self, resultado):
        plano, _ = resultado
        chaves = [p.chave for p in plano.do_idx()]
        assert chaves.index("a") < chaves.index("à")


class TestRelatorio:
    def test_invariantes(self, resultado):
        plano, relatorio = resultado
        assert relatorio.chaves == len(plano.paginas)
        assert relatorio.chaves == relatorio.paginas_simples + relatorio.paginas_combinadas
        assert relatorio.chaves == relatorio.indice["idx"] + relatorio.indice["syn"]
        assert relatorio.indice["idx"] == (
            relatorio.indice["idx_lemas"]
            + relatorio.indice["idx_formas_combinadas"]
            + relatorio.indice["idx_formas_diretas"]
        )
        assert sum(relatorio.artigos_por_pagina.values()) == relatorio.chaves

    def test_sequencias_distintas_das_paginas_combinadas(self, resultado):
        plano, relatorio = resultado
        combinadas = {p.lemas for p in plano.paginas if p.combinada}
        # «foi» e «fora» abrem a mesma sequência (ir, ser)
        assert _paginas(plano)["fora"].lemas == _paginas(plano)["foi"].lemas
        assert relatorio.sequencias_distintas == len(combinadas)
        assert relatorio.paginas_combinadas == len(
            [p for p in plano.paginas if p.combinada]
        )

    def test_to_dict_serializavel(self, resultado):
        _, relatorio = resultado
        dados = relatorio.to_dict()
        assert set(dados) == {
            "chaves", "paginas_simples", "paginas_combinadas",
            "sequencias_distintas", "descartes_sem_letra", "formas_descartadas",
            "artigos_por_pagina", "indice",
        }
        assert all(isinstance(n, str) for n in dados["artigos_por_pagina"])


class TestDeterminismo:
    def test_ordem_da_entrada_nao_muda_o_plano(self, resultado):
        plano, relatorio = resultado
        embaralhados = list(HEADWORDS)
        random.Random(7).shuffle(embaralhados)
        mapa = {lema: list(reversed(formas)) for lema, formas in reversed(MAPA.items())}
        plano2, relatorio2 = agrupar(embaralhados, mapa, set(FREQUENTES))
        assert plano2.paginas == plano.paginas
        assert relatorio2.to_dict() == relatorio.to_dict()
