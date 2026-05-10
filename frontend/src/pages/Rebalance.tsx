function Rebalance() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">本周调仓</h2>

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
