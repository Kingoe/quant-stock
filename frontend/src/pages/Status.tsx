import { useEffect, useState } from 'react'
import { getDataStatus, getDataUpdateLogs, type DataUpdateLogData } from '../services/api'

function Status() {
  const [dataStatus, setDataStatus] = useState<{
    daily_prices: { latest_date: string | null; has_data: boolean }
    valuation_metrics: { latest_date: string | null; has_data: boolean }
    financial_metrics: { latest_date: string | null; has_data: boolean }
    stock_info: { latest_date: string | null; has_data: boolean }
  } | null>(null)
  const [updateLogs, setUpdateLogs] = useState<DataUpdateLogData[]>([])
  const [logStatusFilter, setLogStatusFilter] = useState('all')

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

  useEffect(() => {
    const fetchLogs = async () => {
      const logsResult = await getDataUpdateLogs(
        logStatusFilter === 'all' ? undefined : logStatusFilter,
      )
      setUpdateLogs(logsResult.data)
    }

    fetchLogs()
  }, [logStatusFilter])

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

      {!loading && (
        <section className="bg-white border border-gray-200 rounded-lg">
          <div className="px-4 py-5 border-b border-gray-200 flex flex-col gap-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">数据更新日志</h3>
              <p className="text-sm text-gray-500 mt-1">最近 20 条手动数据更新任务</p>
            </div>
            <div className="grid grid-cols-2 gap-1 rounded-lg border border-gray-200 bg-gray-50 p-1 sm:inline-flex">
              {[
                { value: 'all', label: '全部' },
                { value: 'success', label: '成功' },
                { value: 'failed', label: '失败' },
                { value: 'running', label: '运行中' },
              ].map((item) => (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => setLogStatusFilter(item.value)}
                  className={`whitespace-nowrap px-3 py-1.5 text-sm rounded-md transition-colors ${
                    logStatusFilter === item.value
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {updateLogs.length === 0 ? (
            <div className="px-6 py-10 text-center text-sm text-gray-500">暂无数据更新记录</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">数据类型</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">数据源</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">更新数量</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">开始时间</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">结束时间</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">错误信息</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {updateLogs.map((log) => (
                    <tr key={log.id ?? `${log.started_at}-${log.status}`}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                            log.status === 'success'
                              ? 'bg-emerald-50 text-emerald-700'
                              : log.status === 'failed'
                                ? 'bg-rose-50 text-rose-700'
                                : 'bg-amber-50 text-amber-700'
                          }`}
                        >
                          {statusLabel(log.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {log.result.data_type ?? '未知'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {log.result.source ?? '未知'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {typeof log.result.records_count === 'number' ? `${log.result.records_count} 条` : '—'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {log.started_at ?? '—'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {log.finished_at ?? '—'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {log.error_message ?? '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  )
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    success: '成功',
    failed: '失败',
  }
  return labels[status] ?? status
}

export default Status
