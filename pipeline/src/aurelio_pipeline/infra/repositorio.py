"""Ingestão do banco lexical (spec ingestao-aurelio): único dono do SQL.

Banco somente-leitura por construção (URI mode=ro, RN-01). Valida esquema e
contagens contra o manifesto de integridade antes de expor qualquer dado, com
falha barulhenta e erros nomeados. Consumidores recebem agregados e pares —
nunca cursores, SQL ou nomes de tabela.
"""

import json
import logging
import sqlite3
import time
from collections.abc import Iterator
from pathlib import Path

from aurelio_pipeline.dominio.modelos import (
    BlocoClasse,
    Definicao,
    Exemplo,
    Locucao,
    Nota,
    Regencia,
    Verbete,
)
from aurelio_pipeline.erros import (
    BancoAusenteError,
    BancoCorrompidoError,
    BancoIndisponivelError,
    ContagemDivergenteError,
    EsquemaInvalidoError,
    ManifestoAusenteError,
)

log = logging.getLogger("aurelio.ingestao")

COLUNAS_REQUERIDAS: dict[str, set[str]] = {
    "entries": {
        "id",
        "lemma",
        "lemma_stylized",
        "homonym",
        "word_class_summary",
        "ipa",
        "etymology_html",
        "sort_key",
    },
    "word_class_blocks": {"id", "entry_id", "word_class_id", "position", "intro_text"},
    "word_classes": {"id", "whole"},
    "definitions": {
        "id",
        "word_class_block_id",
        "position",
        "number",
        "content_html",
        "content_text",
        "rubric_id",
    },
    "rubrics": {"id", "abbreviation"},
    "examples": {
        "id",
        "definition_id",
        "locution_definition_id",
        "position",
        "kind",
        "content_html",
        "content_text",
    },
    "notes": {
        "id",
        "parent_type",
        "parent_id",
        "position",
        "content_html",
        "content_text",
    },
    "locutions": {"id", "entry_id", "position", "expression", "rubric_id"},
    "locution_definitions": {
        "id",
        "locution_id",
        "position",
        "number",
        "content_html",
        "content_text",
        "rubric_id",
    },
    "verb_rection": {
        "id",
        "entry_id",
        "sense",
        "position",
        "transitivity",
        "prepositions",
        "observation",
    },
    "flexions": {"id", "entry_head", "flexion"},
    "conjugations": {"id", "infinitive", "conjugation"},
}

ORDEM_FUSAO = "ORDER BY lemma, COALESCE(homonym, 999999), COALESCE(sort_key, ''), id"


class RepositorioAurelio:
    def __init__(self, db_path: Path, manifesto_path: Path):
        self._db_path = Path(db_path)
        self._manifesto_path = Path(manifesto_path)
        self._conn: sqlite3.Connection | None = None
        self._classes: dict[int, str] = {}
        self._rubricas: dict[int, str] = {}

    # ------------------------------------------------------------- conexão

    def _abrir(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        if not self._db_path.exists():
            raise BancoAusenteError(
                f"banco não encontrado em {self._db_path} — restaure com: "
                f"rclone copy gdrive:inculto-e-belo/aurelio_normalized.db {self._db_path.parent}/"
            )
        try:
            conn = sqlite3.connect(f"file:{self._db_path}?mode=ro", uri=True, timeout=5)
            conn.row_factory = sqlite3.Row
            conn.execute("SELECT 1 FROM sqlite_schema LIMIT 1").fetchone()
        except sqlite3.DatabaseError as exc:
            if "locked" in str(exc).lower() or "busy" in str(exc).lower():
                raise BancoIndisponivelError(
                    f"banco bloqueado por outro processo: {exc} — feche o processo concorrente"
                ) from exc
            raise BancoCorrompidoError(
                f"banco ilegível ({exc}) — restaure com: "
                f"rclone copy gdrive:inculto-e-belo/aurelio_normalized.db {self._db_path.parent}/"
            ) from exc
        self._conn = conn
        return conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # ------------------------------------------------------------ validação

    def _carregar_manifesto(self) -> dict[str, int]:
        try:
            dados = json.loads(self._manifesto_path.read_text(encoding="utf-8"))
            return {tabela: int(n) for tabela, n in dados["contagens"].items()}
        except (OSError, ValueError, KeyError) as exc:
            raise ManifestoAusenteError(
                f"manifesto de integridade ilegível em {self._manifesto_path}: {exc} — "
                "regenere-o conforme pipeline/README.md e commite a mudança"
            ) from exc

    def validar(self) -> dict[str, int]:
        """Smoke tests de esquema e contagem (RF-01, RF-03, RF-04 da spec). Retorna os totais."""
        inicio = time.monotonic()
        conn = self._abrir()
        manifesto = self._carregar_manifesto()

        divergencias_esquema: list[str] = []
        for tabela, colunas in COLUNAS_REQUERIDAS.items():
            existentes = {
                linha["name"]
                for linha in conn.execute(f"PRAGMA table_info({tabela})").fetchall()
            }
            if not existentes:
                divergencias_esquema.append(f"tabela ausente: {tabela}")
                continue
            faltantes = colunas - existentes
            if faltantes:
                divergencias_esquema.append(
                    f"colunas ausentes em {tabela}: {', '.join(sorted(faltantes))}"
                )
        if divergencias_esquema:
            raise EsquemaInvalidoError("; ".join(divergencias_esquema))

        totais: dict[str, int] = {}
        divergencias_contagem: list[str] = []
        for tabela in COLUNAS_REQUERIDAS:
            total = conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
            totais[tabela] = total
            esperado = manifesto.get(tabela)
            if esperado is None:
                divergencias_contagem.append(f"{tabela}: sem entrada no manifesto")
            elif total != esperado:
                divergencias_contagem.append(
                    f"{tabela}: esperado={esperado} obtido={total}"
                )
        if divergencias_contagem:
            raise ContagemDivergenteError(
                "; ".join(divergencias_contagem)
                + " — se a mudança do banco foi deliberada, atualize "
                "pipeline/manifesto-integridade.json em commit próprio"
            )

        duracao_ms = round((time.monotonic() - inicio) * 1000)
        log.info(
            "smoke_tests_ok duracao_ms=%d %s",
            duracao_ms,
            " ".join(f"{tabela}={n}" for tabela, n in totais.items()),
        )
        return totais

    # ------------------------------------------------------------- consultas

    def _caches(self, conn: sqlite3.Connection) -> None:
        if not self._classes:
            self._classes = {
                linha["id"]: linha["whole"]
                for linha in conn.execute("SELECT id, whole FROM word_classes")
            }
            self._rubricas = {
                linha["id"]: linha["abbreviation"]
                for linha in conn.execute("SELECT id, abbreviation FROM rubrics")
            }

    def headwords(self) -> list[str]:
        conn = self._abrir()
        return [
            linha["lemma"]
            for linha in conn.execute(
                "SELECT DISTINCT lemma FROM entries ORDER BY lemma"
            )
        ]

    def flexoes(self) -> Iterator[tuple[int, str, str]]:
        conn = self._abrir()
        for linha in conn.execute(
            "SELECT id, entry_head, flexion FROM flexions ORDER BY id"
        ):
            yield linha["id"], linha["entry_head"], linha["flexion"]

    def conjugacoes(self) -> Iterator[tuple[int, str, str]]:
        conn = self._abrir()
        for linha in conn.execute(
            "SELECT id, infinitive, conjugation FROM conjugations ORDER BY id"
        ):
            yield linha["id"], linha["infinitive"], linha["conjugation"]

    def textos_definicoes(self, lemma: str) -> list[str]:
        """content_text das acepções do lema (todas as entries homônimas), para a paridade."""
        conn = self._abrir()
        return [
            linha["content_text"]
            for linha in conn.execute(
                "SELECT d.content_text FROM definitions d "
                "JOIN word_class_blocks b ON d.word_class_block_id = b.id "
                "JOIN entries e ON b.entry_id = e.id "
                "WHERE e.lemma = ? ORDER BY e.id, b.position, d.position",
                (lemma,),
            )
        ]

    # ------------------------------------------------------------- agregados

    def _notas(self, conn, parent_type: str, parent_id: int) -> tuple[Nota, ...]:
        return tuple(
            Nota(linha["content_html"], linha["content_text"])
            for linha in conn.execute(
                "SELECT content_html, content_text FROM notes "
                "WHERE parent_type = ? AND parent_id = ? ORDER BY position",
                (parent_type, parent_id),
            )
        )

    def _exemplos(self, conn, coluna: str, dono_id: int) -> tuple[Exemplo, ...]:
        return tuple(
            Exemplo(linha["kind"], linha["content_html"], linha["content_text"])
            for linha in conn.execute(
                f"SELECT kind, content_html, content_text FROM examples "
                f"WHERE {coluna} = ? ORDER BY position",
                (dono_id,),
            )
        )

    def _definicoes(self, conn, bloco_id: int) -> tuple[Definicao, ...]:
        return tuple(
            Definicao(
                numero=linha["number"],
                rubrica=self._rubricas.get(linha["rubric_id"]),
                content_html=linha["content_html"],
                content_text=linha["content_text"],
                exemplos=self._exemplos(conn, "definition_id", linha["id"]),
                notas=self._notas(conn, "definition", linha["id"]),
            )
            for linha in conn.execute(
                "SELECT id, number, content_html, content_text, rubric_id "
                "FROM definitions WHERE word_class_block_id = ? ORDER BY position",
                (bloco_id,),
            )
        )

    def _locucoes(self, conn, entry_id: int) -> tuple[Locucao, ...]:
        locucoes = []
        for loc in conn.execute(
            "SELECT id, expression, rubric_id FROM locutions "
            "WHERE entry_id = ? ORDER BY position",
            (entry_id,),
        ):
            definicoes = tuple(
                Definicao(
                    numero=linha["number"],
                    rubrica=self._rubricas.get(linha["rubric_id"]),
                    content_html=linha["content_html"],
                    content_text=linha["content_text"],
                    exemplos=self._exemplos(
                        conn, "locution_definition_id", linha["id"]
                    ),
                    notas=self._notas(conn, "locution_definition", linha["id"]),
                )
                for linha in conn.execute(
                    "SELECT id, number, content_html, content_text, rubric_id "
                    "FROM locution_definitions WHERE locution_id = ? ORDER BY position",
                    (loc["id"],),
                )
            )
            locucoes.append(
                Locucao(
                    expression=loc["expression"],
                    rubrica=self._rubricas.get(loc["rubric_id"]),
                    definicoes=definicoes,
                    notas=self._notas(conn, "locution", loc["id"]),
                )
            )
        return tuple(locucoes)

    def _verbete(self, conn, entry: sqlite3.Row) -> Verbete:
        blocos = tuple(
            BlocoClasse(
                classe=self._classes.get(bloco["word_class_id"]),
                intro_text=bloco["intro_text"],
                definicoes=self._definicoes(conn, bloco["id"]),
            )
            for bloco in conn.execute(
                "SELECT id, word_class_id, intro_text FROM word_class_blocks "
                "WHERE entry_id = ? ORDER BY position",
                (entry["id"],),
            )
        )
        regencias = tuple(
            Regencia(
                sense=linha["sense"],
                transitivity=linha["transitivity"],
                prepositions=linha["prepositions"],
                observation=linha["observation"],
            )
            for linha in conn.execute(
                "SELECT sense, transitivity, prepositions, observation FROM verb_rection "
                "WHERE entry_id = ? ORDER BY COALESCE(sense, 0), position",
                (entry["id"],),
            )
        )
        return Verbete(
            id=entry["id"],
            lemma=entry["lemma"],
            lemma_stylized=entry["lemma_stylized"],
            homonym=entry["homonym"],
            word_class_summary=entry["word_class_summary"],
            ipa=entry["ipa"],
            etymology_html=entry["etymology_html"],
            blocos=blocos,
            locucoes=self._locucoes(conn, entry["id"]),
            notas=self._notas(conn, "entry", entry["id"]),
            regencias=regencias,
        )

    def artigos(self) -> Iterator[tuple[str, list[Verbete]]]:
        """Agregados completos por lema, na ordem de fusão de homônimos (RF-05/RF-02)."""
        conn = self._abrir()
        self._caches(conn)
        lote: list[Verbete] = []
        lema_atual: str | None = None
        cursor = conn.cursor()
        for entry in cursor.execute(f"SELECT * FROM entries {ORDEM_FUSAO}"):
            if lema_atual is not None and entry["lemma"] != lema_atual:
                yield lema_atual, lote
                lote = []
            lema_atual = entry["lemma"]
            lote.append(self._verbete(conn, entry))
        if lema_atual is not None:
            yield lema_atual, lote
