export default defineEventHandler((event) => {
  const now = new Date().toISOString()
  const method = event.method
  const url = event.path
  const ip = getRequestIP(event, { xForwardedFor: true }) || 'unknown'
  
  console.log(`\n========================================`)
  console.log(`[${now}] ${method} ${url}`)
  console.log(`IP: ${ip}`)
  console.log(`Headers: ${JSON.stringify(getRequestHeaders(event), null, 2)}`)
  console.log(`========================================\n`)
})
