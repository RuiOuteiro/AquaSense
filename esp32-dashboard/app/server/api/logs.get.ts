/**
 * Endpoint para obter logs do ESP32.
 * GET /api/logs?since=<timestamp>
 */

// Buffer partilhado de logs em memória
let logBuffer: Array<{
  time: string;
  message: string;
  type: 'info' | 'warn' | 'error' | 'success';
  device_id: string;
  timestamp: number;
}> = [];

const MAX_LOGS = 500;

// Função para adicionar log (usada pelo POST)
export function addLog(
  message: string, 
  type: 'info' | 'warn' | 'error' | 'success' = 'info',
  device_id: string = 'ESP32'
) {
  const entry = {
    time: new Date().toLocaleTimeString('pt-PT'),
    message,
    type,
    device_id,
    timestamp: Date.now()
  };
  
  logBuffer.push(entry);
  
  if (logBuffer.length > MAX_LOGS) {
    logBuffer.shift();
  }
  
  return entry;
}

// Função para adicionar múltiplos logs
export function addLogs(logs: Array<{ message: string; type?: string }>, device_id: string = 'ESP32') {
  for (const log of logs) {
    addLog(log.message, (log.type as any) || 'info', device_id);
  }
}

// Função para obter logs
export function getLogs(since?: number, limit: number = 100) {
  let result = logBuffer;
  
  if (since) {
    result = result.filter(l => l.timestamp > since);
  }
  
  return result.slice(-limit);
}

// Função para limpar logs
export function clearLogs() {
  logBuffer = [];
}

export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const since = query.since ? parseInt(String(query.since)) : undefined;
  const limit = query.limit ? parseInt(String(query.limit)) : 100;
  
  const logs = getLogs(since, limit);
  
  return {
    success: true,
    logs,
    count: logs.length,
    total: logBuffer.length,
    timestamp: Date.now()
  };
});
