// Usage: node scripts/verify_gemini_patterns.mjs /tmp/tools/node_modules/@google/gemini-cli-core
// Imports the actual published host engine; no model, account, or runtime dependency.
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, copyFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import assert from 'node:assert/strict';
const repo = resolve(dirname(fileURLToPath(import.meta.url)), '..');
if (!process.argv[2]) throw new Error('Pass an installed @google/gemini-cli-core package directory');
const core = resolve(process.argv[2]);
const { FileDiscoveryService } = await import(pathToFileURL(join(core, 'dist/src/services/fileDiscoveryService.js')));
const cases = JSON.parse(readFileSync(join(repo, 'tests/host-controls/cases.json')));
const root = mkdtempSync(join(tmpdir(), 'lbp-gemini-'));
try {
  copyFileSync(join(repo, 'resources/host-controls/geminiignore'), join(root, '.geminiignore'));
  const paths = Object.entries(cases).flatMap(([kind, paths]) =>
    ['', 'packages/demo/'].flatMap(prefix => paths.map(path => [prefix + path, kind === 'deny'])));
  for (const [path] of paths) {
    mkdirSync(dirname(join(root, path)), { recursive: true });
    writeFileSync(join(root, path), 'SYNTHETIC FIXTURE ONLY\n');
  }
  const service = new FileDiscoveryService(root, { respectGitIgnore: false, respectGeminiIgnore: true });
  for (const [path, denied] of paths) assert.equal(service.shouldIgnoreFile(path), denied, path);
  assert.deepEqual(service.filterFiles(paths.map(([path]) => path)), paths.filter(([, denied]) => !denied).map(([path]) => path));
  assert.equal(service.shouldIgnoreFile('.env', { respectGeminiIgnore: false }), false, 'disabled-control check');
  const version = JSON.parse(readFileSync(join(core, 'package.json'))).version;
  console.log(`PASS Gemini CLI core ${version}: ${paths.length} discovery checks + batch filtering + disabled control`);
} finally {
  rmSync(root, { recursive: true, force: true });
}
