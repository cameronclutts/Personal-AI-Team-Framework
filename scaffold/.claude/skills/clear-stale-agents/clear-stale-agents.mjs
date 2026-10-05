#!/usr/bin/env node
// clear-stale-agents: close idle pixel-agents characters through the running
// server's WebSocket (requestDiagnostics, closeAgent). Writes no file and
// signals no process. Needs Node 22+ for the built-in WebSocket client, which
// sends no Origin header, so the standalone same-origin gate admits it.
import { execFileSync } from 'node:child_process';
import { statSync } from 'node:fs';
import path from 'node:path';

const MIN_CUTOFF_MIN = 10; // A server restart re-adopts transcripts modified in the last 10 min.
const TIMEOUT_MS = 5000;

function parseArgs(argv) {
  const opts = { minutes: 30, port: 3100, dryRun: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--port') opts.port = Number(argv[++i]);
    else if (a === '--dry-run') opts.dryRun = true;
    else if (/^\d+$/.test(a)) opts.minutes = Number(a);
    else fail(64, `unknown argument: ${a}`);
  }
  if (!Number.isInteger(opts.port) || opts.port < 1 || opts.port > 65535) fail(64, 'bad --port');
  if (opts.minutes < MIN_CUTOFF_MIN) {
    fail(64, `cutoff must be at least ${MIN_CUTOFF_MIN} minutes; a server restart would re-adopt anything closed sooner`);
  }
  return opts;
}

function fail(code, message) {
  console.error(`clear-stale-agents: ${message}`);
  process.exit(code);
}

function mtimeMs(file) {
  try {
    return statSync(file).mtimeMs;
  } catch {
    return 0;
  }
}

// Decide one agent. lastDataAt is Date.now() ms of the last transcript line the
// server read; 0 means the server has read no new line since it adopted or
// restored the agent (it is not "idle forever"), so the transcript's mtime is
// the fallback and the later of the two wins.
export function classify(d, now, cutoffMs, mtimeOf = mtimeMs) {
  if (!d.jsonlFile) return { action: 'keep', reason: 'no transcript path (hooks-only agent)' };
  if (!d.jsonlExists) return { action: 'close', reason: 'transcript missing' };
  const last = Math.max(d.lastDataAt || 0, mtimeOf(d.jsonlFile));
  if (last === 0) return { action: 'close', reason: 'transcript missing' };
  const idleMin = Math.floor((now - last) / 60000);
  if (now - last > cutoffMs) return { action: 'close', reason: `idle ${idleMin} min` };
  return { action: 'keep', reason: `idle ${idleMin} min` };
}

function label(d) {
  const dir = path.basename(d.projectDir || '');
  return d.jsonlFile ? `${dir}/${path.basename(d.jsonlFile)}` : dir;
}

function liveClaudeCount() {
  try {
    const out = execFileSync('pgrep', ['-f', 'native-binary/claude|^claude'], { encoding: 'utf8' });
    return out.split('\n').filter(Boolean).length;
  } catch {
    return 0; // pgrep exits 1 when nothing matches
  }
}

function open(url) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(url);
    const timer = setTimeout(() => reject(new Error('connect timeout')), TIMEOUT_MS);
    ws.addEventListener('open', () => { clearTimeout(timer); resolve(ws); });
    ws.addEventListener('error', () => { clearTimeout(timer); reject(new Error('connect failed')); });
    ws.addEventListener('close', (e) => {
      clearTimeout(timer);
      reject(new Error(`closed by server: ${e.code} ${e.reason}`));
    });
  });
}

function diagnostics(ws) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('no agentDiagnostics reply')), TIMEOUT_MS);
    const onMessage = (e) => {
      let msg;
      try { msg = JSON.parse(e.data); } catch { return; }
      if (msg.type !== 'agentDiagnostics') return;
      clearTimeout(timer);
      ws.removeEventListener('message', onMessage);
      resolve(msg.agents ?? []);
    };
    ws.addEventListener('message', onMessage);
    ws.send(JSON.stringify({ type: 'requestDiagnostics' }));
  });
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const url = `ws://127.0.0.1:${opts.port}/ws`;
  let ws;
  try {
    ws = await open(url);
  } catch (err) {
    fail(2, `pixel-agents is not reachable at ${url} (${err.message}); nothing closed. If you use pixel-agents, start it, then rerun`);
  }
  const now = Date.now();
  const before = await diagnostics(ws);
  console.log(`pixel-agents ${url}  cutoff ${opts.minutes} min${opts.dryRun ? '  (dry run)' : ''}`);
  console.log(`before: ${before.length} agents`);
  const toClose = [];
  for (const d of before) {
    const { action, reason } = classify(d, now, opts.minutes * 60000);
    console.log(`  ${action.padEnd(5)} #${d.id}  ${reason}  ${label(d)}`);
    if (action === 'close') toClose.push(d.id);
  }
  if (!opts.dryRun) {
    for (const id of toClose) ws.send(JSON.stringify({ type: 'closeAgent', id }));
  }
  const after = await diagnostics(ws); // same socket, so it is handled after the closes
  ws.close();
  const verb = opts.dryRun ? 'would close' : 'closed';
  console.log(`after: ${after.length} agents (${verb} ${toClose.length})`);
  console.log(`live claude processes: ${liveClaudeCount()}`);
}

main().catch((err) => fail(1, err.message));
