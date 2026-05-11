import { useEffect, useMemo, useState } from 'react'

import { getNotifications, type NotificationRecordData } from '../services/api'

function compactJson(value: Record<string, unknown>): string {
  const text = JSON.stringify(value, null, 2)
  return text.length > 260 ? `${text.slice(0, 260)}...` : text
}

function badgeClass(value: string): string {
  if (value === 'success') {
    return 'bg-emerald-50 text-emerald-700 ring-emerald-200'
  }

  if (value === 'failed' || value === 'error') {
    return 'bg-rose-50 text-rose-700 ring-rose-200'
  }

  if (value === 'warning') {
    return 'bg-amber-50 text-amber-700 ring-amber-200'
  }

  return 'bg-gray-100 text-gray-700 ring-gray-200'
}

function Notifications() {
  const [notifications, setNotifications] = useState<NotificationRecordData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchNotifications = async () => {
      setLoading(true)
      const result = await getNotifications()
      setNotifications(result.data)
      setLoading(false)
    }

    fetchNotifications()
  }, [])

  const latestNotification = useMemo(() => notifications[0] ?? null, [notifications])

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">通知历史</h2>
          <p className="mt-2 text-sm text-gray-500">
            汇总策略运行后的提醒记录，便于确认触达结果和失败原因。
          </p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-right">
          <div className="text-xs text-gray-500">通知数</div>
          <div className="text-2xl font-semibold text-gray-900">{notifications.length}</div>
        </div>
      </div>

      {loading && (
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <div className="h-40 flex items-center justify-center text-gray-400">加载中</div>
        </div>
      )}

      {!loading && notifications.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white p-10 text-center">
          <div className="text-base font-medium text-gray-900">暂无通知记录</div>
          <div className="mt-2 text-sm text-gray-500">后续策略运行产生通知后会在这里展示。</div>
        </div>
      )}

      {!loading && notifications.length > 0 && (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
          <div className="rounded-lg border border-gray-200 bg-white">
            <div className="border-b border-gray-200 px-6 py-4">
              <h3 className="text-lg font-semibold text-gray-900">最近通知</h3>
            </div>
            <div className="divide-y divide-gray-100">
              {notifications.map((notification) => (
                <article key={notification.id} className="px-6 py-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h4 className="text-base font-semibold text-gray-900">
                          {notification.title}
                        </h4>
                        <span className="rounded-md bg-gray-100 px-2.5 py-1 text-xs text-gray-600">
                          {notification.channel}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-gray-600">{notification.content}</p>
                    </div>
                    <span className="rounded-md bg-gray-100 px-2.5 py-1 text-xs text-gray-600">
                      {notification.created_at}
                    </span>
                  </div>

                  <div className="mt-4 flex flex-wrap items-center gap-2">
                    <span
                      className={`rounded-md px-2.5 py-1 text-xs font-medium ring-1 ${badgeClass(
                        notification.level,
                      )}`}
                    >
                      {notification.level}
                    </span>
                    <span
                      className={`rounded-md px-2.5 py-1 text-xs font-medium ring-1 ${badgeClass(
                        notification.status,
                      )}`}
                    >
                      状态 {notification.status}
                    </span>
                  </div>

                  {notification.error_message && (
                    <p className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
                      {notification.error_message}
                    </p>
                  )}
                </article>
              ))}
            </div>
          </div>

          <aside className="rounded-lg border border-gray-200 bg-white">
            <div className="border-b border-gray-200 px-6 py-4">
              <h3 className="text-lg font-semibold text-gray-900">元数据摘要</h3>
            </div>
            {latestNotification && (
              <div className="space-y-4 p-6">
                <div>
                  <div className="text-xs text-gray-500">当前展示</div>
                  <div className="mt-1 text-base font-semibold text-gray-900">
                    通知 #{latestNotification.id}
                  </div>
                </div>
                <pre className="max-h-80 overflow-auto rounded-lg bg-gray-950 p-4 text-xs leading-5 text-gray-100">
                  {compactJson(latestNotification.metadata)}
                </pre>
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  )
}

export default Notifications
