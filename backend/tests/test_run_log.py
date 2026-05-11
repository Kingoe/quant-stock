from __future__ import annotations


def test_create_run_log() -> None:
    """测试创建运行日志。"""
    from app.run_log import create_run_log
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        log = create_run_log(connection, "test_task")

        assert log.id is not None
        assert log.task_type == "test_task"
        assert log.status.value == "pending"
        assert log.started_at is not None
        assert log.finished_at is None


def test_update_run_log_status() -> None:
    """测试更新运行日志状态。"""
    from app.run_log import RunStatus, create_run_log, update_run_log_status
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        log = create_run_log(connection, "test_task")
        update_run_log_status(connection, log.id, RunStatus.SUCCESS)

        updated_log = connection.execute(
            "select * from run_logs where id = ?",
            (log.id,),
        ).fetchone()

        assert updated_log["status"] == "success"
        assert updated_log["finished_at"] is not None


def test_update_run_log_with_error() -> None:
    """测试更新运行日志错误信息。"""
    from app.run_log import RunStatus, create_run_log, update_run_log_status
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        log = create_run_log(connection, "test_task")
        update_run_log_status(
            connection,
            log.id,
            RunStatus.FAILED,
            error_message="Task failed",
        )

        updated_log = connection.execute(
            "select * from run_logs where id = ?",
            (log.id,),
        ).fetchone()

        assert updated_log["status"] == "failed"
        assert updated_log["error_message"] == "Task failed"


def test_update_run_log_with_result() -> None:
    """测试更新运行日志结果。"""
    from app.run_log import RunStatus, create_run_log, update_run_log_status
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        log = create_run_log(connection, "test_task")
        result = {"stocks_count": 10, "total_score": 0.75}
        update_run_log_status(
            connection,
            log.id,
            RunStatus.SUCCESS,
            result=result,
        )

        updated_log = connection.execute(
            "select * from run_logs where id = ?",
            (log.id,),
        ).fetchone()

        import json

        assert json.loads(updated_log["result"]) == result


def test_get_recent_run_logs() -> None:
    """测试获取最近的运行日志。"""
    from app.run_log import create_run_log, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        log1 = create_run_log(connection, "task_1")
        log2 = create_run_log(connection, "task_2")
        log3 = create_run_log(connection, "task_1")

        logs = get_recent_run_logs(connection, limit=10)

        assert len(logs) == 3
        assert logs[0].id == log3.id
        assert logs[1].id == log2.id
        assert logs[2].id == log1.id


def test_get_recent_run_logs_with_task_type_filter() -> None:
    """测试按任务类型筛选运行日志。"""
    from app.run_log import create_run_log, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        create_run_log(connection, "task_1")
        create_run_log(connection, "task_2")
        create_run_log(connection, "task_1")

        logs = get_recent_run_logs(connection, limit=10, task_type="task_1")

        assert len(logs) == 2
        assert all(log.task_type == "task_1" for log in logs)


def test_get_recent_run_logs_with_status_filter() -> None:
    """测试按运行状态筛选运行日志。"""
    from app.run_log import RunStatus, create_run_log, get_recent_run_logs, update_run_log_status
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        success_log = create_run_log(connection, "data_update")
        update_run_log_status(connection, success_log.id, RunStatus.SUCCESS)
        failed_log = create_run_log(connection, "data_update")
        update_run_log_status(connection, failed_log.id, RunStatus.FAILED)
        create_run_log(connection, "data_update")

        logs = get_recent_run_logs(connection, limit=10, status=RunStatus.FAILED)

        assert len(logs) == 1
        assert logs[0].id == failed_log.id
        assert logs[0].status == RunStatus.FAILED


def test_get_recent_run_logs_with_limit() -> None:
    """测试限制返回数量。"""
    from app.run_log import create_run_log, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        for _ in range(10):
            create_run_log(connection, "test_task")

        logs = get_recent_run_logs(connection, limit=5)

        assert len(logs) == 5


def test_run_status_enum() -> None:
    """测试运行状态枚举。"""
    from app.run_log import RunStatus

    assert RunStatus.PENDING.value == "pending"
    assert RunStatus.RUNNING.value == "running"
    assert RunStatus.SUCCESS.value == "success"
    assert RunStatus.FAILED.value == "failed"
