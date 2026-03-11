/**
 * Earnings Calendar Component
 * Displays upcoming earnings events and news for tracked symbols
 */

import { useState, useMemo } from 'react'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Badge } from '@components/common/Badge'
import { formatDate, formatTime } from '@utils/formatting'
import { Calendar, TrendingUp, Newspaper } from 'lucide-react'
import classNames from 'classnames'

interface CalendarEvent {
  date: Date
  symbol: string
  type: 'earnings' | 'news'
  title: string
  description: string
  impact?: 'high' | 'medium' | 'low'
}

interface EarningsCalendarProps {
  events?: CalendarEvent[]
  isLoading?: boolean
  onEventClick?: (event: CalendarEvent) => void
  watchlistSymbols?: string[]
}

export const EarningsCalendar: React.FC<EarningsCalendarProps> = ({
  events = [],
  isLoading = false,
  onEventClick,
}) => {
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [filterType, setFilterType] = useState<'all' | 'earnings' | 'news'>('all')

  // Filter and sort events
  const filteredEvents = useMemo(() => {
    let filtered = events

    if (filterType !== 'all') {
      filtered = filtered.filter(e => e.type === filterType)
    }

    if (selectedDate) {
      filtered = filtered.filter(
        e => formatDate(e.date) === formatDate(selectedDate)
      )
    }

    // Only show future events and today
    const now = new Date()
    now.setHours(0, 0, 0, 0)
    filtered = filtered.filter(e => {
      const eventDate = new Date(e.date)
      eventDate.setHours(0, 0, 0, 0)
      return eventDate >= now
    })

    return filtered.sort((a, b) => a.date.getTime() - b.date.getTime())
  }, [events, filterType, selectedDate])

  // Get upcoming dates with events
  const upcomingDates = useMemo(() => {
    const dates = new Set<string>()
    const now = new Date()
    now.setHours(0, 0, 0, 0)

    events.forEach(event => {
      const eventDate = new Date(event.date)
      eventDate.setHours(0, 0, 0, 0)
      if (eventDate >= now) {
        dates.add(formatDate(eventDate))
      }
    })

    return dates
  }, [events])

  // Get next 7 days
  const nextDays = useMemo(() => {
    const days = []
    const today = new Date()

    for (let i = 0; i < 7; i++) {
      const date = new Date(today)
      date.setDate(date.getDate() + i)
      days.push(date)
    }

    return days
  }, [])

  const handleDateClick = (date: Date) => {
    const dateStr = formatDate(date)
    const selectedDateStr = selectedDate ? formatDate(selectedDate) : null
    setSelectedDate(dateStr === selectedDateStr ? null : date)
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Earnings & News Calendar
          </h3>
        </CardHeader>
        <CardBody>
          <div className="animate-pulse h-64 bg-neutral-100 dark:bg-neutral-700 rounded-lg" />
        </CardBody>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Earnings & News Calendar
          </h3>
          <div className="flex gap-2">
            {['all', 'earnings', 'news'].map(type => (
              <button
                key={type}
                onClick={() => setFilterType(type as 'all' | 'earnings' | 'news')}
                className={classNames(
                  'px-3 py-1 text-xs font-medium rounded transition-colors',
                  filterType === type
                    ? 'bg-accent-600 text-white dark:bg-accent-500'
                    : 'bg-neutral-200 text-neutral-900 hover:bg-neutral-300 dark:bg-neutral-700 dark:text-neutral-100 dark:hover:bg-neutral-600'
                )}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>

      <CardBody className="space-y-4">
        {/* Quick Date Selector - Next 7 Days */}
        <div>
          <p className="text-xs font-medium text-neutral-600 dark:text-neutral-400 mb-2 uppercase tracking-wide">
            Next 7 Days
          </p>
          <div className="grid grid-cols-7 gap-2">
            {nextDays.map(date => {
              const dateStr = formatDate(date)
              const hasEvents = upcomingDates.has(dateStr)
              const isSelected = selectedDate && formatDate(selectedDate) === dateStr
              const isToday = formatDate(new Date()) === dateStr

              return (
                <button
                  key={dateStr}
                  onClick={() => handleDateClick(date)}
                  className={classNames(
                    'p-2 rounded text-xs font-medium transition-colors text-center',
                    isSelected
                      ? 'bg-accent-600 text-white dark:bg-accent-500'
                      : isToday
                      ? 'bg-blue-100 text-blue-900 dark:bg-blue-900/30 dark:text-blue-300 border border-blue-300'
                      : hasEvents
                      ? 'bg-neutral-200 text-neutral-900 dark:bg-neutral-700 dark:text-neutral-100 border border-orange-400'
                      : 'bg-neutral-100 text-neutral-700 dark:bg-neutral-700/50 dark:text-neutral-300'
                  )}
                >
                  <div className="text-xs">{date.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                  <div className="font-bold">{date.getDate()}</div>
                  {hasEvents && <div className="w-1 h-1 bg-orange-500 rounded-full mx-auto mt-1" />}
                </button>
              )
            })}
          </div>
        </div>

        {/* Events List */}
        <div className="border-t border-neutral-200 dark:border-neutral-700 pt-4">
          {filteredEvents.length === 0 ? (
            <div className="text-center py-6 text-neutral-500">
              <Calendar className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">
                {selectedDate
                  ? 'No events on this date'
                  : 'No upcoming events'}
              </p>
            </div>
          ) : (
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {filteredEvents.map((event, index) => (
                <button
                  key={`${event.date.getTime()}-${event.symbol}-${index}`}
                  onClick={() => onEventClick?.(event)}
                  className="w-full text-left p-3 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-700/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {event.type === 'earnings' ? (
                          <TrendingUp className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        ) : (
                          <Newspaper className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
                        )}
                        <Badge
                          variant={event.type === 'earnings' ? 'success' : 'info'}
                          size="sm"
                        >
                          {event.symbol}
                        </Badge>
                        {event.impact && (
                          <Badge
                            variant={
                              event.impact === 'high'
                                ? 'danger'
                                : event.impact === 'medium'
                                ? 'warning'
                                : 'info'
                            }
                            size="sm"
                          >
                            {event.impact.charAt(0).toUpperCase() + event.impact.slice(1)} Impact
                          </Badge>
                        )}
                      </div>
                      <h4 className="font-medium text-neutral-900 dark:text-neutral-100 mb-1">
                        {event.title}
                      </h4>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400">
                        {event.description}
                      </p>
                    </div>
                    <div className="text-xs text-neutral-500 dark:text-neutral-400 whitespace-nowrap">
                      <div className="font-medium">
                        {event.date.toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                        })}
                      </div>
                      <div className="text-xs">
                        {formatTime(event.date.getTime())}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Summary Stats */}
        {filteredEvents.length > 0 && (
          <div className="grid grid-cols-2 gap-2 border-t border-neutral-200 dark:border-neutral-700 pt-4">
            <div className="p-2 bg-neutral-100 dark:bg-neutral-700/50 rounded">
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Total Events</p>
              <p className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
                {filteredEvents.length}
              </p>
            </div>
            <div className="p-2 bg-neutral-100 dark:bg-neutral-700/50 rounded">
              <p className="text-xs text-neutral-600 dark:text-neutral-400">This Week</p>
              <p className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
                {filteredEvents.filter(e => {
                  const today = new Date()
                  const weekEnd = new Date(today)
                  weekEnd.setDate(weekEnd.getDate() + 7)
                  return e.date >= today && e.date <= weekEnd
                }).length}
              </p>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  )
}
