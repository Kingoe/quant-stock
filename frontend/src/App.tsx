import { useState } from 'react'
import Overview from './pages/Overview'
import Rebalance from './pages/Rebalance'
import Factors from './pages/Factors'
import Backtest from './pages/Backtest'
import Config from './pages/Config'
import Status from './pages/Status'
import Experiments from './pages/Experiments'
import Notifications from './pages/Notifications'
import BrokerReadiness from './pages/BrokerReadiness'
import './index.css'

type Page =
  | 'overview'
  | 'rebalance'
  | 'factors'
  | 'backtest'
  | 'config'
  | 'status'
  | 'experiments'
  | 'notifications'
  | 'broker-readiness'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('overview')

  const renderPage = () => {
    switch (currentPage) {
      case 'overview':
        return <Overview />
      case 'rebalance':
        return <Rebalance />
      case 'factors':
        return <Factors />
      case 'backtest':
        return <Backtest />
      case 'config':
        return <Config />
      case 'status':
        return <Status />
      case 'experiments':
        return <Experiments />
      case 'notifications':
        return <Notifications />
      case 'broker-readiness':
        return <BrokerReadiness />
      default:
        return <Overview />
    }
  }

  const navItems = [
    { key: 'overview' as Page, label: '总览' },
    { key: 'rebalance' as Page, label: '本周调仓' },
    { key: 'factors' as Page, label: '因子评分' },
    { key: 'backtest' as Page, label: '回测分析' },
    { key: 'config' as Page, label: '策略配置' },
    { key: 'status' as Page, label: '数据状态' },
    { key: 'experiments' as Page, label: '实验记录' },
    { key: 'notifications' as Page, label: '通知历史' },
    { key: 'broker-readiness' as Page, label: '券商准入' },
  ]

  return (
    <div className="flex min-h-screen flex-col bg-white md:flex-row">
      <aside className="w-full bg-gray-50 border-b border-gray-200 flex flex-col md:w-64 md:border-b-0 md:border-r">
        <div className="p-4 border-b border-gray-200 md:p-6">
          <h1 className="text-xl font-semibold text-gray-900">量化选股辅助系统</h1>
        </div>
        <nav className="p-3 md:flex-1 md:p-4">
          <ul className="flex gap-1 overflow-x-auto md:block md:space-y-1">
            {navItems.map((item) => (
              <li key={item.key} className="shrink-0 md:shrink">
                <button
                  onClick={() => setCurrentPage(item.key)}
                  className={`w-full whitespace-nowrap text-left px-4 py-2 rounded-lg transition-colors ${
                    currentPage === item.key
                      ? 'bg-indigo-50 text-indigo-600 font-medium'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
      <main className="flex-1 p-4 md:p-8">
        {renderPage()}
      </main>
    </div>
  )
}

export default App
