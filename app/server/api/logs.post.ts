/**
 * Endpoint para receber logs do ESP32.
 * POST /api/logs
 */
import { addLogs, getLogs } from './logs.get';

export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  
  if (!body) {
    return { success: false, error: 'Corpo vazio' };
  }

  const { device_id, logs } = body;
  
  if (!logs || !Array.isArray(logs)) {
    return { success: false, error: 'Formato inválido' };
  }

  addLogs(logs, device_id || 'ESP32');

  console.log(`[LOGS] Recebidos ${logs.length} logs de ${device_id || 'ESP32'}`);
  
  return { 
    success: true, 
    count: logs.length,
    total: getLogs().length
  };
});
