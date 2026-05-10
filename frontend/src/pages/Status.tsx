import { useEffect, useState } from 'react'
import { getDataStatus } from '../services/api'

function Status() {
  const [dataStatus, setDataStatus] = useState<{
    daily_prices: { latest_date: string | null; has_data: boolean }
    valuation_metrics: { latest_date: string | null; has_data: boolean }
    financial_metrics: { latest_date: string | null; has_data: boolean }
    stock_info: { latest_date: string | null; has_data: boolean }
  } | null>(null)

  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const result = await getDataStatus()
        if (result.data && 'meta' in result) {
          setDataStatus(result.data)
        }
      } catch (error) {
        console.error('Failed to fetch data status:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">数据状态</h2>

      {loading && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-gray-900"></div>
          </div>
        </div>
      )}

      {!loading && dataStatus && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-sm text-gray-500 mb-2">日行情</div>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-semibold text-gray-900">{dataStatus.daily_prices.has_data ? '√' : '—'}</span>
              {dataStatus.daily_prices.latest_date && (
                <span className="text-sm text-gray-500">最新日期: {dataStatus.daily_prices.latest_date}</span>
              )}
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-sm text-gray-500 mb-2">估值指标</div>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-semibold text-gray-900">{dataStatus.valuation_metrics.has_data ? '√' : '—'}</span>
              {dataStatus.valuation_metrics.latest_date && (
                <span className="text-sm text-gray-500">最新日期: {dataStatus.valuation_metrics.latest_date}</span>
              )}
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-sm text-gray-500 mb-2">财务指标</div>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-semibold text-gray-900">{dataStatus.financial_metrics.has_data ? '√' : '—'}</span>
              {dataStatus.financial_metrics.latest_date && (
                <span className="text-sm text-gray-500">最新日期: {dataStatus.financial_metrics.latest_date}</span>
              )}
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-sm text-gray-500 mb-2">股票信息</div>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-semibold text-gray-900">{dataStatus.stock_info.has_data ? '√' : '—'}</span>
              {dataStatus.stock_info.latest_date && (
                <span className="text-sm text-gray-500">最新日期: {dataStatus.stock_info.latest_date}</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Status
