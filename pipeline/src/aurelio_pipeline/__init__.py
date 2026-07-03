"""Pipeline de produção do dicionário StarDict do Aurélio.

Camadas (specs em _reversa_sdd/sdd/):
  infra/repositorio       — ingestao-aurelio (único dono do SQL; banco somente-leitura)
  dominio/indice_flexoes  — indice-de-flexoes (mapeamento forma→headword, puro)
  dominio/renderizacao    — conversao-formato, metade pura (Verbete → HTML)
  infra/escrita_stardict  — conversao-formato, adaptador PyGlossary
  validacao/              — validacao-paridade (parser próprio em stdlib)
"""

__version__ = "1.0.0"
