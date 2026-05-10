from __future__ import annotations


def test_scheduler_add_daily_job() -> None:
    """测试添加每日任务。"""
    from app.scheduler import Scheduler

    scheduler = Scheduler()

    def dummy_task() -> None:
        pass

    scheduler.add_daily_job(dummy_task, hour=9, minute=30, id="test_daily")

    assert len(scheduler._scheduler.get_jobs()) == 1
    job = scheduler._scheduler.get_jobs()[0]
    assert job.id == "test_daily"


def test_scheduler_add_weekly_job() -> None:
    """测试添加每周任务。"""
    from app.scheduler import Scheduler

    scheduler = Scheduler()

    def dummy_task() -> None:
        pass

    scheduler.add_weekly_job(dummy_task, day_of_week=4, hour=15, minute=0, id="test_weekly")

    assert len(scheduler._scheduler.get_jobs()) == 1
    job = scheduler._scheduler.get_jobs()[0]
    assert job.id == "test_weekly"


def test_scheduler_start_and_shutdown() -> None:
    """测试启动和关闭调度器。"""
    from app.scheduler import Scheduler

    scheduler = Scheduler()

    assert not scheduler._scheduler.running

    scheduler.start()
    assert scheduler._scheduler.running

    scheduler.shutdown()
    assert not scheduler._scheduler.running


def test_scheduler_multiple_jobs() -> None:
    """测试添加多个任务。"""
    from app.scheduler import Scheduler

    scheduler = Scheduler()

    def dummy_task() -> None:
        pass

    scheduler.add_daily_job(dummy_task, hour=9, minute=30, id="daily_1")
    scheduler.add_daily_job(dummy_task, hour=10, minute=0, id="daily_2")
    scheduler.add_weekly_job(dummy_task, day_of_week=4, hour=15, minute=0, id="weekly_1")

    assert len(scheduler._scheduler.get_jobs()) == 3


def test_global_scheduler_instance() -> None:
    """测试全局调度器实例。"""
    from app.scheduler import Scheduler, scheduler

    assert isinstance(scheduler, Scheduler)
    assert hasattr(scheduler, "_scheduler")
