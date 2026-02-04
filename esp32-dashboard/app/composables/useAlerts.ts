export interface Alert {
  id: string
  type: 'warning' | 'danger' | 'info' | 'success'
  title: string
  message: string
  parameter?: string
  timestamp: number
}

export interface AlertConfig {
  enabled: boolean
  tempMin: number
  tempMax: number
  phMin: number
  phMax: number
  turbidezMax: number
  humidadeMin: number
  humidadeMax: number
}

const alerts = ref<Alert[]>([])
const alertHistory = ref<Alert[]>([])

const defaultConfig: AlertConfig = {
  enabled: true,
  tempMin: 22,
  tempMax: 28,
  phMin: 6.5,
  phMax: 7.5,
  turbidezMax: 30,
  humidadeMin: 40,
  humidadeMax: 80
}

const alertConfig = ref<AlertConfig>({ ...defaultConfig })

export function useAlerts() {
  function addAlert(alert: Omit<Alert, 'id' | 'timestamp'>) {
    if (!alertConfig.value.enabled) return

    const existingIndex = alerts.value.findIndex(a => a.parameter === alert.parameter)
    if (existingIndex !== -1) return

    const newAlert: Alert = {
      ...alert,
      id: `alert-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      timestamp: Date.now()
    }

    alerts.value.push(newAlert)
    alertHistory.value.unshift(newAlert)

    if (alertHistory.value.length > 50) {
      alertHistory.value = alertHistory.value.slice(0, 50)
    }
  }

  function removeAlert(id: string) {
    alerts.value = alerts.value.filter(a => a.id !== id)
  }

  function clearAlerts() {
    alerts.value = []
  }

  function checkParameters(params: {
    temperatura?: number | null
    ph?: number | null
    turbidez?: number | null
    humidade?: number | null
  }) {
    if (!alertConfig.value.enabled) return

    const cfg = alertConfig.value

    if (params.temperatura !== null && params.temperatura !== undefined) {
      if (params.temperatura < cfg.tempMin) {
        addAlert({
          type: 'warning',
          title: 'Temperatura Baixa',
          message: `Temperatura actual: ${params.temperatura.toFixed(1)}°C (mín: ${cfg.tempMin}°C)`,
          parameter: 'temperatura'
        })
      } else if (params.temperatura > cfg.tempMax) {
        addAlert({
          type: 'danger',
          title: 'Temperatura Alta',
          message: `Temperatura actual: ${params.temperatura.toFixed(1)}°C (máx: ${cfg.tempMax}°C)`,
          parameter: 'temperatura'
        })
      }
    }

    if (params.ph !== null && params.ph !== undefined) {
      if (params.ph < cfg.phMin) {
        addAlert({
          type: 'warning',
          title: 'pH Baixo',
          message: `pH actual: ${params.ph.toFixed(2)} (mín: ${cfg.phMin})`,
          parameter: 'ph'
        })
      } else if (params.ph > cfg.phMax) {
        addAlert({
          type: 'danger',
          title: 'pH Alto',
          message: `pH actual: ${params.ph.toFixed(2)} (máx: ${cfg.phMax})`,
          parameter: 'ph'
        })
      }
    }

    if (params.turbidez !== null && params.turbidez !== undefined) {
      if (params.turbidez > cfg.turbidezMax) {
        addAlert({
          type: 'warning',
          title: 'Turbidez Elevada',
          message: `Turbidez actual: ${params.turbidez.toFixed(0)}% (máx: ${cfg.turbidezMax}%)`,
          parameter: 'turbidez'
        })
      }
    }

    if (params.humidade !== null && params.humidade !== undefined) {
      if (params.humidade < cfg.humidadeMin) {
        addAlert({
          type: 'info',
          title: 'Humidade Baixa',
          message: `Humidade actual: ${params.humidade.toFixed(0)}% (mín: ${cfg.humidadeMin}%)`,
          parameter: 'humidade'
        })
      } else if (params.humidade > cfg.humidadeMax) {
        addAlert({
          type: 'info',
          title: 'Humidade Alta',
          message: `Humidade actual: ${params.humidade.toFixed(0)}% (máx: ${cfg.humidadeMax}%)`,
          parameter: 'humidade'
        })
      }
    }
  }

  function updateConfig(newConfig: Partial<AlertConfig>) {
    alertConfig.value = { ...alertConfig.value, ...newConfig }
  }

  function getConfig() {
    return alertConfig.value
  }

  return {
    alerts: readonly(alerts),
    alertHistory: readonly(alertHistory),
    alertConfig: readonly(alertConfig),
    addAlert,
    removeAlert,
    clearAlerts,
    checkParameters,
    updateConfig,
    getConfig
  }
}
