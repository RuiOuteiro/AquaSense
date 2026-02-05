const TELEGRAM_BOT_TOKEN = '8598186249:AAEXBDAgVM-M6Qw5mz23LLEay7r2F-9E1zE'

export async function sendTelegramMessage(chatId: string, message: string): Promise<boolean> {
  try {
    const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`
    
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: 'HTML'
      })
    })
    
    const data = await response.json()
    return data.ok === true
  } catch (error) {
    console.error('[TELEGRAM] Erro ao enviar mensagem:', error)
    return false
  }
}

export async function sendAlerta(chatId: string, tipo: string, valor: number): Promise<boolean> {
  const nomes: Record<string, string> = {
    temperature: 'TEMPERATURA',
    ambient_temp: 'TEMPERATURA AMBIENTE',
    humidity: 'HUMIDADE',
    ph: 'PH',
    turbidity: 'TURBIDEZ'
  }
  
  const nome = nomes[tipo.toLowerCase()] || tipo.toUpperCase()
  const valorFormatado = valor.toFixed(1)
  
  const message = `⚠️ <b>${nome} FORA DOS PARÂMETROS ACEITÁVEIS</b>

Valor: ${valorFormatado}`
  
  return sendTelegramMessage(chatId, message)
}

export async function testTelegramConnection(chatId: string): Promise<boolean> {
  const message = `
<b>AquaSense Conectado! ✅</b>

O teu Telegram está configurado para receber alertas do AquaSense.

Vais receber notificações quando os sensores saírem dos limites definidos.
`
  
  return sendTelegramMessage(chatId, message)
}
