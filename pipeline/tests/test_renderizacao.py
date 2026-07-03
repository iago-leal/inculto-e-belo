"""Testes de unidade do renderizador Verbete → HTML (T006; RF-04, D-06)."""

import re

from aurelio_pipeline.dominio.modelos import (
    BlocoClasse,
    Definicao,
    Exemplo,
    Locucao,
    Nota,
    Regencia,
    Verbete,
)
from aurelio_pipeline.dominio.renderizacao import renderizar_artigo

TAGS_PERMITIDAS = {"b", "i", "u", "p", "ul", "li", "small", "em", "strong"}


def _verbete_rico() -> Verbete:
    return Verbete(
        id=1,
        lemma="belo",
        lemma_stylized="Belo",
        homonym=None,
        word_class_summary="adj., s.m.",
        ipa="ˈbɛlu",
        etymology_html="<em>Do lat. bellu.</em>",
        blocos=(
            BlocoClasse(
                classe="adjetivo",
                intro_text=None,
                definicoes=(
                    Definicao(
                        numero="1",
                        rubrica=None,
                        content_html="<em>Que</em> tem beleza",
                        content_text="Que tem beleza",
                        exemplos=(
                            Exemplo("editor", "Um <em>belo</em> dia", "Um belo dia"),
                            Exemplo(
                                "citation",
                                "“Tudo era belo” (Bilac)",
                                "“Tudo era belo” (Bilac)",
                            ),
                        ),
                        notas=(
                            Nota("Superlativo: belíssimo", "Superlativo: belíssimo"),
                        ),
                    ),
                    Definicao(
                        numero="2",
                        rubrica="Fig.",
                        content_html="Agradável aos olhos",
                        content_text="Agradável aos olhos",
                        exemplos=(),
                        notas=(),
                    ),
                ),
            ),
            BlocoClasse(
                classe="substantivo masculino",
                intro_text="Indica:",
                definicoes=(
                    Definicao(
                        numero=None,
                        rubrica=None,
                        content_html="O que é belo",
                        content_text="O que é belo",
                        exemplos=(),
                        notas=(),
                    ),
                ),
            ),
        ),
        locucoes=(
            Locucao(
                expression="belo dia",
                rubrica=None,
                definicoes=(
                    Definicao(
                        numero=None,
                        rubrica=None,
                        content_html="Dia agradável",
                        content_text="Dia agradável",
                        exemplos=(Exemplo("editor", "Que belo dia!", "Que belo dia!"),),
                        notas=(),
                    ),
                ),
                notas=(),
            ),
        ),
        notas=(Nota("Nota do verbete belo", "Nota do verbete belo"),),
        regencias=(
            Regencia(
                sense=1, transitivity="v.t.d.", prepositions=None, observation=None
            ),
        ),
    )


def _manga(homonym: int, definicao: str) -> Verbete:
    return Verbete(
        id=homonym + 10,
        lemma="manga",
        lemma_stylized=None,
        homonym=homonym,
        word_class_summary="s.f.",
        ipa=None,
        etymology_html=None,
        blocos=(
            BlocoClasse(
                classe="substantivo feminino",
                intro_text=None,
                definicoes=(
                    Definicao(
                        numero="1",
                        rubrica=None,
                        content_html=definicao,
                        content_text=definicao,
                        exemplos=(),
                        notas=(),
                    ),
                ),
            ),
        ),
        locucoes=(),
        notas=(),
        regencias=(),
    )


class TestVerbeteIntegral:
    def test_todas_as_secoes_presentes(self):
        html = renderizar_artigo("belo", [_verbete_rico()])
        assert "Belo" in html  # lema estilizado
        assert "ˈbɛlu" in html  # IPA
        assert "Do lat. bellu." in html  # etimologia
        assert "<em>Que</em> tem beleza" in html and "Agradável aos olhos" in html
        assert "Fig." in html  # rubrica
        assert "Um <em>belo</em> dia" in html  # exemplo editor (HTML embutido intacto)
        assert "Tudo era belo" in html  # exemplo citation
        assert "Superlativo: belíssimo" in html  # nota da definição
        assert "belo dia" in html and "Dia agradável" in html  # locução
        assert "Que belo dia!" in html  # exemplo da definição de locução
        assert "v.t.d." in html  # regência
        assert "Nota do verbete belo" in html  # nota do verbete
        assert "Indica:" in html  # intro do bloco

    def test_ordem_das_definicoes_segue_position(self):
        html = renderizar_artigo("belo", [_verbete_rico()])
        assert html.index("tem beleza") < html.index("Agradável aos olhos")
        assert html.index("Agradável aos olhos") < html.index("O que é belo")

    def test_distincao_editor_citation(self):
        html = renderizar_artigo("belo", [_verbete_rico()])
        pos_editor = html.index("Um <em>belo</em> dia")
        pos_citation = html.index("“Tudo era belo” (Bilac)")
        trecho_editor = html[pos_editor - 40 : pos_editor]
        trecho_citation = html[pos_citation - 40 : pos_citation]
        assert trecho_editor != trecho_citation  # marcação distinta por kind (RB-07)
        assert "<small>" in trecho_citation

    def test_vocabulario_de_tags_restrito(self):
        html = renderizar_artigo("belo", [_verbete_rico()])
        tags = set(re.findall(r"</?([a-z0-9]+)", html))
        assert tags <= TAGS_PERMITIDAS


class TestFusaoDeHomonimos:
    def test_secoes_numeradas_na_ordem(self):
        html = renderizar_artigo(
            "manga", [_manga(1, "Fruta da mangueira"), _manga(2, "Parte da camisa")]
        )
        assert "<b>1.</b>" in html and "<b>2.</b>" in html
        assert html.index("Fruta da mangueira") < html.index("Parte da camisa")

    def test_verbete_unico_sem_numeracao_de_secao(self):
        html = renderizar_artigo("belo", [_verbete_rico()])
        assert "<b>1.</b> <b>Belo</b>" not in html


class TestAdvertencia:
    def test_artigo_gigante_dispara_advertencia(self):
        avisos: list[str] = []
        verbete = _manga(1, "x" * 2_000_000)
        renderizar_artigo("manga", [verbete], advertir=avisos.append)
        assert avisos and "manga" in avisos[0]
