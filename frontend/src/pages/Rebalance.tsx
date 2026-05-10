import { useState } from 'react'

import { runWeeklyStrategy } from '../services/api'

function Rebalance() {
  const [isRunning, setIsRunning] = useState(false)
  const [runMessage, setRunMessage] = useState<string | null>(null)

  const handleRunWeeklyStrategy = async () => {
    setIsRunning(true)
    setRunMessage(null)

    const result = await runWeeklyStrategy()

    if (result.data.status === 'success') {
      setRunMessage(`运行成功，生成 ${result.data.recommendations_count} 条建议`)
    } else {
      setRunMessage(`运行失败：${result.data.error_message ?? '请检查数据和后端服务'}`)
    }

    setIsRunning(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold text-gray-900">本周调仓</h2>
        <button
          type="button"
          onClick={handleRunWeeklyStrategy}
          disabled={isRunning}
          className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          {isRunning ? '运行中...' : '运行本周策略'}
        </button>
      </div>

      {runMessage && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700">
          {runMessage}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center justify-between">
            买入
            <span className="text-sm text-gray-500">5 只</span>
          </h3>
          <div className="space-y-2">
            <div className="h-64 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
              暂无数据
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center justify-between">
            卖出
            <span className="text-sm text-gray-500">2 只</span>
          </h3>
          <div className="space-y-2">
            <div className="h-64 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
              暂无数据
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center justify-between">
            持有
            <span className="text-sm text-gray-500">8 只</span>
          </h3>
          <div className="space-y-2">
            <div className="h-64 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
              暂无数据
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center justify-between">
            观察
            <span className="text-sm text-gray-500">10 只</span>
          </h3>
          <div className="space-y-2">
            <div className="h-64 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
              暂无数据
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Rebalance
