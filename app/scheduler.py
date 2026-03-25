from __future__ import annotations

from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler

from app.airports import airport_name
from app.config import settings
from app.db import (
    add_log,
    get_enabled_tasks,
    update_task_check_result,
    update_task_notified,
)
from app.services.notifier import send_wechat_message
from app.services.provider import query_lowest_price

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


def _should_notify(task: dict[str, Any], current_price: float) -> bool:
    target_price = float(task["target_price"])
    if current_price > target_price:
        return False

    last_notified = task["last_notified_price"]
    if last_notified is None:
        return True

    return abs(float(last_notified) - current_price) >= 50


def _task_to_dict(row: Any) -> dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def run_once() -> None:
    tasks = get_enabled_tasks()
    add_log("INFO", f"开始监控轮询，任务数: {len(tasks)}")

    for row in tasks:
        task = _task_to_dict(row)
        origin_name = airport_name(task["origin"])
        dest_name = airport_name(task["destination"])
        route = f"{origin_name}({task['origin']})->{dest_name}({task['destination']})"
        try:
            result = query_lowest_price(task)
            current_price = float(result["price"])
            flight_no = result.get("flight_no", "-")
            provider = result.get("provider", "unknown")
            update_task_check_result(task["id"], current_price)
            add_log(
                "INFO",
                f"任务#{task['id']} [{task['travel_date']}] {route} "
                f"| 当前价: {current_price:.0f}元 | 阈值: {float(task['target_price']):.0f}元 "
                f"| 航班: {flight_no} | 来源: {provider}",
            )

            if _should_notify(task, current_price):
                title = f"机票降价提醒 {origin_name}->{dest_name}"
                desp = (
                    f"航线: {origin_name}({task['origin']}) → {dest_name}({task['destination']})\n"
                    f"日期: {task['travel_date']}\n"
                    f"航班: {flight_no}\n"
                    f"当前价: {current_price:.0f} 元\n"
                    f"目标价: ≤ {float(task['target_price']):.0f} 元\n"
                    f"数据来源: {provider}"
                )
                ok, msg = send_wechat_message(title, desp)
                if ok:
                    update_task_notified(task["id"], current_price)
                    add_log("INFO", f"任务#{task['id']} 降价推送成功 | {origin_name}->{dest_name} {current_price:.0f}元")
                else:
                    add_log("ERROR", f"任务#{task['id']} 推送失败: {msg}")
            else:
                target = float(task["target_price"])
                if current_price > target:
                    add_log("INFO", f"任务#{task['id']} 未达标 | 当前{current_price:.0f}元 > 阈值{target:.0f}元，继续监控")
        except Exception as exc:
            add_log("ERROR", f"任务#{task['id']} [{task['travel_date']}] {route} 执行异常: {exc}")


def start_scheduler() -> None:
    if scheduler.running:
        return

    scheduler.add_job(
        run_once,
        trigger="interval",
        minutes=settings.poll_interval_minutes,
        id="flight_monitor_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    add_log("INFO", f"定时任务已启动，每 {settings.poll_interval_minutes} 分钟执行一次")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        add_log("INFO", "定时任务已停止")
