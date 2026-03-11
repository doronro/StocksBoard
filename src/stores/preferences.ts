import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type TraderType = 'day_trader' | 'swing_trader' | 'value_investor' | 'institutional'
export type TimeHorizon = 'day_trading' | 'swing' | 'position' | 'long_term'

interface TechnicalIndicatorPreferences {
  sma20: boolean
  sma50: boolean
  sma200: boolean
  rsi: boolean
  macd: boolean
  bollingerBands: boolean
  volumeProfile: boolean
  fibonacci: boolean
}

interface AlertPreferences {
  enableEmailAlerts: boolean
  enablePushAlerts: boolean
  enableInAppAlerts: boolean
  enableSoundAlerts: boolean
  priceAlertThreshold: number // percentage
}

interface ChartPreferences {
  chartType: 'candlestick' | 'ohlc' | 'line'
  defaultTimeframe: string
  showVolume: boolean
  showGrid: boolean
  darkMode: boolean
}

interface PreferencesState {
  // Trader Profile
  traderType: TraderType
  timeHorizon: TimeHorizon

  // Technical Indicators
  technicalIndicators: TechnicalIndicatorPreferences

  // Alerts
  alerts: AlertPreferences

  // Chart
  chart: ChartPreferences

  // Portfolio Settings
  showDividends: boolean
  showTaxLots: boolean
  riskToleranceLevel: 'conservative' | 'moderate' | 'aggressive'

  // Notifications
  notificationFrequency: 'realtime' | 'hourly' | 'daily'

  // Actions
  setTraderType: (type: TraderType) => void
  setTimeHorizon: (horizon: TimeHorizon) => void
  updateTechnicalIndicators: (indicators: Partial<TechnicalIndicatorPreferences>) => void
  updateAlerts: (alerts: Partial<AlertPreferences>) => void
  updateChart: (chart: Partial<ChartPreferences>) => void
  setRiskTolerance: (level: 'conservative' | 'moderate' | 'aggressive') => void
  setNotificationFrequency: (freq: 'realtime' | 'hourly' | 'daily') => void
}

const DEFAULT_TECHNICAL_INDICATORS: TechnicalIndicatorPreferences = {
  sma20: true,
  sma50: true,
  sma200: true,
  rsi: true,
  macd: true,
  bollingerBands: false,
  volumeProfile: false,
  fibonacci: false,
}

const DEFAULT_ALERT_PREFERENCES: AlertPreferences = {
  enableEmailAlerts: true,
  enablePushAlerts: true,
  enableInAppAlerts: true,
  enableSoundAlerts: true,
  priceAlertThreshold: 2,
}

const DEFAULT_CHART_PREFERENCES: ChartPreferences = {
  chartType: 'candlestick',
  defaultTimeframe: '1d',
  showVolume: true,
  showGrid: true,
  darkMode: true,
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      // Initial state
      traderType: 'swing_trader',
      timeHorizon: 'swing',
      technicalIndicators: DEFAULT_TECHNICAL_INDICATORS,
      alerts: DEFAULT_ALERT_PREFERENCES,
      chart: DEFAULT_CHART_PREFERENCES,
      showDividends: true,
      showTaxLots: false,
      riskToleranceLevel: 'moderate',
      notificationFrequency: 'realtime',

      // Actions
      setTraderType: (type) => {
        set({ traderType: type })

        // Auto-configure based on trader type
        const configurations: Record<TraderType, Partial<PreferencesState>> = {
          day_trader: {
            timeHorizon: 'day_trading',
            technicalIndicators: {
              ...DEFAULT_TECHNICAL_INDICATORS,
              rsi: true,
              volumeProfile: true,
              fibonacci: true,
            },
            chart: {
              ...DEFAULT_CHART_PREFERENCES,
              defaultTimeframe: '5m',
            },
            alerts: {
              ...DEFAULT_ALERT_PREFERENCES,
              priceAlertThreshold: 0.5,
            },
            notificationFrequency: 'realtime',
          },
          swing_trader: {
            timeHorizon: 'swing',
            technicalIndicators: {
              ...DEFAULT_TECHNICAL_INDICATORS,
              bollingerBands: true,
            },
            chart: {
              ...DEFAULT_CHART_PREFERENCES,
              defaultTimeframe: '4h',
            },
            notificationFrequency: 'hourly',
          },
          value_investor: {
            timeHorizon: 'long_term',
            technicalIndicators: {
              sma20: false,
              sma50: false,
              sma200: true,
              rsi: false,
              macd: false,
              bollingerBands: false,
              volumeProfile: false,
              fibonacci: false,
            },
            chart: {
              ...DEFAULT_CHART_PREFERENCES,
              defaultTimeframe: '1d',
            },
            showDividends: true,
            notificationFrequency: 'daily',
          },
          institutional: {
            timeHorizon: 'position',
            technicalIndicators: DEFAULT_TECHNICAL_INDICATORS,
            chart: {
              ...DEFAULT_CHART_PREFERENCES,
              defaultTimeframe: '1h',
            },
            showTaxLots: true,
            notificationFrequency: 'realtime',
          },
        }

        set(configurations[type])
      },

      setTimeHorizon: (horizon) => {
        set({ timeHorizon: horizon })
      },

      updateTechnicalIndicators: (indicators) => {
        set((state) => ({
          technicalIndicators: {
            ...state.technicalIndicators,
            ...indicators,
          },
        }))
      },

      updateAlerts: (alerts) => {
        set((state) => ({
          alerts: {
            ...state.alerts,
            ...alerts,
          },
        }))
      },

      updateChart: (chart) => {
        set((state) => ({
          chart: {
            ...state.chart,
            ...chart,
          },
        }))
      },

      setRiskTolerance: (level) => {
        set({ riskToleranceLevel: level })
      },

      setNotificationFrequency: (freq) => {
        set({ notificationFrequency: freq })
      },
    }),
    {
      name: 'stock-exchange-preferences',
    }
  )
)
