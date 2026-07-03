"""Renderização Verbete → artigo HTML autocontido (RF-04; função pura, sem I/O).

Vocabulário de tags validado no spike (D-06): b, i, u, p, ul, li, small — mais
as tags embutidas do banco (em, u, strong; RB-03). content_html entra como está.
"""

import html
from collections.abc import Callable, Sequence

from aurelio_pipeline.dominio.modelos import Definicao, Locucao, Nota, Verbete

LIMITE_ADVERTENCIA_BYTES = 1_000_000  # EC-05 da spec conversao-formato


def _esc(texto: str | None) -> str:
    return html.escape(texto, quote=False) if texto else ""


def _classe_legivel(word_class_summary: str | None) -> str:
    """O campo original é lista delimitada por vírgulas com segmentos vazios."""
    if not word_class_summary:
        return ""
    return " · ".join(p.strip() for p in word_class_summary.split(",") if p.strip())


def _exemplos_html(definicao: Definicao) -> str:
    partes = []
    for exemplo in definicao.exemplos:
        if exemplo.kind == "citation":
            partes.append(f" <small><i>{exemplo.content_html}</i></small>")
        else:
            partes.append(f" <i>{exemplo.content_html}</i>")
    return "".join(partes)


def _notas_html(notas: Sequence[Nota]) -> str:
    return "".join(f" <small>[Obs.: {nota.content_html}]</small>" for nota in notas)


def _definicao_li(definicao: Definicao) -> str:
    numero = f"<b>{_esc(definicao.numero)}.</b> " if definicao.numero else ""
    rubrica = f"<i>{_esc(definicao.rubrica)}</i> " if definicao.rubrica else ""
    return (
        f"<li>{numero}{rubrica}{definicao.content_html}"
        f"{_exemplos_html(definicao)}{_notas_html(definicao.notas)}</li>"
    )


def _locucao_li(locucao: Locucao) -> str:
    rubrica = f" <i>{_esc(locucao.rubrica)}</i>" if locucao.rubrica else ""
    corpo = "; ".join(
        f"{definicao.content_html}{_exemplos_html(definicao)}{_notas_html(definicao.notas)}"
        for definicao in locucao.definicoes
    )
    return f"<li><b>{_esc(locucao.expression)}</b>{rubrica}: {corpo}{_notas_html(locucao.notas)}</li>"


def _secao_verbete(lemma: str, verbete: Verbete, numero_secao: int | None) -> str:
    partes: list[str] = []
    cabecalho: list[str] = []
    if numero_secao is not None:
        cabecalho.append(f"<b>{numero_secao}.</b>")
    if verbete.lemma_stylized and verbete.lemma_stylized != lemma:
        cabecalho.append(f"<b>{_esc(verbete.lemma_stylized)}</b>")
    if verbete.word_class_summary:
        cabecalho.append(f"<i>{_esc(_classe_legivel(verbete.word_class_summary))}</i>")
    if verbete.ipa:
        cabecalho.append(f"[{_esc(verbete.ipa)}]")
    if cabecalho:
        partes.append("<p>" + " ".join(cabecalho) + "</p>")
    if verbete.etymology_html:
        partes.append(f"<p><small>Etim.: {verbete.etymology_html}</small></p>")

    for bloco in verbete.blocos:
        if bloco.classe:
            partes.append(f"<p><i>{_esc(bloco.classe)}</i></p>")
        if bloco.intro_text:
            partes.append(f"<p>{_esc(bloco.intro_text)}</p>")
        if bloco.definicoes:
            partes.append(
                "<ul>" + "".join(_definicao_li(d) for d in bloco.definicoes) + "</ul>"
            )

    if verbete.locucoes:
        partes.append(
            "<p><u>Locuções</u></p><ul>"
            + "".join(_locucao_li(loc) for loc in verbete.locucoes)
            + "</ul>"
        )

    if verbete.regencias:
        linhas = []
        for regencia in verbete.regencias:
            segmentos = []
            if regencia.sense:
                segmentos.append(f"<b>{regencia.sense}.</b>")
            if regencia.transitivity:
                segmentos.append(_esc(regencia.transitivity))
            if regencia.prepositions:
                segmentos.append(f"(prep.: {_esc(regencia.prepositions)})")
            if regencia.observation:
                segmentos.append(f"<small>{_esc(regencia.observation)}</small>")
            linhas.append("<li>" + " ".join(segmentos) + "</li>")
        partes.append("<p><u>Regência (Luft)</u></p><ul>" + "".join(linhas) + "</ul>")

    for nota in verbete.notas:
        partes.append(f"<p><small>[Nota: {nota.content_html}]</small></p>")

    return "".join(partes)


def renderizar_artigo(
    lemma: str,
    verbetes: Sequence[Verbete],
    advertir: Callable[[str], None] | None = None,
) -> str:
    """Artigo HTML integral do lema, com homônimos fundidos em seções numeradas (RF-01/RF-04)."""
    partes = [f"<b>{_esc(lemma)}</b>"]
    varios = len(verbetes) > 1
    for n, verbete in enumerate(verbetes, start=1):
        partes.append(_secao_verbete(lemma, verbete, n if varios else None))
    artigo = "".join(partes)
    if advertir and len(artigo.encode("utf-8")) > LIMITE_ADVERTENCIA_BYTES:
        advertir(
            f"artigo acima de 1 MB: lemma={lemma} bytes={len(artigo.encode('utf-8'))}"
        )
    return artigo
