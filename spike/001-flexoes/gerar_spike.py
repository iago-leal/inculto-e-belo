#!/usr/bin/env python3
"""Gerador do artefato StarDict do spike de flexões (feature 001-spike-de-flexoes).

Spike descartável, mas reprodutível (RN-04): valida se o KOReader mantém latência
aceitável com um .syn em escala real (~1M de formas). Índices reais, corpo trivial —
verbete completo apenas para os lemas do roteiro de 20 palavras.

Uso:
    uv run python gerar_spike.py --piloto      # ~22 verbetes, valida a mecânica do .syn
    uv run python gerar_spike.py               # escala real (RF-01)
    uv run python gerar_spike.py --cobertura flexions-somente   # 1º fallback de RN-05

Regras herdadas das specs (_reversa_sdd/):
  RN-02  banco somente-leitura (URI mode=ro)
  EC-04  forma vazia/só espaços → falha barulhenta com id do registro
  RB-14  flexions.flexion pode ter múltiplas formas separadas por "," ou " ou " → split
  D-04   descartes classificados: orfa | duplicada | identica (comparação exata)
  D-05   formas entram como chaves alternativas (l_word) → PyGlossary materializa o .syn
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import shutil
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("spike")

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
DB_PADRAO = RAIZ_REPO / "aurelio_normalized.db"
DIST = Path(__file__).resolve().parent / "dist"
BASENAME = "aurelio-spike"
BOOKNAME = "Aurélio spike (uso pessoal)"

# RB-14: separadores de formas múltiplas numa única linha de flexions.flexion
SEPARADORES = re.compile(r",| ou ")

# Lemas-alvo do roteiro (recebem verbete completo; ver roteiro.md da feature)
ROTEIRO_LEMAS = {
    "árvore",
    "bela",
    "belo",
    "coração",
    "flor",
    "irmã",
    "mão",
    "olho",
    "papel",
    "pão",
    "voz",
    "amar",
    "cantar",
    "dizer",
    "dormir",
    "estar",
    "ir",
    "ser",
    "poder",
    "saber",
    "trazer",
    "ver",
}


class FormaAnomalaError(Exception):
    """EC-04: registro anômalo nas tabelas de origem interrompe a geração."""


def conectar(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        sys.exit(
            f"ERRO: banco não encontrado em {db_path} — restaure via rclone (README do repo)."
        )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def carregar_headwords(conn: sqlite3.Connection) -> dict[str, list[int]]:
    """Lemas únicos → ids dos entries na ordem editorial (fusão de homônimos)."""
    headwords: dict[str, list[int]] = {}
    cur = conn.execute(
        "SELECT id, lemma FROM entries "
        "ORDER BY lemma, COALESCE(homonym, 999999), COALESCE(sort_key, ''), id"
    )
    for row in cur:
        headwords.setdefault(row["lemma"], []).append(row["id"])
    return headwords


def dividir_formas(bruta: str, tabela: str, rowid: int) -> list[str]:
    """Valida (EC-04) e divide (RB-14) o campo de forma."""
    if bruta is None or not bruta.strip():
        raise FormaAnomalaError(f"forma vazia/só espaços em {tabela}.id={rowid}")
    partes = [p.strip() for p in SEPARADORES.split(bruta)]
    if any(not p for p in partes):
        raise FormaAnomalaError(
            f"fragmento vazio após split em {tabela}.id={rowid}: {bruta!r}"
        )
    return partes


def construir_mapa(
    conn: sqlite3.Connection,
    headwords: dict[str, list[int]],
    cobertura: str,
    restringir_a: set[str] | None = None,
) -> tuple[dict[str, list[str]], dict]:
    """Mapa headword → formas do .syn, com relatório de descartes (D-04)."""
    fontes = [
        ("flexions", "SELECT id, entry_head AS head, flexion AS forma FROM flexions")
    ]
    if cobertura == "total":
        fontes.append(
            (
                "conjugations",
                "SELECT id, infinitive AS head, conjugation AS forma FROM conjugations",
            )
        )

    mapa: dict[str, set[str]] = {}
    vistos: set[tuple[str, str]] = set()
    entrada_linhas = {"flexions": 0, "conjugations": 0}
    entrada_formas = {"flexions": 0, "conjugations": 0}
    descartes = {"orfa": 0, "duplicada": 0, "identica": 0}
    orfas: set[str] = set()
    processadas = 0

    for tabela, sql in fontes:
        for row in conn.execute(sql):
            entrada_linhas[tabela] += 1
            for forma in dividir_formas(row["forma"], tabela, row["id"]):
                entrada_formas[tabela] += 1
                processadas += 1
                if processadas % 100_000 == 0:
                    log.info("progresso pares_processados=%d", processadas)
                head = row["head"]
                if restringir_a is not None and head not in restringir_a:
                    # modo piloto: fora do recorte não conta para o relatório
                    entrada_formas[tabela] -= 1
                    processadas -= 1
                    continue
                if head not in headwords:
                    descartes["orfa"] += 1
                    orfas.add(head)
                    continue
                if forma == head:  # comparação exata, sensível a diacríticos (EC-06)
                    descartes["identica"] += 1
                    continue
                if (forma, head) in vistos:
                    descartes["duplicada"] += 1
                    continue
                vistos.add((forma, head))
                mapa.setdefault(head, set()).add(forma)

    gravadas = len(vistos)
    total_entrada = sum(entrada_formas.values())
    assert total_entrada == gravadas + sum(descartes.values()), (
        f"invariante violada: {total_entrada} != {gravadas} + {descartes}"
    )
    relatorio = {
        "entrada_linhas": entrada_linhas,
        "entrada_formas": entrada_formas,
        "gravadas": gravadas,
        "descartes": descartes,
        "orfas": sorted(orfas),
        "headwords_com_formas": len(mapa),
    }
    return {h: sorted(f) for h, f in mapa.items()}, relatorio


# ---------------------------------------------------------------- renderização


def _esc(texto: str | None) -> str:
    return html.escape(texto) if texto else ""


def _classe_legivel(word_class_summary: str | None) -> str:
    """O campo original é lista delimitada por vírgulas com segmentos vazios."""
    if not word_class_summary:
        return ""
    return " · ".join(p.strip() for p in word_class_summary.split(",") if p.strip())


def corpo_trivial(conn: sqlite3.Connection, lemma: str, ids: list[int]) -> str:
    row = conn.execute(
        "SELECT lemma_stylized, word_class_summary FROM entries WHERE id = ?", (ids[0],)
    ).fetchone()
    titulo = row["lemma_stylized"] or lemma
    classe = (
        f" <i>{_esc(_classe_legivel(row['word_class_summary']))}</i>"
        if row["word_class_summary"]
        else ""
    )
    return f"<b>{_esc(titulo)}</b>{classe} — corpo de teste do spike; verbete completo no build final."


def verbete_completo(conn: sqlite3.Connection, lemma: str, ids: list[int]) -> str:
    """Artigo HTML autocontido com homônimos fundidos (seções numeradas)."""
    partes: list[str] = [f"<b>{_esc(lemma)}</b>"]
    for n, entry_id in enumerate(ids, start=1):
        e = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
        cab = []
        if len(ids) > 1:
            cab.append(f"<b>{n}.</b>")
        if e["lemma_stylized"] and e["lemma_stylized"] != lemma:
            cab.append(f"<b>{_esc(e['lemma_stylized'])}</b>")
        if e["word_class_summary"]:
            cab.append(f"<i>{_esc(_classe_legivel(e['word_class_summary']))}</i>")
        if e["ipa"]:
            cab.append(f"[{_esc(e['ipa'])}]")
        partes.append("<p>" + " ".join(cab) + "</p>" if cab else "")
        if e["etymology_html"]:
            partes.append(f"<p><small>Etim.: {e['etymology_html']}</small></p>")

        blocos = conn.execute(
            "SELECT wcb.id, wcb.intro_text, wc.whole AS classe "
            "FROM word_class_blocks wcb LEFT JOIN word_classes wc ON wc.id = wcb.word_class_id "
            "WHERE wcb.entry_id = ? ORDER BY wcb.position",
            (entry_id,),
        ).fetchall()
        for bloco in blocos:
            if bloco["classe"]:
                partes.append(f"<p><i>{_esc(bloco['classe'])}</i></p>")
            if bloco["intro_text"]:
                partes.append(f"<p>{_esc(bloco['intro_text'])}</p>")
            defs = conn.execute(
                "SELECT d.id, d.number, d.content_html, r.abbreviation AS rubrica "
                "FROM definitions d LEFT JOIN rubrics r ON r.id = d.rubric_id "
                "WHERE d.word_class_block_id = ? ORDER BY d.position",
                (bloco["id"],),
            ).fetchall()
            itens = []
            for d in defs:
                num = f"<b>{_esc(d['number'])}.</b> " if d["number"] else ""
                rub = f"<i>{_esc(d['rubrica'])}</i> " if d["rubrica"] else ""
                exemplo_html = ""
                for ex in conn.execute(
                    "SELECT kind, content_html FROM examples WHERE definition_id = ? ORDER BY position",
                    (d["id"],),
                ):
                    exemplo_html += f" <i>{ex['content_html']}</i>"
                nota_html = ""
                for nt in conn.execute(
                    "SELECT content_html FROM notes WHERE parent_type='definition' AND parent_id=? ORDER BY position",
                    (d["id"],),
                ):
                    nota_html += f" <small>[Obs.: {nt['content_html']}]</small>"
                itens.append(
                    f"<li>{num}{rub}{d['content_html']}{exemplo_html}{nota_html}</li>"
                )
            if itens:
                partes.append("<ul>" + "".join(itens) + "</ul>")

        locucoes = conn.execute(
            "SELECT id, expression FROM locutions WHERE entry_id = ? ORDER BY position",
            (entry_id,),
        ).fetchall()
        if locucoes:
            loc_html = []
            for loc in locucoes:
                defs_loc = conn.execute(
                    "SELECT content_html FROM locution_definitions WHERE locution_id = ? ORDER BY position",
                    (loc["id"],),
                ).fetchall()
                corpo = "; ".join(d["content_html"] for d in defs_loc)
                loc_html.append(f"<li><b>{_esc(loc['expression'])}</b>: {corpo}</li>")
            partes.append("<p><u>Locuções</u></p><ul>" + "".join(loc_html) + "</ul>")

        recoes = conn.execute(
            "SELECT sense, transitivity, prepositions, observation FROM verb_rection "
            "WHERE entry_id = ? ORDER BY COALESCE(sense, 0), position",
            (entry_id,),
        ).fetchall()
        if recoes:
            linhas = []
            for vr in recoes:
                seg = []
                if vr["sense"]:
                    seg.append(f"<b>{vr['sense']}.</b>")
                if vr["transitivity"]:
                    seg.append(_esc(vr["transitivity"]))
                if vr["prepositions"]:
                    seg.append(f"(prep.: {_esc(vr['prepositions'])})")
                if vr["observation"]:
                    seg.append(f"<small>{_esc(vr['observation'])}</small>")
                linhas.append("<li>" + " ".join(seg) + "</li>")
            partes.append(
                "<p><u>Regência (Luft)</u></p><ul>" + "".join(linhas) + "</ul>"
            )

        for nt in conn.execute(
            "SELECT content_html FROM notes WHERE parent_type='entry' AND parent_id=? ORDER BY position",
            (entry_id,),
        ):
            partes.append(f"<p><small>[Nota: {nt['content_html']}]</small></p>")

    return "".join(p for p in partes if p)


# ---------------------------------------------------------------------- build


def gerar(db_path: Path, piloto: bool, cobertura: str) -> None:
    t0 = time.monotonic()
    conn = conectar(db_path)

    headwords = carregar_headwords(conn)
    log.info(
        "headwords lemas_unicos=%d entries=%d",
        len(headwords),
        sum(len(v) for v in headwords.values()),
    )

    recorte = ROTEIRO_LEMAS if piloto else None
    mapa, relatorio = construir_mapa(conn, headwords, cobertura, restringir_a=recorte)
    log.info(
        "mapa gravadas=%d descartes=%s orfas=%d",
        relatorio["gravadas"],
        relatorio["descartes"],
        len(relatorio["orfas"]),
    )

    from pyglossary.glossary_v2 import Glossary  # import tardio: erro nomeado se faltar

    Glossary.init()
    glos = Glossary()
    glos.setInfo("name", BOOKNAME + (" [piloto]" if piloto else ""))
    glos.setInfo("bookname", BOOKNAME + (" [piloto]" if piloto else ""))
    glos.setInfo(
        "description",
        "Artefato de spike: índices em escala real, corpo trivial. Uso estritamente pessoal (RN-03).",
    )
    glos.setInfo("date", time.strftime("%Y-%m-%d"))

    lemas = sorted(recorte & headwords.keys()) if piloto else sorted(headwords)
    for i, lemma in enumerate(lemas):
        ids = headwords[lemma]
        if lemma in ROTEIRO_LEMAS:
            defi = verbete_completo(conn, lemma, ids)
        else:
            defi = corpo_trivial(conn, lemma, ids)
        l_word = [lemma] + mapa.get(lemma, [])
        glos.addEntry(glos.newEntry(l_word, defi, defiFormat="h"))
        if (i + 1) % 10_000 == 0:
            log.info("progresso verbetes_adicionados=%d", i + 1)

    sufixo = "-piloto" if piloto else ""
    destino = DIST / f"{BASENAME}{sufixo}"
    with tempfile.TemporaryDirectory(dir=DIST.parent) as tmp:
        alvo_tmp = Path(tmp) / f"{BASENAME}{sufixo}"
        alvo_tmp.mkdir()
        glos.write(
            str(alvo_tmp / f"{BASENAME}{sufixo}.ifo"),
            formatName="Stardict",
            dictzip=True,
            sametypesequence="h",
        )
        DIST.mkdir(exist_ok=True)
        if destino.exists():
            shutil.rmtree(
                destino
            )  # regeneração: substitui o próprio artefato anterior do spike
        shutil.move(str(alvo_tmp), str(destino))

    duracao = time.monotonic() - t0
    relatorio_final = {
        "artefato": str(destino),
        "piloto": piloto,
        "cobertura": cobertura,
        "headwords": len(lemas),
        **relatorio,
        "duracao_s": round(duracao, 1),
        "arquivos": {p.name: p.stat().st_size for p in sorted(destino.iterdir())},
    }
    rel_path = destino / "relatorio-cobertura.json"
    rel_path.write_text(
        json.dumps(relatorio_final, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    ifo = (destino / f"{BASENAME}{sufixo}.ifo").read_text(encoding="utf-8")
    log.info(
        "build_ok duracao_s=%.1f headwords=%d sinonimos=%d",
        duracao,
        len(lemas),
        relatorio["gravadas"],
    )
    print("---- .ifo ----")
    print(ifo)
    print(f"---- relatório: {rel_path} ----")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--piloto",
        action="store_true",
        help="gera artefato mínimo (só os lemas do roteiro) para validar a mecânica do .syn",
    )
    ap.add_argument(
        "--db", type=Path, default=DB_PADRAO, help="caminho do aurelio_normalized.db"
    )
    ap.add_argument(
        "--cobertura",
        choices=["total", "flexions-somente"],
        default="total",
        help="'flexions-somente' é o 1º fallback de RN-05 (corta as 869k conjugações do .syn)",
    )
    args = ap.parse_args()
    try:
        gerar(args.db, args.piloto, args.cobertura)
    except FormaAnomalaError as exc:
        log.error("EC-04 %s — geração abortada, artefato parcial descartado", exc)
        sys.exit(2)


if __name__ == "__main__":
    main()
