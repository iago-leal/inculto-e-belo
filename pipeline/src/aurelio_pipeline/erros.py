"""Erros nomeados do pipeline (falha barulhenta é contrato: requirements RNF-Confiabilidade)."""


class ErroPipeline(Exception):
    """Base de todos os erros nomeados do pipeline."""


# --- ingestao-aurelio ---------------------------------------------------------


class BancoAusenteError(ErroPipeline):
    """Banco não encontrado no caminho configurado (EC-01 da ingestão)."""


class BancoIndisponivelError(ErroPipeline):
    """Banco bloqueado por outro processo ou falha de abertura (EC-02)."""


class BancoCorrompidoError(ErroPipeline):
    """Arquivo presente mas ilegível como SQLite (EC-06 da ingestão)."""


class EsquemaInvalidoError(ErroPipeline):
    """Tabela ou coluna requerida ausente; a mensagem lista todas as divergências (EC-03)."""


class ContagemDivergenteError(ErroPipeline):
    """Contagem de tabela difere do manifesto de integridade (EC-04 da ingestão)."""


class ManifestoAusenteError(ErroPipeline):
    """manifesto-integridade.json não encontrado ou ilegível."""


# --- indice-de-flexoes --------------------------------------------------------


class FormaAnomalaError(ErroPipeline):
    """Forma vazia ou só espaços nas tabelas de origem (EC-04 do índice)."""


# --- conversao-formato --------------------------------------------------------


class FalhaGeracaoError(ErroPipeline):
    """Falha do PyGlossary ou artefato incompleto após a escrita (EC-03 da conversão, D-05)."""


# --- validacao-paridade -------------------------------------------------------


class ArtefatoAusenteError(ErroPipeline):
    """Diretório do artefato sem um dos arquivos obrigatórios (EC-01 da paridade)."""


class ArtefatoCorrompidoError(ErroPipeline):
    """Estrutura binária inválida no .idx/.syn/.dict.dz (EC-02/EC-03 da paridade)."""
