function Backtest() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">回测分析</h2>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="h-64 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
          暂无数据
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">净值曲线</h3>
        <div className="h-64 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
          暂无数据
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">回撤曲线</h3>
        <div className="h-64 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg">
          暂无数据
        </div>
      </div>
    </div>
  )
}

export default Backtest
