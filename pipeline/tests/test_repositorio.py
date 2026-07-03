"""Testes da ingestão (T017, completando o aceite de RF-01: cada erro nomeado coberto)."""

import json
import sqlite3

import pytest

from aurelio_pipeline.erros import (
    BancoAusenteError,
    BancoCorrompidoError,
    ContagemDivergenteError,
    EsquemaInvalidoError,
    ManifestoAusenteError,
)
from aurelio_pipeline.infra.repositorio import RepositorioAurelio


class TestErrosNomeados:
    def test_banco_ausente_com_instrucao_de_restauracao(self, tmp_path, manifesto_path):
        repo = RepositorioAurelio(tmp_path / "nao-existe.db", manifesto_path)
        with pytest.raises(BancoAusenteError, match="rclone copy"):
            repo.validar()

    def test_banco_corrompido(self, tmp_path, manifesto_path):
        caminho = tmp_path / "lixo.db"
        caminho.write_bytes(b"isto nao e um sqlite" * 100)
        with pytest.raises(BancoCorrompidoError):
            RepositorioAurelio(caminho, manifesto_path).validar()

    def test_esquema_invalido_lista_todas_as_divergencias(
        self, tmp_path, manifesto_path
    ):
        caminho = tmp_path / "parcial.db"
        conn = sqlite3.connect(caminho)
        conn.execute(
            "CREATE TABLE entries (id INTEGER PRIMARY KEY)"
        )  # sem as demais colunas
        conn.commit()
        conn.close()
        with pytest.raises(EsquemaInvalidoError) as excinfo:
            RepositorioAurelio(caminho, manifesto_path).validar()
        mensagem = str(excinfo.value)
        assert "colunas ausentes em entries" in mensagem
        assert "tabela ausente: flexions" in mensagem
        assert "tabela ausente: conjugations" in mensagem

    def test_contagem_divergente_aponta_esperado_e_obtido(self, db_path, tmp_path):
        manifesto = tmp_path / "manifesto-errado.json"
        manifesto.write_text(
            json.dumps(
                {
                    "contagens": {
                        "entries": 999,
                        "word_class_blocks": 6,
                        "word_classes": 4,
                        "definitions": 7,
                        "rubrics": 1,
                        "examples": 3,
                        "notes": 2,
                        "locutions": 1,
                        "locution_definitions": 1,
                        "verb_rection": 2,
                        "flexions": 6,
                        "conjugations": 3,
                    }
                }
            ),
            encoding="utf-8",
        )
        with pytest.raises(ContagemDivergenteError, match=r"esperado=999 obtido=5"):
            RepositorioAurelio(db_path, manifesto).validar()

    def test_manifesto_ausente(self, db_path, tmp_path):
        with pytest.raises(ManifestoAusenteError):
            RepositorioAurelio(db_path, tmp_path / "nao-existe.json").validar()

    def test_escrita_impossivel_por_construcao(self, db_path, manifesto_path):
        repo = RepositorioAurelio(db_path, manifesto_path)
        repo.validar()
        with pytest.raises(sqlite3.OperationalError):
            repo._abrir().execute("INSERT INTO rubrics VALUES (99, 'x', 'y')")


class TestConsultas:
    def test_validar_retorna_totais(self, db_path, manifesto_path):
        totais = RepositorioAurelio(db_path, manifesto_path).validar()
        assert totais["entries"] == 5
        assert totais["flexions"] == 6

    def test_headwords_sao_lemas_unicos_ordenados(self, db_path, manifesto_path):
        repo = RepositorioAurelio(db_path, manifesto_path)
        assert repo.headwords() == ["amar", "bela", "belo", "manga"]

    def test_pares_brutos_sem_split(self, db_path, manifesto_path):
        repo = RepositorioAurelio(db_path, manifesto_path)
        flexoes = list(repo.flexoes())
        assert (3, "belo", "belos, belinhos") in flexoes  # split RB-14 é do domínio
        assert len(flexoes) == 6
        assert len(list(repo.conjugacoes())) == 3

    def test_artigos_agrupam_homonimos_na_ordem(self, db_path, manifesto_path):
        repo = RepositorioAurelio(db_path, manifesto_path)
        artigos = dict((lemma, verbetes) for lemma, verbetes in repo.artigos())
        assert set(artigos) == {"amar", "bela", "belo", "manga"}
        assert [v.homonym for v in artigos["manga"]] == [1, 2]

    def test_agregado_rico_completo(self, db_path, manifesto_path):
        repo = RepositorioAurelio(db_path, manifesto_path)
        belo = dict(repo.artigos())["belo"][0]
        assert belo.ipa == "ˈbɛlu"
        assert [bloco.classe for bloco in belo.blocos] == [
            "adjetivo",
            "substantivo masculino",
        ]
        definicao = belo.blocos[0].definicoes[0]
        assert definicao.content_text == "Que tem beleza"
        assert [exemplo.kind for exemplo in definicao.exemplos] == [
            "editor",
            "citation",
        ]
        assert definicao.notas[0].content_text == "Superlativo: belíssimo"
        assert belo.blocos[0].definicoes[1].rubrica == "Fig."
        assert belo.locucoes[0].expression == "belo dia"
        assert (
            belo.locucoes[0].definicoes[0].exemplos[0].content_text == "Que belo dia!"
        )
        assert belo.notas[0].content_text == "Nota do verbete belo"

    def test_regencia_do_verbo(self, db_path, manifesto_path):
        repo = RepositorioAurelio(db_path, manifesto_path)
        amar = dict(repo.artigos())["amar"][0]
        assert amar.regencias[0].transitivity == "v.t.d."
        assert amar.regencias[1].observation == "Também pronominal"

    def test_textos_definicoes_do_lema(self, db_path, manifesto_path):
        repo = RepositorioAurelio(db_path, manifesto_path)
        assert repo.textos_definicoes("manga") == [
            "Fruta da mangueira",
            "Parte da camisa que cobre o braço",
        ]
