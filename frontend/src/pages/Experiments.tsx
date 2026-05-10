import { useEffect, useMemo, useState } from 'react'

import { getExperiments, type ParameterExperimentData } from '../services/api'

function formatPercent(value: unknown): string {
  return typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : '—'
}

function formatNumber(value: unknown): string {
  return typeof value === 'number' ? value.toFixed(2) : '—'
}

function compactJson(value: Record<string, unknown>): string {
  const text = JSON.stringify(value, null, 2)
  return text.length > 220 ? `${text.slice(0, 220)}...` : text
}

function Experiments() {
  const [experiments, setExperiments] = useState<ParameterExperimentData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchExperiments = async () => {
      setLoading(true)
      const result = await getExperiments()
      setExperiments(result.data)
      setLoading(false)
    }

    fetchExperiments()
  }, [])

  const latestExperiment = useMemo(() => experiments[0] ?? null, [experiments])

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">实验记录</h2>
          <p className="mt-2 text-sm text-gray-500">
            复盘参数变化、核心指标和备注，避免凭感觉反复调参。
          </p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-right">
          <div className="text-xs text-gray-500">记录数</div>
          <div className="text-2xl font-semibold text-gray-900">{experiments.length}</div>
        </div>
      </div>

      {loading && (
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <div className="h-40 flex items-center justify-center text-gray-400">加载中</div>
        </div>
      )}

      {!loading && experiments.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white p-10 text-center">
          <div className="text-base font-medium text-gray-900">暂无实验记录</div>
          <div className="mt-2 text-sm text-gray-500">后续运行参数实验后会在这里展示。</div>
        </div>
      )}

      {!loading && experiments.length > 0 && (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
          <div className="rounded-lg border border-gray-200 bg-white">
            <div className="border-b border-gray-200 px-6 py-4">
              <h3 className="text-lg font-semibold text-gray-900">最近实验</h3>
            </div>
            <div className="divide-y divide-gray-100">
              {experiments.map((experiment) => (
                <article key={experiment.experiment_id} className="px-6 py-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h4 className="text-base font-semibold text-gray-900">{experiment.name}</h4>
                      <p className="mt-1 text-sm text-gray-500">
                        {experiment.description ?? '无实验说明'}
                      </p>
                    </div>
                    <span className="rounded-md bg-gray-100 px-2.5 py-1 text-xs text-gray-600">
                      {experiment.created_at}
                    </span>
                  </div>

                  <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
                    <div className="rounded-lg bg-gray-50 p-3">
                      <div className="text-xs text-gray-500">年化收益</div>
                      <div className="mt-1 text-lg font-semibold text-gray-900">
                        {formatPercent(experiment.metrics.annual_return)}
                      </div>
                    </div>
                    <div className="rounded-lg bg-gray-50 p-3">
                      <div className="text-xs text-gray-500">最大回撤</div>
                      <div className="mt-1 text-lg font-semibold text-gray-900">
                        {formatPercent(experiment.metrics.max_drawdown)}
                      </div>
                    </div>
                    <div className="rounded-lg bg-gray-50 p-3">
                      <div className="text-xs text-gray-500">Sharpe</div>
                      <div className="mt-1 text-lg font-semibold text-gray-900">
                        {formatNumber(experiment.metrics.sharpe)}
                      </div>
                    </div>
                  </div>

                  {experiment.notes && (
                    <p className="mt-4 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-600">
                      {experiment.notes}
                    </p>
                  )}
                </article>
              ))}
            </div>
          </div>

          <aside className="rounded-lg border border-gray-200 bg-white">
            <div className="border-b border-gray-200 px-6 py-4">
              <h3 className="text-lg font-semibold text-gray-900">参数详情</h3>
            </div>
            {latestExperiment && (
              <div className="space-y-4 p-6">
                <div>
                  <div className="text-xs text-gray-500">当前展示</div>
                  <div className="mt-1 text-base font-semibold text-gray-900">
                    {latestExperiment.name}
                  </div>
                </div>
                <pre className="max-h-80 overflow-auto rounded-lg bg-gray-950 p-4 text-xs leading-5 text-gray-100">
                  {compactJson(latestExperiment.parameters)}
                </pre>
                <pre className="max-h-60 overflow-auto rounded-lg bg-gray-50 p-4 text-xs leading-5 text-gray-700">
                  {compactJson(latestExperiment.metrics)}
                </pre>
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  )
}

export default Experiments
