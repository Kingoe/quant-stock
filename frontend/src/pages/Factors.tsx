function Factors() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">因子评分</h2>

      <div className="flex gap-4">
        <input
          type="text"
          placeholder="搜索股票代码或名称"
          className="flex-1 max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="h-64 flex items-center justify-center text-gray-400 border-b border-gray-200">
          暂无数据
        </div>
      </div>
    </div>
  )
}

export default Factors
