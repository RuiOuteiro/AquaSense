export default defineEventHandler((event) => {
  const ip = getRequestIP(event, { xForwardedFor: true }) || 'unknown'
  console.log(`\n!!! TEST ENDPOINT HIT !!! IP: ${ip}\n`)
  return { 
    status: 'ok', 
    time: new Date().toISOString(),
    ip: ip,
    message: 'Servidor AquaSense a funcionar!'
  }
})
