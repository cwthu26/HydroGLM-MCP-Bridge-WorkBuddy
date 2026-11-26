#!/usr/bin/env node
'use strict';

const { spawn, spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const metadata = require('../package.json');

const ROOT = path.resolve(__dirname, '..');
const PYTHON_PROBE = 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 78)';

function findPython(env = process.env, platform = process.platform) {
  const explicit = env.HYDROGLM_PYTHON?.trim();
  const choices = explicit
    ? [{ command: explicit, args: [] }]
    : platform === 'win32'
      ? [{ command: 'py', args: ['-3'] }, { command: 'python', args: [] }, { command: 'python3', args: [] }]
      : [{ command: 'python3', args: [] }, { command: 'python', args: [] }];
  for (const choice of choices) {
    const probe = spawnSync(choice.command, [...choice.args, '-c', PYTHON_PROBE], {
      env, encoding: 'utf8', timeout: 5000, windowsHide: true, shell: false,
      stdio: ['ignore', 'ignore', 'pipe'],
    });
    if (!probe.error && probe.status === 0) return choice;
  }
  throw new Error(explicit
    ? 'HYDROGLM_PYTHON must point to a working Python 3.10+ executable (without extra arguments).'
    : 'Python 3.10+ is required. Install Python or set HYDROGLM_PYTHON to its executable path.');
}

function buildConfig(client, serverName = 'hydroglm_bridge') {
  if (!/^[A-Za-z0-9_-]+$/.test(serverName)) throw new Error('Invalid server name.');
  const args = ['-y', `${metadata.name}@${metadata.version}`];
  if (client === 'codex') {
    return `[mcp_servers.${serverName}]\ncommand = "npx"\nargs = ${JSON.stringify(args)}\nenabled = true\nstartup_timeout_sec = 120\ntool_timeout_sec = 660\n`;
  }
  if (!['workbuddy', 'claude', 'generic'].includes(client)) {
    throw new Error('Client must be codex, workbuddy, claude or generic.');
  }
  const entry = { command: 'npx', args };
  if (client === 'workbuddy') entry.type = 'stdio';
  return JSON.stringify({ mcpServers: { [serverName]: entry } }, null, 2) + '\n';
}

function writeConfig(args) {
  const values = {};
  let force = false;
  for (let index = 0; index < args.length; index++) {
    const flag = args[index];
    if (flag === '--force') {
      force = true;
    } else if (['--client', '--server-name', '--output'].includes(flag) && args[index + 1] && !args[index + 1].startsWith('--')) {
      values[flag] = args[++index];
    } else {
      throw new Error(`Unknown option or missing value: ${flag}`);
    }
  }
  const text = buildConfig(values['--client'], values['--server-name']);
  if (values['--output']) {
    fs.writeFileSync(path.resolve(values['--output']), text, { encoding: 'utf8', flag: force ? 'w' : 'wx' });
    process.stderr.write('Configuration snippet saved. Merge it into your MCP client settings.\n');
  } else {
    process.stdout.write(text);
  }
}

function launchPython(script, args) {
  const python = findPython();
  const child = spawn(python.command, [...python.args, '-X', 'utf8', '-u', path.join(ROOT, script), ...args], {
    stdio: 'inherit', shell: false, windowsHide: true,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  const handlers = new Map();
  for (const signal of ['SIGINT', 'SIGTERM']) {
    const handler = () => { if (!child.killed) child.kill(signal); };
    handlers.set(signal, handler);
    process.on(signal, handler);
  }
  function cleanUp() {
    for (const [signal, handler] of handlers) process.removeListener(signal, handler);
  }
  child.once('error', () => {
    cleanUp();
    process.stderr.write('Could not start the HydroGLM Python service.\n');
    process.exitCode = 1;
  });
  child.once('exit', (code, signal) => {
    cleanUp();
    process.exitCode = code ?? (signal === 'SIGINT' ? 130 : 143);
  });
  return child;
}

function main(args = process.argv.slice(2)) {
  if (args[0] === '--version' || args[0] === '-v') {
    process.stdout.write(`${metadata.version}\n`);
    return;
  }
  if (args[0] === '--help' || args[0] === '-h' || args[0] === 'help') {
    process.stdout.write(`hydroglm-mcp-bridge ${metadata.version}\n\nRequires Node.js 22+ and Python 3.10+.\n\nCommands:\n  serve                           Start the stdio MCP service (default)\n  configure --agent HydroGLM      Save an API key once\n  configure --agent HydroGLM-plus Save the plus API key once\n  config --client codex|workbuddy|claude|generic [--output FILE]\n  diagnose --agent HydroGLM       Check the models endpoint\n  probe --agent HydroGLM          Send one actual API request\n\nSet HYDROGLM_PYTHON to choose a Python executable.\n`);
    return;
  }
  const command = args[0] || 'serve';
  const remaining = args.slice(1);
  if (command === 'config') return writeConfig(remaining);
  if (command === 'serve') {
    if (remaining.length) throw new Error('The serve command takes no arguments.');
    return launchPython('server.py', []);
  }
  const scripts = { configure: 'configure_key.py', diagnose: 'diagnose.py', probe: 'probe_chat.py' };
  if (!Object.hasOwn(scripts, command)) throw new Error(`Unknown command: ${command}. Use --help.`);
  return launchPython(scripts[command], remaining);
}

module.exports = { ROOT, findPython, buildConfig, main };

if (require.main === module) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`hydroglm-mcp-bridge: ${error.message}\n`);
    process.exitCode = 1;
  }
}
