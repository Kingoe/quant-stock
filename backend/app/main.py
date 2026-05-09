from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI

app = FastAPI(title="Quant Stock Backend")


@app.get("/api/health")
def health_check() -> dict[str, dict[str, str]]:
    return {
        "data": {
            "status": "ok",
            "service": "quant-stock-backend",
        },
        "meta": {
            "request_id": "local-dev",
            "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        },
    }
