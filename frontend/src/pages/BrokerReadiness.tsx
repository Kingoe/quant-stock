import { useEffect, useMemo, useState } from 'react'

import { getBrokerReadiness, type BrokerReadinessData } from '../services/api'

const emptyReadiness: BrokerReadinessData = {
  status: 'blocked',
  ready_for_manual_pilot: false,
  failed_reasons: [],
  allowed_actions: [],
  trade_boundary: '不是实盘交易入口，仅用于人工小资金试点评审。',
}

function actionLabel(action: string): string {
  const labels: Record<string, string> = {
    read_account: '读取账户概览',
    read_positions: '读取持仓',
    read_orders: '读取委托记录',
  }

  return labels[action] ?? action
}

function BrokerReadiness() {
  const [readiness, setReadiness] = useState<BrokerReadinessData>(emptyReadiness)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchReadiness = async () => {
      setLoading(true)
      const result = await getBrokerReadiness()
      setReadiness(result.data)
      setLoading(false)
    }

    fetchReadiness()
  }, [])

  const statusText = readiness.ready_for_manual_pilot ? '可进入人工试点评审' : '不可进入试点评审'
  const statusClass = readiness.ready_for_manual_pilot
    ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
    : 'border-amber-200 bg-amber-50 text-amber-700'

  const checklist = useMemo(
    () => [
      { label: '模拟运行不少于 60 天', failed: readiness.failed_reasons.includes('模拟运行天数不足') },
      { label: '最大回撤不超过阈值', failed: readiness.failed_reasons.includes('最大回撤超过阈值') },
      { label: '最近运行没有失败记录', failed: readiness.failed_reasons.includes('存在失败运行记录') },
      { label: '通知渠道已经启用', failed: readiness.failed_reasons.includes('通知渠道未启用') },
      { label: '人工确认开关已经启用', failed: readiness.failed_reasons.includes('人工确认开关未启用') },
      { label: '模拟交易流程已经验证', failed: readiness.failed_reasons.includes('模拟交易验证未完成') },
    ],
    [readiness.failed_reasons],
  )

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">券商准入评估</h2>
          <p className="mt-2 text-sm text-gray-500">
            评估策略是否具备进入人工小资金试点评审的条件，并明确只读动作边界。
          </p>
        </div>
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-right">
          <div className="text-xs text-rose-600">交易边界</div>
          <div className="text-xl font-semibold text-rose-700">不自动下单</div>
        </div>
      </div>

      {loading && (
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <div className="h-40 flex items-center justify-center text-gray-400">加载中</div>
        </div>
      )}

      {!loading && (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.8fr)]">
          <section className="space-y-6">
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="text-xs text-gray-500">当前状态</div>
                  <div className="mt-2 text-2xl font-semibold text-gray-900">
                    {readiness.status}
                  </div>
                </div>
                <span className={`rounded-md border px-3 py-1.5 text-sm font-medium ${statusClass}`}>
                  {statusText}
                </span>
              </div>
              <p className="mt-5 rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700">
                {readiness.trade_boundary}
              </p>
            </div>

            <div className="rounded-lg border border-gray-200 bg-white">
              <div className="border-b border-gray-200 px-6 py-4">
                <h3 className="text-lg font-semibold text-gray-900">准入条件</h3>
              </div>
              <div className="divide-y divide-gray-100">
                {checklist.map((item) => (
                  <div key={item.label} className="flex items-center justify-between gap-4 px-6 py-4">
                    <span className="text-sm text-gray-700">{item.label}</span>
                    <span
                      className={`rounded-md px-2.5 py-1 text-xs font-medium ${
                        item.failed ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'
                      }`}
                    >
                      {item.failed ? '待满足' : '已满足'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <aside className="space-y-6">
            <div className="rounded-lg border border-gray-200 bg-white">
              <div className="border-b border-gray-200 px-6 py-4">
                <h3 className="text-lg font-semibold text-gray-900">失败原因</h3>
              </div>
              <div className="space-y-3 p-6">
                {readiness.failed_reasons.length === 0 && (
                  <div className="rounded-lg border border-dashed border-gray-300 p-4 text-sm text-gray-500">
                    暂无失败原因
                  </div>
                )}
                {readiness.failed_reasons.map((reason) => (
                  <div
                    key={reason}
                    className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800"
                  >
                    {reason}
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-gray-200 bg-white">
              <div className="border-b border-gray-200 px-6 py-4">
                <h3 className="text-lg font-semibold text-gray-900">允许动作</h3>
              </div>
              <div className="space-y-3 p-6">
                {readiness.allowed_actions.map((action) => (
                  <div key={action} className="rounded-lg bg-gray-50 px-3 py-3">
                    <div className="text-sm font-medium text-gray-900">{actionLabel(action)}</div>
                    <div className="mt-1 text-xs text-gray-500">{action}</div>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>
      )}
    </div>
  )
}

export default BrokerReadiness
