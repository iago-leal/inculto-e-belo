"""Contratos internos entre camadas (data-delta.md §3; specs §9 dos componentes)."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Exemplo:
    kind: str  # 'editor' | 'citation' (RB-07: distinção editorial preservada)
    content_html: str
    content_text: str


@dataclass(frozen=True)
class Nota:
    content_html: str
    content_text: str


@dataclass(frozen=True)
class Definicao:
    numero: str | None
    rubrica: str | None
    content_html: str
    content_text: str
    exemplos: tuple[Exemplo, ...] = ()
    notas: tuple[Nota, ...] = ()


@dataclass(frozen=True)
class BlocoClasse:
    classe: str | None
    intro_text: str | None
    definicoes: tuple[Definicao, ...] = ()


@dataclass(frozen=True)
class Locucao:
    expression: str
    rubrica: str | None
    definicoes: tuple[Definicao, ...] = ()
    notas: tuple[Nota, ...] = ()


@dataclass(frozen=True)
class Regencia:
    sense: int | None
    transitivity: str | None
    prepositions: str | None
    observation: str | None


@dataclass(frozen=True)
class Verbete:
    id: int
    lemma: str
    lemma_stylized: str | None
    homonym: int | None
    word_class_summary: str | None
    ipa: str | None
    etymology_html: str | None
    blocos: tuple[BlocoClasse, ...] = ()
    locucoes: tuple[Locucao, ...] = ()
    notas: tuple[Nota, ...] = ()
    regencias: tuple[Regencia, ...] = ()


@dataclass
class RelatorioCobertura:
    entrada_linhas: dict[str, int]
    entrada_formas: dict[str, int]
    gravadas: int
    descartes: dict[str, int]
    orfas: list[str]
    headwords_com_formas: int

    def to_dict(self) -> dict:
        return {
            "entrada_linhas": dict(self.entrada_linhas),
            "entrada_formas": dict(self.entrada_formas),
            "gravadas": self.gravadas,
            "descartes": dict(self.descartes),
            "orfas": list(self.orfas),
            "headwords_com_formas": self.headwords_com_formas,
        }


@dataclass
class ResultadoBuild:
    headwords: int
    sinonimos: int
    duracao_s: float
    arquivos: dict[str, int] = field(default_factory=dict)


# --- alvo Readest (feature 003; data-delta.md §4) ----------------------------

DESTINOS_READEST = ("idx-lema", "idx-forma-combinada", "idx-forma-direta", "syn")


@dataclass(frozen=True)
class PaginaReadest:
    """Uma chave pesquisável do alvo Readest e a página que ela abre.

    chave: comparação do Readest (minúsculas); grafia: o que o índice grava;
    lemas: sequência de artigos na ordem de exibição (RN-04); destino: onde a
    chave entra no índice (D-09).
    """

    chave: str
    grafia: str
    lemas: tuple[str, ...]
    destino: str

    @property
    def combinada(self) -> bool:
        return len(self.lemas) > 1


@dataclass
class PlanoPaginas:
    """Saída do agrupamento: páginas em ordem de índice (comparação do Readest)."""

    paginas: list[PaginaReadest]

    def do_idx(self) -> list[PaginaReadest]:
        return [p for p in self.paginas if p.destino != "syn"]

    def do_syn(self) -> list[PaginaReadest]:
        return [p for p in self.paginas if p.destino == "syn"]


@dataclass
class RelatorioAgrupamento:
    chaves: int
    paginas_simples: int
    paginas_combinadas: int
    sequencias_distintas: int
    descartes_sem_letra: int
    formas_descartadas: list[dict[str, str]]
    artigos_por_pagina: dict[int, int]
    indice: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "chaves": self.chaves,
            "paginas_simples": self.paginas_simples,
            "paginas_combinadas": self.paginas_combinadas,
            "sequencias_distintas": self.sequencias_distintas,
            "descartes_sem_letra": self.descartes_sem_letra,
            "formas_descartadas": [dict(f) for f in self.formas_descartadas],
            "artigos_por_pagina": {
                str(n): total for n, total in sorted(self.artigos_por_pagina.items())
            },
            "indice": dict(self.indice),
        }


@dataclass
class ResultadoEscritaReadest:
    idx: int
    syn: int
    trechos: int
    bytes_corpo: int
    impressao_digital: str
    preparo: Path
    artefato: Path
    expectativa: Path
    duracao_s: float
    arquivos: dict[str, int] = field(default_factory=dict)
