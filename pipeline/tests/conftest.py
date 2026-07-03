"""Fixtures: banco SQLite mínimo com o schema real das 12 tabelas consumidas.

O banco nasce em tmp_path (arquivo) porque o repositório abre por URI mode=ro;
a criação é rápida o suficiente para manter a suíte abaixo de 2 minutos.
Dados cobrem os casos exigidos por T004: homônimos, RB-14 (vírgula e " ou "),
órfã, ambígua, idêntica ao lema e um verbete rico com todas as seções.
"""

import json
import sqlite3
from pathlib import Path

import pytest

SCHEMA = """
CREATE TABLE entries (
    id INTEGER PRIMARY KEY, slug TEXT NOT NULL, slug_reverse TEXT,
    lemma TEXT NOT NULL, lemma_stylized TEXT, homonym INTEGER,
    word_class_summary TEXT, ipa TEXT, orthoepy TEXT,
    etymology_html TEXT, etymology_text TEXT,
    head_type INTEGER, most_used INTEGER, sort_key TEXT
);
CREATE TABLE word_class_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id INTEGER NOT NULL,
    word_class_id INTEGER, position INTEGER NOT NULL, intro_text TEXT
);
CREATE TABLE word_classes (
    id INTEGER PRIMARY KEY, abbreviation TEXT NOT NULL, whole TEXT NOT NULL
);
CREATE TABLE definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, word_class_block_id INTEGER NOT NULL,
    position INTEGER NOT NULL, number TEXT,
    content_html TEXT NOT NULL, content_text TEXT NOT NULL, rubric_id INTEGER
);
CREATE TABLE rubrics (
    id INTEGER PRIMARY KEY, abbreviation TEXT NOT NULL, whole TEXT NOT NULL
);
CREATE TABLE examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT, definition_id INTEGER,
    locution_definition_id INTEGER, position INTEGER NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN ('editor','citation')),
    content_html TEXT NOT NULL, content_text TEXT NOT NULL
);
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_type TEXT NOT NULL CHECK(parent_type IN
        ('entry','definition','locution','locution_definition')),
    parent_id INTEGER NOT NULL, position INTEGER NOT NULL,
    content_html TEXT NOT NULL, content_text TEXT NOT NULL
);
CREATE TABLE locutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id INTEGER NOT NULL,
    position INTEGER NOT NULL, expression TEXT NOT NULL, rubric_id INTEGER
);
CREATE TABLE locution_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, locution_id INTEGER NOT NULL,
    position INTEGER NOT NULL, number TEXT,
    content_html TEXT NOT NULL, content_text TEXT NOT NULL, rubric_id INTEGER
);
CREATE TABLE verb_rection (
    id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id INTEGER NOT NULL,
    sense INTEGER, position INTEGER NOT NULL, transitivity TEXT,
    prepositions TEXT, observation TEXT,
    source TEXT NOT NULL DEFAULT 'luft', raw_text TEXT
);
CREATE TABLE flexions (
    id INTEGER PRIMARY KEY, entry_head TEXT NOT NULL, entry_head_slug TEXT,
    flexion TEXT NOT NULL, flexion_slug TEXT, type INTEGER, homonym INTEGER
);
CREATE TABLE conjugations (
    id INTEGER PRIMARY KEY, infinitive TEXT NOT NULL, tense INTEGER NOT NULL,
    person TEXT, conjugation TEXT NOT NULL, homonym INTEGER
);
"""

DADOS = """
INSERT INTO entries VALUES
 (1,'belo',NULL,'belo','Belo',NULL,'adj., s.m.','ˈbɛlu',NULL,
  '<em>Do lat. bellu.</em>','Do lat. bellu.',1,1,'belo'),
 (2,'bela',NULL,'bela',NULL,NULL,'s.f.',NULL,NULL,NULL,NULL,1,NULL,'bela'),
 (3,'manga',NULL,'manga',NULL,1,'s.f.',NULL,NULL,NULL,NULL,1,NULL,'manga'),
 (4,'manga',NULL,'manga',NULL,2,'s.f.',NULL,NULL,NULL,NULL,1,NULL,'manga'),
 (5,'amar',NULL,'amar',NULL,NULL,'v.t.d.',NULL,NULL,NULL,NULL,1,NULL,'amar');

INSERT INTO word_classes VALUES
 (1,'adj.','adjetivo'),(2,'s.m.','substantivo masculino'),
 (3,'s.f.','substantivo feminino'),(4,'v.t.d.','verbo transitivo direto');

INSERT INTO word_class_blocks (id, entry_id, word_class_id, position, intro_text) VALUES
 (1,1,1,1,NULL),(2,1,2,2,'Indica:'),(3,3,3,1,NULL),(4,4,3,1,NULL),
 (5,5,4,1,NULL),(6,2,3,1,NULL);

INSERT INTO rubrics VALUES (1,'Fig.','Figurado');

INSERT INTO definitions (id, word_class_block_id, position, number, content_html, content_text, rubric_id) VALUES
 (1,1,1,'1','<em>Que</em> tem beleza','Que tem beleza',NULL),
 (2,1,2,'2','Agradável aos olhos','Agradável aos olhos',1),
 (3,2,1,NULL,'O que é belo','O que é belo',NULL),
 (4,3,1,'1','Fruta da mangueira','Fruta da mangueira',NULL),
 (5,4,1,'1','Parte da camisa que cobre o braço','Parte da camisa que cobre o braço',NULL),
 (6,5,1,'1','Ter amor a','Ter amor a',NULL),
 (7,6,1,'1','Mulher bela','Mulher bela',NULL);

INSERT INTO examples (id, definition_id, locution_definition_id, position, kind, content_html, content_text) VALUES
 (1,1,NULL,1,'editor','Um <em>belo</em> dia','Um belo dia'),
 (2,1,NULL,2,'citation','“Tudo era belo” (Bilac)','“Tudo era belo” (Bilac)');

INSERT INTO notes (id, parent_type, parent_id, position, content_html, content_text) VALUES
 (1,'definition',1,1,'Superlativo: belíssimo','Superlativo: belíssimo'),
 (2,'entry',1,1,'Nota do verbete belo','Nota do verbete belo');

INSERT INTO locutions (id, entry_id, position, expression, rubric_id) VALUES
 (1,1,1,'belo dia',NULL);

INSERT INTO locution_definitions (id, locution_id, position, number, content_html, content_text, rubric_id) VALUES
 (1,1,1,NULL,'Dia agradável','Dia agradável',NULL);

INSERT INTO examples (id, definition_id, locution_definition_id, position, kind, content_html, content_text) VALUES
 (3,NULL,1,1,'editor','Que belo dia!','Que belo dia!');

INSERT INTO verb_rection (id, entry_id, sense, position, transitivity, prepositions, observation, source, raw_text) VALUES
 (1,5,1,1,'v.t.d.',NULL,NULL,'luft',NULL),
 (2,5,1,2,NULL,NULL,'Também pronominal','luft',NULL);

INSERT INTO flexions (id, entry_head, entry_head_slug, flexion, flexion_slug, type, homonym) VALUES
 (1,'belo','belo','belas','belas',3,NULL),
 (2,'bela','bela','belas','belas',1,NULL),
 (3,'belo','belo','belos, belinhos',NULL,1,NULL),
 (4,'manga','manga','manguitas ou manguinhas',NULL,4,NULL),
 (5,'belo','belo','belo',NULL,1,NULL),
 (6,'inexistente','inexistente','inexistentes',NULL,1,NULL);

INSERT INTO conjugations (id, infinitive, tense, person, conjugation, homonym) VALUES
 (1,'amar',1,'eu','amo',NULL),
 (2,'amar',1,'nós','amamos',NULL),
 (3,'amar',2,'nós','amamos',NULL);
"""

CONTAGENS = {
    "entries": 5,
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


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    caminho = tmp_path / "aurelio_teste.db"
    conn = sqlite3.connect(caminho)
    conn.executescript(SCHEMA)
    conn.executescript(DADOS)
    conn.commit()
    conn.close()
    return caminho


@pytest.fixture()
def manifesto_path(tmp_path: Path) -> Path:
    caminho = tmp_path / "manifesto-integridade.json"
    caminho.write_text(
        json.dumps({"gerado_em": "2026-07-03", "contagens": CONTAGENS}),
        encoding="utf-8",
    )
    return caminho
