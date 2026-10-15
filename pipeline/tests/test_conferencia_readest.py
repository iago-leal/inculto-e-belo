"""Testes da infraestrutura da conferência com o código do Readest (T009; RF-06, D-13, D-14).

Sem rede: o download e os subprocessos são injetados. O teste de integração
roda o roteiro real (`conferir.ts`) quando há Node e o cache já foi preparado;
caso contrário, é pulado.
"""

import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from aurelio_pipeline.erros import AmbienteConferenciaError
from aurelio_pipeline.infra.conferencia_readest import (
    DIR_CONFERENCIA,
    ConferenciaReadest,
    versao_suficiente,
)

ORIGINAL_A = "import { b } from './b';\nexport const a = b;\n"
ORIGINAL_B = "export class B {\n  constructor(private readonly x: number) {}\n}\nexport const b = 1;\n"
REESCRITAS = [
    {"arquivo": "a.ts", "de": "'./b'", "para": "'./b.ts'"},
    {
        "arquivo": "b.ts",
        "de": "  constructor(private readonly x: number) {}\n",
        "para": "  private readonly x: number;\n  constructor(x: number) {\n    this.x = x;\n  }\n",
    },
]


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _reescrito(nome: str, texto: str) -> str:
    for r in REESCRITAS:
        if r["arquivo"] == nome:
            texto = texto.replace(r["de"], r["para"])
    return texto


ORIGINAIS = {"a.ts": ORIGINAL_A, "b.ts": ORIGINAL_B}


def _diretorio(tmp_path: Path, originais=ORIGINAIS) -> Path:
    diretorio = tmp_path / "conferencia"
    diretorio.mkdir()
    fonte = {
        "repositorio": "readest/readest",
        "tag": "v0.0.1",
        "commit": "abc123",
        "base": "src/",
        "arquivos": {nome: _sha(texto) for nome, texto in originais.items()},
        "reescritas": REESCRITAS,
        "arquivos_reescritos": {
            nome: _sha(_reescrito(nome, texto)) for nome, texto in originais.items()
        },
        "fflate": "0.8.3",
        "node_minimo": "22.18",
    }
    (diretorio / "fonte-readest.json").write_text(json.dumps(fonte), encoding="utf-8")
    return diretorio


class Processos:
    """Subprocessos falsos: node, npm e o roteiro, com registro das chamadas."""

    def __init__(self, node="v26.10.0", npm="11.19.1", roteiro=None):
        self.node, self.npm, self.roteiro = node, npm, roteiro
        self.chamadas: list[list[str]] = []

    def __call__(self, comando, **kwargs):
        self.chamadas.append(list(comando))
        programa = comando[0]
        if programa == "node" and comando[1] == "--version":
            if self.node is None:
                raise FileNotFoundError("node")
            return subprocess.CompletedProcess(comando, 0, self.node + "\n", "")
        if programa == "npm" and comando[1] == "--version":
            if self.npm is None:
                raise FileNotFoundError("npm")
            return subprocess.CompletedProcess(comando, 0, self.npm + "\n", "")
        if programa == "npm" and comando[1] == "ci":
            modulo = Path(kwargs["cwd"]) / "node_modules" / "fflate"
            modulo.mkdir(parents=True)
            (modulo / "package.json").write_text(json.dumps({"version": "0.8.3"}))
            return subprocess.CompletedProcess(comando, 0, "", "")
        if programa == "node":
            if isinstance(self.roteiro, BaseException):
                raise self.roteiro
            return self.roteiro
        raise AssertionError(f"comando inesperado: {comando}")


def _baixar_de(originais):
    urls = []

    def baixar(url, timeout):
        urls.append(url)
        return originais[url.rsplit("/", 1)[1]].encode("utf-8")

    baixar.urls = urls
    return baixar


def _sem_rede(url, timeout):
    raise AssertionError(f"rede usada indevidamente: {url}")


class TestAmbiente:
    @pytest.mark.parametrize(
        ("saida", "esperado"),
        [("v22.18.0", True), ("v26.10.0", True), ("v22.17.9", False), ("v20.19.0", False), ("lixo", False)],
    )
    def test_versao_suficiente(self, saida, esperado):
        assert versao_suficiente(saida, "22.18") is esperado

    def test_node_abaixo_do_minimo(self, tmp_path):
        conferencia = ConferenciaReadest(
            _diretorio(tmp_path), baixar=_sem_rede, executar=Processos(node="v22.17.0")
        )
        with pytest.raises(AmbienteConferenciaError, match=r"22\.17\.0.*22\.18"):
            conferencia.verificar_ambiente()

    def test_node_ausente(self, tmp_path):
        conferencia = ConferenciaReadest(
            _diretorio(tmp_path), baixar=_sem_rede, executar=Processos(node=None)
        )
        with pytest.raises(AmbienteConferenciaError, match="brew install node"):
            conferencia.verificar_ambiente()

    def test_npm_ausente(self, tmp_path):
        conferencia = ConferenciaReadest(
            _diretorio(tmp_path), baixar=_sem_rede, executar=Processos(npm=None)
        )
        with pytest.raises(AmbienteConferenciaError, match="npm"):
            conferencia.verificar_ambiente()


class TestCache:
    def test_preparar_baixa_pelo_commit_reescreve_e_marca(self, tmp_path):
        diretorio = _diretorio(tmp_path)
        baixar = _baixar_de(ORIGINAIS)
        processos = Processos()
        cache = ConferenciaReadest(diretorio, baixar=baixar, executar=processos).preparar()
        assert cache == diretorio / ".cache" / "v0.0.1"
        assert all("/readest/readest/abc123/src/" in url for url in baixar.urls)
        assert (cache / "a.ts").read_text() == _reescrito("a.ts", ORIGINAL_A)
        assert "private readonly x: number;\n" in (cache / "b.ts").read_text()
        assert (cache / ".pronto").exists()
        assert ["npm", "ci", "--no-audit", "--no-fund"] in processos.chamadas

    def test_cache_pronto_dispensa_a_rede(self, tmp_path):
        diretorio = _diretorio(tmp_path)
        ConferenciaReadest(diretorio, baixar=_baixar_de(ORIGINAIS), executar=Processos()).preparar()
        processos = Processos()
        ConferenciaReadest(diretorio, baixar=_sem_rede, executar=processos).preparar()
        assert not any(c[:2] == ["npm", "ci"] for c in processos.chamadas)

    def test_hash_divergente_nao_grava_cache(self, tmp_path):
        diretorio = _diretorio(tmp_path)
        adulterados = dict(ORIGINAIS, **{"b.ts": ORIGINAL_B + "// alterado\n"})
        conferencia = ConferenciaReadest(
            diretorio, baixar=_baixar_de(adulterados), executar=Processos()
        )
        with pytest.raises(AmbienteConferenciaError, match=r"b\.ts.*hash"):
            conferencia.preparar()
        cache = diretorio / ".cache" / "v0.0.1"
        assert not (cache / ".pronto").exists()
        assert not (cache / "b.ts").exists()

    def test_falha_http_e_acionavel(self, tmp_path):
        def baixar(url, timeout):
            raise OSError("sem rede")

        conferencia = ConferenciaReadest(_diretorio(tmp_path), baixar=baixar, executar=Processos())
        with pytest.raises(AmbienteConferenciaError, match="conecte-se à rede"):
            conferencia.preparar()

    @pytest.mark.parametrize("ocorrencias", [0, 2])
    def test_reescrita_exige_exatamente_uma_ocorrencia(self, tmp_path, ocorrencias):
        original_a = "import { b } from './c';\n" if ocorrencias == 0 else (
            "import { b } from './b';\nimport { c } from './b';\n"
        )
        originais = dict(ORIGINAIS, **{"a.ts": original_a})
        diretorio = _diretorio(tmp_path, originais)
        conferencia = ConferenciaReadest(
            diretorio, baixar=_baixar_de(originais), executar=Processos()
        )
        with pytest.raises(AmbienteConferenciaError, match=f"{ocorrencias} ocorrência"):
            conferencia.preparar()


class TestExecucao:
    def _conferir(self, tmp_path, roteiro):
        diretorio = _diretorio(tmp_path)
        conferencia = ConferenciaReadest(
            diretorio, baixar=_baixar_de(ORIGINAIS), executar=Processos(roteiro=roteiro)
        )
        return conferencia.conferir(tmp_path / "artefato", "aurelio-readest", tmp_path / "exp.tsv")

    def test_aprovado(self, tmp_path):
        saida = json.dumps({"veredito": "aprovado", "chaves_ok": 3})
        resultado = self._conferir(tmp_path, subprocess.CompletedProcess([], 0, saida, ""))
        assert resultado["veredito"] == "aprovado"
        assert resultado["chaves_ok"] == 3

    def test_reprovado(self, tmp_path):
        saida = json.dumps({"veredito": "reprovado", "falhas": [{"chave": "foi"}]})
        resultado = self._conferir(tmp_path, subprocess.CompletedProcess([], 1, saida, ""))
        assert resultado["veredito"] == "reprovado"

    def test_falha_de_execucao(self, tmp_path):
        with pytest.raises(AmbienteConferenciaError, match="código 2"):
            self._conferir(tmp_path, subprocess.CompletedProcess([], 2, "", "TypeError: x"))

    def test_saida_ilegivel(self, tmp_path):
        with pytest.raises(AmbienteConferenciaError, match="JSON"):
            self._conferir(tmp_path, subprocess.CompletedProcess([], 0, "não é json", ""))

    def test_timeout_vira_reprovacao_com_causa(self, tmp_path):
        resultado = self._conferir(tmp_path, subprocess.TimeoutExpired(["node"], 600))
        assert resultado["veredito"] == "reprovado"
        assert "tempo" in resultado["causa"]


def _cache_real_pronto() -> bool:
    if shutil.which("node") is None:
        return False
    fonte = json.loads((DIR_CONFERENCIA / "fonte-readest.json").read_text(encoding="utf-8"))
    return (DIR_CONFERENCIA / ".cache" / fonte["tag"] / ".pronto").exists() and (
        DIR_CONFERENCIA / "node_modules" / "fflate"
    ).exists()


@pytest.mark.integracao
@pytest.mark.skipif(not _cache_real_pronto(), reason="sem Node ou sem cache da conferência")
class TestIntegracaoComReadest:
    def _artefato(self, tmp_path):
        from aurelio_pipeline.dominio.agrupamento_readest import agrupar
        from aurelio_pipeline.infra.escrita_readest import EscritorReadest

        headwords = ["a", "A", "à", "ir", "ser", "cantar", "vir", "ver"]
        mapa = {"ir": ["foi"], "ser": ["foi", "era"], "cantar": ["cantávamos"],
                "vir": ["vieram"], "ver": ["vir"]}
        plano, _ = agrupar(headwords, mapa, frozenset({"ser"}))
        artigos = {
            lema: f"<b>{html.escape(lema, quote=False)}</b><p>{'x' * 70000}</p>"
            for lema in headwords
        }
        return EscritorReadest(tmp_path / "dist").escrever(plano, artigos, data="2026-07-03")

    def test_roteiro_real_aprova_artefato_correto(self, tmp_path):
        resultado = self._artefato(tmp_path)
        saida = ConferenciaReadest().conferir(
            resultado.artefato, "aurelio-readest", resultado.expectativa
        )
        assert saida["veredito"] == "aprovado", saida
        assert saida["chaves_falha"] == 0
        assert saida["chaves_ok"] == resultado.idx + resultado.syn

    def test_roteiro_real_reprova_expectativa_divergente(self, tmp_path):
        resultado = self._artefato(tmp_path)
        linhas = resultado.expectativa.read_text(encoding="utf-8").splitlines()
        grafia, offset, tamanho = linhas[0].split("\t")
        linhas[0] = f"{grafia}\t{int(offset) + 1}\t{tamanho}"
        resultado.expectativa.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        saida = ConferenciaReadest().conferir(
            resultado.artefato, "aurelio-readest", resultado.expectativa
        )
        assert saida["veredito"] == "reprovado"
        assert saida["chaves_falha"] == 1
        assert saida["falhas"][0]["chave"] == grafia
