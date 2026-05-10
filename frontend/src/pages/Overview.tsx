function Overview() {
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
    </div>
  )
}

export default Overview
