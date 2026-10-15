"""Conferência com o código de busca do próprio Readest (RF-06, D-13, D-14).

Obtém, pelo commit fixado em `conferencia_readest/fonte-readest.json`, os dois
arquivos do leitor StarDict do Readest, confere o SHA-256 do original e do
reescrito, guarda-os em cache local fora do git e instala o `fflate` travado no
lockfile. Depois executa `conferir.ts` no Node, por subprocesso, sobre o
artefato no diretório de preparo. Com o cache íntegro, nenhuma chamada de rede.

Erros de ambiente viram `AmbienteConferenciaError` com mensagem acionável
(exit code 2); reprovação é veredito, não exceção.
"""

import hashlib
import json
import logging
import re
import subprocess
import urllib.request
from collections.abc import Callable
from pathlib import Path

from aurelio_pipeline.erros import AmbienteConferenciaError

log = logging.getLogger("aurelio.conferencia")

PIPELINE_DIR = Path(__file__).resolve().parents[3]
DIR_CONFERENCIA = PIPELINE_DIR / "conferencia_readest"
URL_BRUTA = "https://raw.githubusercontent.com/{repositorio}/{commit}/{base}{arquivo}"
TIMEOUT_DOWNLOAD_S = 30
TIMEOUT_NPM_S = 300
TIMEOUT_ROTEIRO_S = 600
INSTALAR_NODE = "instale com `brew install node`"


def versao_suficiente(saida: str, minimo: str) -> bool:
    """`v26.10.0` contra `22.18`: compara maior e menor."""
    encontrada = re.match(r"v?(\d+)\.(\d+)", saida.strip())
    if encontrada is None:
        return False
    exigida = tuple(int(parte) for parte in minimo.split(".")[:2])
    return (int(encontrada[1]), int(encontrada[2])) >= exigida


def _sha256(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def _baixar_http(url: str, timeout: float) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as resposta:  # noqa: S310 — URL fixa do GitHub
        if resposta.status != 200:
            raise OSError(f"HTTP {resposta.status}")
        return resposta.read()


def _cauda(texto: str, linhas: int = 5) -> str:
    return " | ".join((texto or "").strip().splitlines()[-linhas:])


class ConferenciaReadest:
    def __init__(
        self,
        diretorio: Path = DIR_CONFERENCIA,
        *,
        baixar: Callable[[str, float], bytes] = _baixar_http,
        executar: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    ):
        self.diretorio = Path(diretorio)
        self._baixar = baixar
        self._executar = executar
        caminho_fonte = self.diretorio / "fonte-readest.json"
        try:
            self.fonte = json.loads(caminho_fonte.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise AmbienteConferenciaError(
                f"fonte fixada ilegível em {caminho_fonte}: {exc} — restaure-a do git"
            ) from exc

    @property
    def cache(self) -> Path:
        return self.diretorio / ".cache" / self.fonte["tag"]

    # ------------------------------------------------------------ ambiente

    def verificar_ambiente(self) -> dict[str, str]:
        """Node no mínimo fixado e npm presentes (D-14)."""
        minimo = self.fonte["node_minimo"]
        try:
            node = self._executar(
                ["node", "--version"], capture_output=True, text=True, timeout=30
            )
        except OSError as exc:
            raise AmbienteConferenciaError(
                f"Node.js não encontrado no PATH ({exc}); a conferência com o código do "
                f"Readest exige Node {minimo} ou posterior — {INSTALAR_NODE}"
            ) from exc
        versao = node.stdout.strip()
        if node.returncode != 0 or not versao_suficiente(versao, minimo):
            raise AmbienteConferenciaError(
                f"Node.js {versao or '(versão ilegível)'} abaixo do mínimo {minimo} exigido "
                f"pela conferência com o código do Readest — {INSTALAR_NODE}"
            )
        try:
            npm = self._executar(
                ["npm", "--version"], capture_output=True, text=True, timeout=30
            )
        except OSError as exc:
            raise AmbienteConferenciaError(
                f"npm não encontrado no PATH ({exc}); ele acompanha o Node — {INSTALAR_NODE}"
            ) from exc
        return {"node": versao, "npm": npm.stdout.strip()}

    def preparar(self) -> Path:
        """Ambiente, cache do código do Readest e `node_modules`, nessa ordem; idempotente."""
        ambiente = self.verificar_ambiente()
        if not self._cache_valido():
            self._obter()
        if not self._modulos_validos():
            self._npm_ci()
        log.info(
            "conferencia_pronta node=%s npm=%s readest=%s cache=%s",
            ambiente["node"],
            ambiente["npm"],
            self.fonte["tag"],
            self.cache,
        )
        return self.cache

    # --------------------------------------------------------------- cache

    def _marcador_esperado(self) -> dict:
        return {
            "originais": self.fonte["arquivos"],
            "reescritos": self.fonte["arquivos_reescritos"],
        }

    def _cache_valido(self) -> bool:
        marcador = self.cache / ".pronto"
        try:
            if json.loads(marcador.read_text(encoding="utf-8")) != self._marcador_esperado():
                return False
            return all(
                _sha256((self.cache / nome).read_bytes()) == sha
                for nome, sha in self.fonte["arquivos_reescritos"].items()
            )
        except (OSError, ValueError):
            return False

    def _obter(self) -> None:
        conteudos: dict[str, str] = {}
        for nome, sha_esperado in self.fonte["arquivos"].items():
            url = URL_BRUTA.format(
                repositorio=self.fonte["repositorio"],
                commit=self.fonte["commit"],
                base=self.fonte["base"],
                arquivo=nome,
            )
            log.info("conferencia_download url=%s", url)
            try:
                dados = self._baixar(url, TIMEOUT_DOWNLOAD_S)
            except Exception as exc:  # noqa: BLE001 — toda falha de obtenção é de ambiente
                raise AmbienteConferenciaError(
                    f"falha ao obter {url}: {exc} — conecte-se à rede e repita; "
                    "depois disso o cache dispensa a rede"
                ) from exc
            sha_obtido = _sha256(dados)
            if sha_obtido != sha_esperado:
                raise AmbienteConferenciaError(
                    f"{nome}: hash divergente do fixado em fonte-readest.json "
                    f"(esperado={sha_esperado} obtido={sha_obtido}); o cache não foi gravado — "
                    "não contorne: confira o commit e os hashes"
                )
            conteudos[nome] = dados.decode("utf-8")

        for reescrita in self.fonte["reescritas"]:
            nome = reescrita["arquivo"]
            ocorrencias = conteudos[nome].count(reescrita["de"])
            if ocorrencias != 1:
                raise AmbienteConferenciaError(
                    f"{nome}: a reescrita de {reescrita['de']!r} encontrou {ocorrencias} "
                    "ocorrência(s), esperada exatamente 1 — a versão fixada do Readest mudou?"
                )
            conteudos[nome] = conteudos[nome].replace(reescrita["de"], reescrita["para"])

        for nome, texto in conteudos.items():
            sha_obtido = _sha256(texto.encode("utf-8"))
            sha_esperado = self.fonte["arquivos_reescritos"][nome]
            if sha_obtido != sha_esperado:
                raise AmbienteConferenciaError(
                    f"{nome}: hash do arquivo reescrito divergente (esperado={sha_esperado} "
                    f"obtido={sha_obtido}) — confira as reescritas em fonte-readest.json"
                )

        self.cache.mkdir(parents=True, exist_ok=True)
        (self.cache / ".pronto").unlink(missing_ok=True)
        for nome, texto in conteudos.items():
            (self.cache / nome).write_text(texto, encoding="utf-8")
        (self.cache / ".pronto").write_text(
            json.dumps(self._marcador_esperado(), indent=2), encoding="utf-8"
        )

    # ----------------------------------------------------------------- npm

    def _modulos_validos(self) -> bool:
        pacote = self.diretorio / "node_modules" / "fflate" / "package.json"
        try:
            return json.loads(pacote.read_text(encoding="utf-8"))["version"] == self.fonte["fflate"]
        except (OSError, ValueError, KeyError):
            return False

    def _npm_ci(self) -> None:
        log.info("conferencia_npm_ci dir=%s", self.diretorio)
        try:
            processo = self._executar(
                ["npm", "ci", "--no-audit", "--no-fund"],
                cwd=self.diretorio,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_NPM_S,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AmbienteConferenciaError(f"npm ci não executou: {exc}") from exc
        if processo.returncode != 0:
            raise AmbienteConferenciaError(
                f"npm ci falhou com código {processo.returncode}: {_cauda(processo.stderr)} — "
                "sem rede na primeira instalação? conecte-se e repita"
            )
        if not self._modulos_validos():
            raise AmbienteConferenciaError(
                f"npm ci terminou sem instalar fflate {self.fonte['fflate']} — "
                "confira package-lock.json"
            )

    # ------------------------------------------------------------ execução

    def conferir(
        self,
        artefato: Path,
        basename: str,
        expectativa: Path,
        timeout: float = TIMEOUT_ROTEIRO_S,
    ) -> dict:
        """Executa `conferir.ts`; devolve o JSON do roteiro com o veredito final."""
        comando = ["node", "conferir.ts", str(artefato), basename, str(expectativa)]
        try:
            processo = self._executar(
                comando,
                cwd=self.diretorio,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return {
                "veredito": "reprovado",
                "causa": f"a conferência excedeu o tempo limite de {timeout:.0f} s",
            }
        except OSError as exc:
            raise AmbienteConferenciaError(
                f"Node.js não executou o roteiro da conferência ({exc}) — {INSTALAR_NODE}"
            ) from exc
        if processo.returncode not in (0, 1):
            raise AmbienteConferenciaError(
                f"o roteiro da conferência terminou com código {processo.returncode}: "
                f"{_cauda(processo.stderr)}"
            )
        try:
            dados = json.loads(processo.stdout)
        except ValueError as exc:
            raise AmbienteConferenciaError(
                f"a saída do roteiro da conferência não é JSON ({exc}): {_cauda(processo.stdout)}"
            ) from exc
        aprovado = processo.returncode == 0 and dados.get("veredito") == "aprovado"
        dados["veredito"] = "aprovado" if aprovado else "reprovado"
        log.info(
            "conferencia veredito=%s chaves_ok=%s chaves_falha=%s trechos_ok=%s "
            "trechos_falha=%s duracao_s=%s",
            dados["veredito"],
            dados.get("chaves_ok"),
            dados.get("chaves_falha"),
            dados.get("trechos_ok"),
            dados.get("trechos_falha"),
            dados.get("duracao_s"),
        )
        return dados
