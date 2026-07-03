"""Testes de unidade do índice de flexões (T005; spec indice-de-flexoes §6)."""

import pytest

from aurelio_pipeline.dominio.indice_flexoes import construir_mapa, dividir_formas
from aurelio_pipeline.erros import FormaAnomalaError

HEADWORDS = {"belo", "bela", "manga", "amar"}

FLEXIONS = [
    (1, "belo", "belas"),
    (2, "bela", "belas"),
    (3, "belo", "belos, belinhos"),
    (4, "manga", "manguitas ou manguinhas"),
    (5, "belo", "belo"),
    (6, "inexistente", "inexistentes"),
]
CONJUGATIONS = [
    (1, "amar", "amo"),
    (2, "amar", "amamos"),
    (3, "amar", "amamos"),
]


def _fontes():
    return {"flexions": iter(FLEXIONS), "conjugations": iter(CONJUGATIONS)}


class TestDividirFormas:
    def test_split_por_virgula(self):
        assert dividir_formas("belos, belinhos", "flexions", 3) == ["belos", "belinhos"]

    def test_split_por_ou(self):
        assert dividir_formas("manguitas ou manguinhas", "flexions", 4) == [
            "manguitas",
            "manguinhas",
        ]

    def test_forma_simples_nao_divide(self):
        assert dividir_formas("belas", "flexions", 1) == ["belas"]

    def test_forma_vazia_falha_com_id(self):
        with pytest.raises(FormaAnomalaError, match=r"flexions\.id=99"):
            dividir_formas("   ", "flexions", 99)

    def test_fragmento_vazio_apos_split_falha(self):
        with pytest.raises(FormaAnomalaError, match=r"conjugations\.id=7"):
            dividir_formas("amo, ", "conjugations", 7)


class TestConstruirMapa:
    def test_orfa_descartada_e_listada(self):
        mapa, rel = construir_mapa(_fontes(), HEADWORDS)
        assert rel.descartes["orfa"] == 1
        assert rel.orfas == ["inexistente"]
        assert "inexistente" not in mapa

    def test_identica_descartada_com_comparacao_exata(self):
        mapa, rel = construir_mapa(_fontes(), HEADWORDS)
        assert rel.descartes["identica"] == 1
        assert "belo" not in mapa.get("belo", [])

    def test_duplicada_entra_uma_vez(self):
        mapa, rel = construir_mapa(_fontes(), HEADWORDS)
        assert rel.descartes["duplicada"] == 1
        assert mapa["amar"].count("amamos") == 1

    def test_ambigua_preservada_em_n_headwords(self):
        mapa, _ = construir_mapa(_fontes(), HEADWORDS)
        assert "belas" in mapa["belo"]
        assert "belas" in mapa["bela"]

    def test_split_rb14_indexado(self):
        mapa, _ = construir_mapa(_fontes(), HEADWORDS)
        assert {"belos", "belinhos"} <= set(mapa["belo"])
        assert {"manguitas", "manguinhas"} <= set(mapa["manga"])

    def test_invariante_fecha(self):
        _, rel = construir_mapa(_fontes(), HEADWORDS)
        total_entrada = sum(rel.entrada_formas.values())
        assert total_entrada == 11
        assert total_entrada == rel.gravadas + sum(rel.descartes.values())
        assert rel.gravadas == 8

    def test_contagens_por_tabela(self):
        _, rel = construir_mapa(_fontes(), HEADWORDS)
        assert rel.entrada_linhas == {"flexions": 6, "conjugations": 3}
        assert rel.entrada_formas == {"flexions": 8, "conjugations": 3}

    def test_determinismo(self):
        mapa1, rel1 = construir_mapa(_fontes(), HEADWORDS)
        mapa2, rel2 = construir_mapa(_fontes(), HEADWORDS)
        assert mapa1 == mapa2
        assert rel1.to_dict() == rel2.to_dict()

    def test_formas_ordenadas_por_headword(self):
        mapa, _ = construir_mapa(_fontes(), HEADWORDS)
        for formas in mapa.values():
            assert formas == sorted(formas)
