"""Contratos internos entre camadas (data-delta.md §3; specs §9 dos componentes)."""

from dataclasses import dataclass, field


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
