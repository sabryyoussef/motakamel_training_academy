import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '200kb' }));
app.use(bodyParser.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, _res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// Console tap endpoint
app.post('/__console_tap__', (req, res) => {
  const stamp = new Date().toISOString();
  const data = {
    stamp,
    kind: 'console_tap',
    ...req.body
  };
  
  // Log to console with structured format
  console.log(JSON.stringify(data, null, 2));
  
  // Also log to stderr for error-level messages
  if (req.body.level === 'error' || req.body.type === 'error' || req.body.msg?.includes('error')) {
    console.error(`[ERROR] ${stamp}: ${JSON.stringify(req.body)}`);
  }
  
  res.status(204).end();
});

// Health check endpoint
app.get('/__console_tap__/health', (_req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Stats endpoint
let stats = {
  totalRequests: 0,
  errorCount: 0,
  startTime: new Date().toISOString()
};

app.get('/__console_tap__/stats', (_req, res) => {
  res.json(stats);
});

// Update stats middleware
app.use((req, _res, next) => {
  stats.totalRequests++;
  if (req.body.level === 'error' || req.body.type === 'error') {
    stats.errorCount++;
  }
  next();
});

const port = Number(process.env['CONSOLE_TAP_PORT'] || 5055);
const host = process.env['CONSOLE_TAP_HOST'] || 'localhost';

app.listen(port, host, () => {
  console.log(`🚀 [console-tap] Server listening on http://${host}:${port}`);
  console.log(`📊 Health check: http://${host}:${port}/__console_tap__/health`);
  console.log(`📈 Stats: http://${host}:${port}/__console_tap__/stats`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down console tap server...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Shutting down console tap server...');
  process.exit(0);
});
