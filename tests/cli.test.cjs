'use strict';
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const { ROOT, buildConfig } = require('../bin/hydroglm-mcp-bridge.cjs');
const metadata = require('../package.json');
const executable = path.join(ROOT, 'bin/hydroglm-mcp-bridge.cjs');

function run(args, options = {}) {
  return spawnSync(process.execPath, [executable, ...args], { encoding: 'utf8', timeout: 10000, ...options });
}

test('help and version do not require Python or credentials', () => {
  const env = { ...process.env, HYDROGLM_PYTHON: path.join(ROOT, 'missing-python') };
  assert.equal(run(['--help'], { env }).status, 0);
  const version = run(['--version'], { env });
  assert.equal(version.status, 0);
  assert.equal(version.stdout.trim(), metadata.version);
});

test('launcher preserves stdio JSON without a startup banner', () => {
  const input = [
    { jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-06-18' } },
    { jsonrpc: '2.0', method: 'notifications/initialized' },
    { jsonrpc: '2.0', id: 2, method: 'tools/list' },
    { jsonrpc: '2.0', id: 3, method: 'ping' },
  ].map(message => JSON.stringify(message) + '\n').join('');
  const result = run([], { input, cwd: os.tmpdir() });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, '');
  const replies = result.stdout.trim().split('\n').map(JSON.parse);
  assert.deepEqual(replies.map(reply => reply.id), [1, 2, 3]);
  assert.equal(replies[0].result.serverInfo.version, metadata.version);
  assert.equal(replies[1].result.tools[0].name, 'ask_hydroglm');
});

test('Python selection failure goes to stderr and does not pollute MCP stdout', () => {
  const result = run([], { env: { ...process.env, HYDROGLM_PYTHON: path.join(ROOT, 'missing-python') } });
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /Python 3\.10/);
});

test('MCP configurations use a pinned npx package instead of a temporary cache path', () => {
  for (const client of ['workbuddy', 'claude', 'generic']) {
    const config = JSON.parse(buildConfig(client));
    assert.deepEqual(config.mcpServers.hydroglm_bridge.args, ['-y', `${metadata.name}@${metadata.version}`]);
    assert.equal(config.mcpServers.hydroglm_bridge.command, 'npx');
    assert.ok(!config.mcpServers.hydroglm_bridge.env);
  }
  const codex = buildConfig('codex');
  assert.match(codex, /startup_timeout_sec = 120/);
  assert.match(codex, /tool_timeout_sec = 660/);
  assert.ok(!codex.includes(ROOT));
});

test('configuration output refuses overwrites unless --force is supplied', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'hydroglm-cli-'));
  try {
    const output = path.join(directory, '配置 文件.json');
    const args = ['config', '--client', 'workbuddy', '--output', output];
    assert.equal(run(args).status, 0);
    const original = fs.readFileSync(output, 'utf8');
    assert.notEqual(run(args).status, 0);
    assert.equal(fs.readFileSync(output, 'utf8'), original);
    assert.equal(run([...args, '--force']).status, 0);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('configure forwards Python options without prompting during --help', () => {
  const result = run(['configure', '--help']);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /HydroGLM-plus/);
});

test('unknown commands and malformed config options are rejected', () => {
  assert.notEqual(run(['unexpected']).status, 0);
  assert.notEqual(run(['config', '--client']).status, 0);
  assert.throws(() => buildConfig('generic', 'bad.name'));
});
