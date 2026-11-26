'use strict';
const { spawnSync } = require('node:child_process');
const { findPython, ROOT } = require('../bin/hydroglm-mcp-bridge.cjs');
try {
  const python = findPython();
  const result = spawnSync(python.command, [...python.args, '-X', 'utf8', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], {
    cwd: ROOT, stdio: 'inherit', shell: false,
  });
  process.exitCode = result.status ?? 1;
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
