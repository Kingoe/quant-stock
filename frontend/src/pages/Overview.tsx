import { useEffect, useState } from 'react'

import { getSimulationSummary } from '../services/api'

type SimulationSummary = Awaited<ReturnType<typeof getSimulationSummary>>['data']

const formatNumber = (value: number) => new Intl.NumberFormat('zh-CN').format(value)
const formatPercent = (value: number) => `${value.toFixed(2)}%`

function Overview() {
  const [simulation, setSimulation] = useState<SimulationSummary | null>(null)

  useEffect(() => {
    const fetchSimulation = async () => {
      const result = await getSimulationSummary()
      setSimulation(result.data)
    }

    fetchSimulation()
  }, [])

  const hasSimulationData = simulation !== null && simulation.latest_date !== null

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">总览</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-2">总收益率</div>
          <div className="text-3xl font-semibold text-gray-900">--%</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-2">年化收益率</div>
          <div className="text-3xl font-semibold text-gray-900">--%</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-2">最大回撤</div>
          <div className="text-3xl font-semibold text-gray-900">--%</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-2">夏普比率</div>
          <div className="text-3xl font-semibold text-gray-900">--</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-2">换手率</div>
          <div className="text-3xl font-semibold text-gray-900">--%</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-2">胜率</div>
          <div className="text-3xl font-semibold text-gray-900">--%</div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">净值曲线</h3>
        <div className="h-64 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
          暂无数据
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">模拟运行</h3>
          {simulation?.latest_date && (
            <span className="text-sm text-gray-500">最新日期：{simulation.latest_date}</span>
          )}
        </div>

        {!simulation && (
          <div className="h-32 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
            加载中
          </div>
        )}

        {simulation && !hasSimulationData && (
          <div className="h-32 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
            暂无模拟运行数据
          </div>
        )}

        {simulation && hasSimulationData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="border border-gray-100 rounded-lg p-4">
              <div className="text-sm text-gray-500 mb-2">模拟总资产</div>
              <div className="text-2xl font-semibold text-gray-900">
                {formatNumber(simulation.account.latest_value)}
              </div>
            </div>
            <div className="border border-gray-100 rounded-lg p-4">
              <div className="text-sm text-gray-500 mb-2">模拟收益</div>
              <div className="text-2xl font-semibold text-gray-900">
                {formatPercent(simulation.account.total_return)}
              </div>
            </div>
            <div className="border border-gray-100 rounded-lg p-4">
              <div className="text-sm text-gray-500 mb-2">最大回撤</div>
              <div className="text-2xl font-semibold text-gray-900">
                {formatPercent(simulation.performance.max_drawdown)}
              </div>
            </div>
            <div className="border border-gray-100 rounded-lg p-4">
              <div className="text-sm text-gray-500 mb-2">信号执行</div>
              <div className="text-2xl font-semibold text-gray-900">
                {simulation.execution.executed_signals} / {simulation.execution.total_signals}
              </div>
              <div className="mt-2 text-sm text-gray-500">
                待执行 {simulation.execution.pending_signals} 条
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Overview
