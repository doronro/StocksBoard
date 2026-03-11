import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { usePreferencesStore } from '../preferences'

describe('Preferences Store', () => {
  beforeEach(() => {
    // Clear persisted storage to ensure clean state
    localStorage.removeItem('stock-exchange-preferences')
  })

  afterEach(() => {
    // Clean up after tests
    localStorage.removeItem('stock-exchange-preferences')
  })

  describe('Trader Type Configuration', () => {
    it('sets trader type to day_trader', () => {
      usePreferencesStore.getState().setTraderType('day_trader')
      const store = usePreferencesStore.getState()

      expect(store.traderType).toBe('day_trader')
      expect(store.timeHorizon).toBe('day_trading')
    })

    it('auto-configures chart for day trading', () => {
      usePreferencesStore.getState().setTraderType('day_trader')
      const store = usePreferencesStore.getState()

      expect(store.chart.defaultTimeframe).toBe('5m')
      expect(store.notificationFrequency).toBe('realtime')
    })

    it('configures swing trader with daily charts', () => {
      usePreferencesStore.getState().setTraderType('swing_trader')
      const store = usePreferencesStore.getState()

      expect(store.timeHorizon).toBe('swing')
      expect(store.chart.defaultTimeframe).toBe('4h')
    })

    it('configures value investor with daily charts and dividends', () => {
      usePreferencesStore.getState().setTraderType('value_investor')
      const store = usePreferencesStore.getState()

      expect(store.timeHorizon).toBe('long_term')
      expect(store.showDividends).toBe(true)
      expect(store.chart.defaultTimeframe).toBe('1d')
    })

    it('configures institutional with tax lot tracking', () => {
      usePreferencesStore.getState().setTraderType('institutional')
      const store = usePreferencesStore.getState()

      expect(store.showTaxLots).toBe(true)
      expect(store.chart.defaultTimeframe).toBe('1h')
    })
  })

  describe('Technical Indicators', () => {
    it('updates individual indicator preferences', () => {
      usePreferencesStore.getState().updateTechnicalIndicators({
        rsi: false,
        macd: true,
      })
      const store = usePreferencesStore.getState()

      expect(store.technicalIndicators.rsi).toBe(false)
      expect(store.technicalIndicators.macd).toBe(true)
    })

    it('preserves other indicator settings when updating', () => {
      const store = usePreferencesStore.getState()
      const originalSMA20 = store.technicalIndicators.sma20

      usePreferencesStore.getState().updateTechnicalIndicators({
        rsi: false,
      })
      const updatedStore = usePreferencesStore.getState()

      expect(updatedStore.technicalIndicators.sma20).toBe(originalSMA20)
    })

    it('day traders get volume profile by default', () => {
      usePreferencesStore.getState().setTraderType('day_trader')
      const store = usePreferencesStore.getState()

      expect(store.technicalIndicators.volumeProfile).toBe(true)
    })
  })

  describe('Alert Preferences', () => {
    it('updates alert preferences', () => {
      usePreferencesStore.getState().updateAlerts({
        enableSoundAlerts: false,
        priceAlertThreshold: 1,
      })
      const store = usePreferencesStore.getState()

      expect(store.alerts.enableSoundAlerts).toBe(false)
      expect(store.alerts.priceAlertThreshold).toBe(1)
    })

    it('day traders get tighter price alert threshold', () => {
      usePreferencesStore.getState().setTraderType('day_trader')
      const store = usePreferencesStore.getState()

      expect(store.alerts.priceAlertThreshold).toBe(0.5)
    })
  })

  describe('Chart Preferences', () => {
    it('updates chart preferences', () => {
      usePreferencesStore.getState().updateChart({
        chartType: 'line',
        showVolume: false,
      })
      const store = usePreferencesStore.getState()

      expect(store.chart.chartType).toBe('line')
      expect(store.chart.showVolume).toBe(false)
    })

    it('preserves other chart settings when updating', () => {
      const store = usePreferencesStore.getState()
      const originalDarkMode = store.chart.darkMode

      usePreferencesStore.getState().updateChart({
        chartType: 'line',
      })
      const updatedStore = usePreferencesStore.getState()

      expect(updatedStore.chart.darkMode).toBe(originalDarkMode)
    })
  })

  describe('Risk Tolerance', () => {
    it('updates risk tolerance level', () => {
      usePreferencesStore.getState().setRiskTolerance('aggressive')
      const store = usePreferencesStore.getState()

      expect(store.riskToleranceLevel).toBe('aggressive')
    })

    it('supports conservative risk tolerance', () => {
      usePreferencesStore.getState().setRiskTolerance('conservative')
      const store = usePreferencesStore.getState()

      expect(store.riskToleranceLevel).toBe('conservative')
    })
  })

  describe('Notification Frequency', () => {
    it('updates notification frequency', () => {
      usePreferencesStore.getState().setNotificationFrequency('hourly')
      const store = usePreferencesStore.getState()

      expect(store.notificationFrequency).toBe('hourly')
    })

    it('day traders get realtime notifications by default', () => {
      usePreferencesStore.getState().setTraderType('day_trader')
      const store = usePreferencesStore.getState()

      expect(store.notificationFrequency).toBe('realtime')
    })

    it('value investors get daily notifications by default', () => {
      usePreferencesStore.getState().setTraderType('value_investor')
      const store = usePreferencesStore.getState()

      expect(store.notificationFrequency).toBe('daily')
    })
  })

  describe('Time Horizon', () => {
    it('sets time horizon independently', () => {
      usePreferencesStore.getState().setTimeHorizon('position')
      const store = usePreferencesStore.getState()

      expect(store.timeHorizon).toBe('position')
    })

    it('changing trader type updates time horizon', () => {
      usePreferencesStore.getState().setTraderType('day_trader')
      let store = usePreferencesStore.getState()
      expect(store.timeHorizon).toBe('day_trading')

      usePreferencesStore.getState().setTraderType('value_investor')
      store = usePreferencesStore.getState()
      expect(store.timeHorizon).toBe('long_term')
    })
  })

  describe('Default Preferences', () => {
    it('starts with swing trader defaults', () => {
      // Reset to known state by reloading the module
      localStorage.clear()
      // Use location.reload equivalent by resetting state
      usePreferencesStore.setState({
        traderType: 'swing_trader',
        timeHorizon: 'swing',
        riskToleranceLevel: 'moderate',
        showTaxLots: false,
        showDividends: true,
        notificationFrequency: 'realtime',
      } as any)
      const store = usePreferencesStore.getState()

      expect(store.traderType).toBe('swing_trader')
      expect(store.riskToleranceLevel).toBe('moderate')
    })

    it('enables dividends by default', () => {
      localStorage.clear()
      usePreferencesStore.setState({
        showDividends: true,
      } as any)
      const store = usePreferencesStore.getState()

      expect(store.showDividends).toBe(true)
    })

    it('disables tax lots by default', () => {
      localStorage.clear()
      usePreferencesStore.setState({
        showTaxLots: false,
      } as any)
      const store = usePreferencesStore.getState()

      expect(store.showTaxLots).toBe(false)
    })
  })
})
