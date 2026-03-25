from __future__ import annotations

from datetime import date

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.airports import AIRPORTS
from app.config import settings
from app.db import add_log, add_task, delete_task, init_db, list_logs, list_tasks, toggle_task
from app.scheduler import run_once, scheduler, start_scheduler, stop_scheduler

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    start_scheduler()


@app.on_event("shutdown")
def shutdown_event() -> None:
    stop_scheduler()


@app.get("/")
def index(request: Request):
    tasks = list_tasks(limit=10)
    logs = list_logs(200)
    # 获取下次执行时间（Unix 毫秒，供前端倒计时使用）
    next_run_ms: int | None = None
    try:
        job = scheduler.get_job("flight_monitor_job")
        if job and job.next_run_time:
            import datetime as _dt
            next_run_ms = int(job.next_run_time.timestamp() * 1000)
    except Exception:
        pass
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tasks": tasks,
            "logs": logs,
            "settings": settings,
            "today": date.today().isoformat(),
            "airports": AIRPORTS,
            "next_run_ms": next_run_ms,
        },
    )


@app.post("/tasks")
def create_task(
    travel_date: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    target_price: float = Form(...),
):
    add_task(travel_date, origin, destination, target_price)
    add_log("INFO", f"新建任务: {travel_date} {origin}->{destination} <= {target_price:.0f}")
    return RedirectResponse(url="/", status_code=303)


@app.post("/tasks/{task_id}/delete")
def remove_task(task_id: int):
    delete_task(task_id)
    add_log("INFO", f"删除任务#{task_id}")
    return RedirectResponse(url="/", status_code=303)


@app.post("/tasks/{task_id}/toggle")
def switch_task(task_id: int):
    toggle_task(task_id)
    add_log("INFO", f"切换任务#{task_id}状态")
    return RedirectResponse(url="/", status_code=303)


@app.post("/monitor/run")
def manual_run():
    run_once()
    return RedirectResponse(url="/", status_code=303)
