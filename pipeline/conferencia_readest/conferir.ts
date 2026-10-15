// Conferência do artefato do alvo Readest com o código de busca do próprio Readest
// (feature 003, RF-06, D-13; contrato em interfaces/conferencia-readest.md §4).
//
// Uso: node conferir.ts <dir-artefato> <basename> <expectativa.tsv>
//
// Carrega o artefato com o StarDictReader do Readest (cache preparado pelo
// pipeline em .cache/<tag>/), faz para cada chave da expectativa o que o
// provedor do Readest faz (lookup e, se falhar, resolveSynonym) e compara
// offset e tamanho com o esperado. Depois lê cada trecho distinto pelo leitor
// por blocos do Readest e o compara com a descompressão integral.
//
// Saída: um objeto JSON no stdout. Exit code 0 aprovado, 1 reprovado; qualquer
// outro código é falha de execução. Só sintaxe TypeScript apagável: o Node
// executa este arquivo sem flags.

import { openAsBlob, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { gunzipSync } from 'fflate';

const LIMITE_FALHAS = 50;

interface Falha {
  chave: string;
  esperado: [number, number];
  obtido: [number, number] | null;
}

const aqui = dirname(fileURLToPath(import.meta.url));
const [dirArtefato, basename, caminhoExpectativa] = process.argv.slice(2);
if (!dirArtefato || !basename || !caminhoExpectativa) {
  process.stderr.write('uso: node conferir.ts <dir-artefato> <basename> <expectativa.tsv>\n');
  process.exit(2);
}

const fonte = JSON.parse(readFileSync(join(aqui, 'fonte-readest.json'), 'utf8'));
const cache = join(aqui, '.cache', fonte.tag);
const { StarDictReader } = await import(pathToFileURL(join(cache, 'stardictReader.ts')).href);
const versaoFflate = JSON.parse(
  readFileSync(join(aqui, 'node_modules', 'fflate', 'package.json'), 'utf8'),
).version;

const inicio = performance.now();
const arquivo = (sufixo: string) => join(dirArtefato, `${basename}${sufixo}`);
const leitor = new StarDictReader();
await leitor.load({
  ifo: await openAsBlob(arquivo('.ifo')),
  idx: await openAsBlob(arquivo('.idx')),
  dict: await openAsBlob(arquivo('.dict.dz')),
  syn: await openAsBlob(arquivo('.syn')),
});

const linhas = readFileSync(caminhoExpectativa, 'utf8').split('\n').filter((l) => l.length > 0);
const falhas: Falha[] = [];
let chavesOk = 0;
let chavesFalha = 0;
const trechos = new Map<string, [number, number]>();

for (const linha of linhas) {
  const [chave, offsetTexto, tamanhoTexto] = linha.split('\t');
  const esperado: [number, number] = [Number(offsetTexto), Number(tamanhoTexto)];
  trechos.set(`${esperado[0]}:${esperado[1]}`, esperado);
  // Mesma ordem do provedor do Readest (starDictProvider.ts): .idx, depois .syn
  let entrada = await leitor.lookup(chave);
  if (!entrada) entrada = await leitor.resolveSynonym(chave);
  if (entrada && entrada.offset === esperado[0] && entrada.size === esperado[1]) {
    chavesOk++;
    continue;
  }
  chavesFalha++;
  if (falhas.length < LIMITE_FALHAS) {
    falhas.push({
      chave,
      esperado,
      obtido: entrada ? [entrada.offset, entrada.size] : null,
    });
  }
}

const integral = gunzipSync(new Uint8Array(readFileSync(arquivo('.dict.dz'))));
let trechosOk = 0;
let trechosFalha = 0;
for (const [offset, tamanho] of trechos.values()) {
  const porBlocos = await leitor.read({ word: '', offset, size: tamanho });
  const referencia = integral.subarray(offset, offset + tamanho);
  if (Buffer.from(porBlocos).equals(Buffer.from(referencia))) {
    trechosOk++;
  } else {
    trechosFalha++;
    if (falhas.length < LIMITE_FALHAS) {
      falhas.push({ chave: `<trecho ${offset}:${tamanho}>`, esperado: [offset, tamanho], obtido: null });
    }
  }
}

const aprovado = chavesFalha === 0 && trechosFalha === 0 && linhas.length > 0;
process.stdout.write(
  JSON.stringify({
    readest: { tag: fonte.tag, commit: fonte.commit },
    fflate: versaoFflate,
    node: process.version,
    chaves_ok: chavesOk,
    chaves_falha: chavesFalha,
    trechos_ok: trechosOk,
    trechos_falha: trechosFalha,
    falhas,
    duracao_s: Math.round((performance.now() - inicio) / 100) / 10,
    veredito: aprovado ? 'aprovado' : 'reprovado',
  }) + '\n',
);
process.exit(aprovado ? 0 : 1);
