# 开发环境

本文档定义本项目的本地开发环境、启动方式、测试命令和工具选择。后续如果工具链变化，必须同步更新本文档。

## 1. 推荐环境

### 后端

- Python：3.11 或 3.12
- 包管理：uv 优先；如果本机没有 uv，可临时使用 pip
- API 框架：FastAPI
- 测试：pytest
- 代码检查：ruff

### 前端

- Node.js：20 LTS 或更高 LTS 版本
- 包管理：npm
- 构建工具：Vite
- 前端框架：React + TypeScript
- 测试：vitest
- 代码检查：eslint
- 格式化：prettier

## 2. 目录约定

```text
backend/    # Python 后端
frontend/   # React 前端
data/       # 本地数据库、导出文件、原始数据缓存
docs/       # 项目文档
scripts/    # 辅助脚本
```

## 3. 后端开发命令

后端初始化后，推荐命令如下：

```text
cd backend
uv sync
uv run pytest
uv run ruff check .
uv run ruff format .
uv run uvicorn app.main:app --reload
```

如果暂时不用 uv，可以使用：

```text
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload
```

## 4. 前端开发命令

前端初始化后，推荐命令如下：

```text
cd frontend
npm install
npm run dev
npm test
npm run build
npm run lint
```

## 5. 本地数据目录

本地数据默认放在：

```text
data/
  quant.db
  exports/
  raw/
```

约束：

- `data/quant.db` 是本地运行产物，不应提交到 Git。
- `data/raw/` 可用于缓存原始数据，不应默认提交到 Git。
- 测试数据应放在测试 fixtures 目录中，不能依赖实时行情。

## 6. 验证门禁

后端功能完成前至少运行：

```text
cd backend
uv run pytest
uv run ruff check .
```

前端功能完成前至少运行：

```text
cd frontend
npm test
npm run build
npm run lint
```

如果某个命令因为环境尚未初始化无法运行，必须在最终说明和 `docs/CHANGELOG.md` 中说明原因。

## 7. 版本控制约定

- 每轮迭代完成后提交 Git。
- 提交前确认任务规划和更新日志已经同步。
- 数据库、缓存、日志、构建产物、虚拟环境不得提交。
- 一次提交只包含同一轮迭代相关改动。
