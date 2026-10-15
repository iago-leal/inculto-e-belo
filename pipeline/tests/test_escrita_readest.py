"""Testes do escritor do alvo Readest e da promoção condicionada (T007; D-01, D-08 a D-11, D-15, D-16).

O artefato é lido de volta pelo LeitorStarDict próprio do projeto; os artigos
são HTML sintético no mesmo formato de abertura do renderizador (`<b>lema</b>`).
"""

import hashlib
import html
import re

import pytest

from aurelio_pipeline.dominio.agrupamento_readest import agrupar, ordem_readest
from aurelio_pipeline.dominio.modelos import PaginaReadest, PlanoPaginas
from aurelio_pipeline.erros import FalhaGeracaoError
from aurelio_pipeline.infra.escrita_readest import (
    BASENAME,
    BOOKNAME,
    EscritorReadest,
    descartar,
    promover,
    reprovar,
)
from aurelio_pipeline.validacao.leitor_stardict import LeitorStarDict

HEADWORDS = [
    "era", "ser", "erar", "ir", "fossar", "vir", "ver", "a", "A", "bretão",
    "à", "cantar", "&",
]
MAPA = {
    "ser": ["era", "foi", "fosse", "é", "fora"],
    "erar": ["era"],
    "ir": ["foi", "fosse", "vá", "fora"],
    "fossar": ["fosse"],
    "vir": ["vieram"],
    "ver": ["vir", "viram"],
    "bretão": ["a"],
    "A": ["As"],
    "cantar": ["cantávamos"],
}
FREQUENTES = frozenset({"ser", "ir", "ver"})
DATA = "2026-07-03"


def artigo(lema: str) -> str:
    return f"<b>{html.escape(lema, quote=False)}</b><p>definição de {html.escape(lema, quote=False)}</p>"


ARTIGOS = {lema: artigo(lema) for lema in HEADWORDS}


@pytest.fixture()
def plano():
    plano, _ = agrupar(HEADWORDS, MAPA, FREQUENTES)
    return plano


@pytest.fixture()
def escrito(tmp_path, plano):
    resultado = EscritorReadest(tmp_path / "dist").escrever(plano, ARTIGOS, data=DATA)
    return resultado, LeitorStarDict(resultado.artefato)


def _entrada(leitor, chave):
    for i, (palavra, offset, tamanho) in enumerate(leitor.entradas):
        if palavra.lower() == chave:
            return i, offset, tamanho
    return None


def _sinonimo(leitor, chave):
    for forma, indice in leitor.sinonimos:
        if forma.lower() == chave:
            return indice
    return None


def _texto(leitor, offset, tamanho):
    return leitor._dict[offset : offset + tamanho].decode("utf-8")


class TestArtefato:
    def test_quatro_arquivos_e_contagens(self, escrito, plano):
        resultado, leitor = escrito
        nomes = sorted(p.name for p in resultado.artefato.iterdir())
        assert nomes == [f"{BASENAME}{s}" for s in (".dict.dz", ".idx", ".ifo", ".syn")]
        assert len(leitor.entradas) == resultado.idx == len(plano.do_idx())
        assert len(leitor.sinonimos) == resultado.syn == len(plano.do_syn())

    def test_indices_estritamente_crescentes_na_ordem_do_readest(self, escrito):
        _, leitor = escrito
        for palavras in (
            [p for p, _, _ in leitor.entradas],
            [f for f, _ in leitor.sinonimos],
        ):
            ordens = [ordem_readest(p) for p in palavras]
            assert all(a < b for a, b in zip(ordens, ordens[1:]))

    def test_pagina_combinada_une_artigos_com_divisor(self, escrito):
        _, leitor = escrito
        _, offset, tamanho = _entrada(leitor, "foi")
        assert _texto(leitor, offset, tamanho) == ARTIGOS["ir"] + "<hr>" + ARTIGOS["ser"]
        _, offset, tamanho = _entrada(leitor, "era")
        assert _texto(leitor, offset, tamanho) == "<hr>".join(
            ARTIGOS[lema] for lema in ("era", "ser", "erar")
        )

    @pytest.mark.parametrize(("forma", "lema", "pagina"), [("vieram", "vir", "vir"), ("as", "A", "a")])
    def test_forma_direta_aponta_sub_trecho_sem_copia(self, escrito, forma, lema, pagina):
        _, leitor = escrito
        _, offset, tamanho = _entrada(leitor, forma)
        _, offset_pagina, tamanho_pagina = _entrada(leitor, pagina)
        assert _texto(leitor, offset, tamanho) == ARTIGOS[lema]
        assert offset_pagina <= offset
        assert offset + tamanho <= offset_pagina + tamanho_pagina

    def test_forma_de_pagina_simples_vai_para_o_syn(self, escrito):
        _, leitor = escrito
        assert _entrada(leitor, "cantávamos") is None
        indice = _sinonimo(leitor, "cantávamos")
        assert leitor.entradas[indice][0] == "cantar"

    def test_sequencia_repetida_gravada_uma_vez(self, escrito):
        _, leitor = escrito
        assert _entrada(leitor, "foi")[1:] == _entrada(leitor, "fora")[1:]

    def test_artigo_gravado_uma_vez_por_sequencia_distinta(self, escrito, plano):
        _, leitor = escrito
        corpo = leitor._dict.decode("utf-8")
        sequencias = {p.lemas for p in plano.paginas if p.destino.startswith("idx-") and p.destino != "idx-forma-direta"}
        for lema in ("cantar", "ir", "ser", "vir", "A"):
            esperado = sum(1 for seq in sequencias if lema in seq)
            assert corpo.count(ARTIGOS[lema]) == esperado, lema
        # acesso isolado não copia: «cantar» e «vir» só existem na própria página
        assert corpo.count(ARTIGOS["cantar"]) == corpo.count(ARTIGOS["vir"]) == 1


class TestIfo:
    def test_campos_deterministicos(self, escrito):
        resultado, leitor = escrito
        texto = (resultado.artefato / f"{BASENAME}.ifo").read_text(encoding="utf-8")
        assert texto.splitlines()[0] == "StarDict's dict ifo file"
        assert texto.splitlines()[1] == "version=3.0.0"
        assert leitor.ifo["bookname"] == BOOKNAME == "Aurélio (uso pessoal, Readest)"
        assert leitor.ifo["sametypesequence"] == "h"
        assert leitor.ifo["date"] == DATA
        assert int(leitor.ifo["wordcount"]) == len(leitor.entradas)
        assert int(leitor.ifo["synwordcount"]) == len(leitor.sinonimos)
        assert int(leitor.ifo["idxfilesize"]) == leitor.idx_bytes

    def test_descricao_traz_impressao_digital_do_conteudo(self, escrito):
        resultado, leitor = escrito
        base = resultado.artefato / BASENAME
        hasher = hashlib.sha256()
        for parte in (
            base.with_suffix(".idx").read_bytes(),
            base.with_suffix(".syn").read_bytes(),
            leitor._dict,
        ):
            hasher.update(parte)
        esperado = hasher.hexdigest()[:16]
        assert re.search(rf"conteúdo {esperado}$", leitor.ifo["description"])
        assert resultado.impressao_digital == esperado


class TestCorpo:
    def test_dictzip_com_campo_ra(self, escrito):
        resultado, _ = escrito
        dz = (resultado.artefato / f"{BASENAME}.dict.dz").read_bytes()
        assert dz[:2] == b"\x1f\x8b"
        assert dz[3] & 0x04, "sem FEXTRA"
        assert dz[12:14] == b"RA"

    def test_duas_escritas_produzem_bytes_identicos(self, tmp_path, plano):
        r1 = EscritorReadest(tmp_path / "d1").escrever(plano, ARTIGOS, data=DATA)
        r2 = EscritorReadest(tmp_path / "d2").escrever(plano, ARTIGOS, data=DATA)
        for sufixo in (".ifo", ".idx", ".syn", ".dict.dz"):
            nome = f"{BASENAME}{sufixo}"
            assert (r1.artefato / nome).read_bytes() == (r2.artefato / nome).read_bytes(), nome


class TestExpectativa:
    def test_uma_linha_por_chave_com_o_trecho_esperado(self, escrito):
        resultado, leitor = escrito
        linhas = resultado.expectativa.read_text(encoding="utf-8").splitlines()
        assert len(linhas) == len(leitor.entradas) + len(leitor.sinonimos)
        esperado = {}
        for linha in linhas:
            grafia, offset, tamanho = linha.split("\t")
            esperado[grafia.lower()] = (int(offset), int(tamanho))
        indice = _sinonimo(leitor, "cantávamos")
        assert esperado["cantávamos"] == tuple(leitor.entradas[indice][1:])
        assert esperado["vieram"] == _entrada(leitor, "vieram")[1:]


class TestErros:
    def test_lema_sem_artigo_renderizado(self, tmp_path, plano):
        artigos = dict(ARTIGOS)
        del artigos["cantar"]
        with pytest.raises(FalhaGeracaoError, match="cantar"):
            EscritorReadest(tmp_path / "dist").escrever(plano, artigos, data=DATA)

    def test_grafia_com_tabulacao(self, tmp_path):
        plano = PlanoPaginas([PaginaReadest("a\tb", "a\tb", ("a\tb",), "idx-lema")])
        with pytest.raises(FalhaGeracaoError, match="tabulação"):
            EscritorReadest(tmp_path / "dist").escrever(plano, {"a\tb": artigo("ab")}, data=DATA)

    def test_falha_nao_deixa_preparo(self, tmp_path, plano):
        dist = tmp_path / "dist"
        with pytest.raises(FalhaGeracaoError):
            EscritorReadest(dist).escrever(plano, {}, data=DATA)
        assert not list(dist.glob(".readest-preparo-*"))


class TestPromocao:
    def _escrever(self, dist, plano):
        resultado = EscritorReadest(dist).escrever(plano, ARTIGOS, data=DATA)
        (resultado.preparo / "relatorios").mkdir()
        (resultado.preparo / "relatorios" / "validacao-readest.json").write_text("{}")
        return resultado

    def test_aprovado_substitui_a_versao_anterior(self, tmp_path, plano):
        dist = tmp_path / "dist"
        anterior = dist / "readest" / "aurelio-readest"
        anterior.mkdir(parents=True)
        (anterior / "antigo.txt").write_text("versão anterior")
        resultado = self._escrever(dist, plano)
        destino = promover(resultado, dist)
        assert destino == dist / "readest"
        assert sorted(p.name for p in destino.iterdir()) == ["aurelio-readest", "relatorios"]
        assert not (destino / "aurelio-readest" / "antigo.txt").exists()
        assert len(list((destino / "aurelio-readest").iterdir())) == 4
        assert not list(dist.glob(".readest-*"))

    def test_reprovado_preserva_a_versao_aprovada(self, tmp_path, plano):
        dist = tmp_path / "dist"
        aprovada = dist / "readest" / "aurelio-readest"
        aprovada.mkdir(parents=True)
        (aprovada / "aprovado.txt").write_text("aprovada")
        (dist / "readest.reprovado").mkdir()
        (dist / "readest.reprovado" / "velho.txt").write_text("reprovação antiga")
        resultado = self._escrever(dist, plano)
        destino = reprovar(resultado, dist)
        assert destino == dist / "readest.reprovado"
        assert (aprovada / "aprovado.txt").exists()
        assert not (destino / "velho.txt").exists()
        assert (destino / "expectativa-conferencia.tsv").exists()
        assert (destino / "relatorios" / "validacao-readest.json").exists()
        assert not list(dist.glob(".readest-*"))

    def test_descartar_remove_o_preparo(self, tmp_path, plano):
        dist = tmp_path / "dist"
        resultado = self._escrever(dist, plano)
        descartar(resultado)
        assert not resultado.preparo.exists()
