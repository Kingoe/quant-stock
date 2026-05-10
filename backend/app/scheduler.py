from __future__ import annotations

from collections.abc import Callable

from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:
    """定时任务调度器。"""

    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler()

    def add_daily_job(
        self,
        func: Callable[..., object],
        hour: int,
        minute: int = 0,
        id: str | None = None,
    ) -> None:
        """添加每日定时任务。

        Args:
            func: 要执行的函数
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            id: 任务 ID
        """
        self._scheduler.add_job(
            func,
            "cron",
            hour=hour,
            minute=minute,
            id=id,
        )

    def add_weekly_job(
        self,
        func: Callable[..., object],
        day_of_week: int,
        hour: int,
        minute: int = 0,
        id: str | None = None,
    ) -> None:
        """添加每周定时任务。

        Args:
            func: 要执行的函数
            day_of_week: 星期几 (0-6, 0=周一, 6=周日)
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            id: 任务 ID
        """
        self._scheduler.add_job(
            func,
            "cron",
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
            id=id,
        )

    def start(self) -> None:
        """启动调度器。"""
        if not self._scheduler.running:
            self._scheduler.start()

    def shutdown(self) -> None:
        """关闭调度器。"""
        if self._scheduler.running:
            self._scheduler.shutdown()


scheduler = Scheduler()
