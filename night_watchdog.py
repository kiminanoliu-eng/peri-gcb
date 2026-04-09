#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from extract_product_sources import BASE_DIR, load_products


WATCHDOG_STATUS_PATH = BASE_DIR / "watchdog_status.json"
SUPERVISOR_STATUS_PATH = BASE_DIR / "supervisor_status.json"


def utc_now_iso():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def pending_slugs():
    products = load_products()
    complete = {path.name[:-14] for path in BASE_DIR.glob("*_complete.json")}
    return [slug for slug in products if slug not in complete]


def run_command(args):
    result = subprocess.run(args, cwd=str(BASE_DIR), text=True, capture_output=True)
    return {
        "args": args,
        "returncode": result.returncode,
        "stdout": result.stdout[-6000:],
        "stderr": result.stderr[-6000:],
    }


def save_status(status):
    payload = json.dumps(status, ensure_ascii=False, indent=2)
    WATCHDOG_STATUS_PATH.write_text(payload, encoding="utf-8")
    SUPERVISOR_STATUS_PATH.write_text(payload, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-iterations", type=int, default=0, help="最多执行多少轮，0 表示无限直到完成")
    parser.add_argument("--sleep-seconds", type=int, default=3, help="每轮之间的等待秒数")
    parser.add_argument("--batch-limit", type=int, default=0, help="每轮批处理只做前 N 个待处理产品，0 表示处理全部")
    args = parser.parse_args()

    status = {
        "started_at": utc_now_iso(),
        "iterations": [],
        "phase": "running",
    }
    save_status(status)

    last_pending_count = None
    stalled_rounds = 0
    iteration_count = 0

    while True:
        iteration_count += 1
        pending_before = pending_slugs()
        iteration = {
            "started_at": utc_now_iso(),
            "iteration": iteration_count,
            "pending_before": len(pending_before),
            "sample_pending": pending_before[:10],
        }

        if not pending_before:
            iteration["stage"] = "audit_and_publish"
            iteration["add_pdf_links"] = run_command(["python3", "add_pdf_links.py"])
            iteration["rebuild"] = run_command(["python3", "rebuild_site_v2.py"])
            iteration["audit"] = run_command(["python3", "audit_site_batch.py"])

            if iteration["audit"]["returncode"] != 0:
                status["phase"] = "audit_failed"
                status["iterations"].append(iteration)
                save_status(status)
                raise SystemExit("站点审计失败，未发布。")

            iteration["git_add"] = run_command(["git", "add", "-A"])
            iteration["git_commit"] = run_command(["git", "commit", "-m", "Night batch complete 160 products"])
            iteration["git_push"] = run_command(["git", "push"])

            status["phase"] = "published"
            iteration["finished_at"] = utc_now_iso()
            status["iterations"].append(iteration)
            status["finished_at"] = utc_now_iso()
            save_status(status)
            print("✅ 全量产品完成，审计通过，已发布。")
            return

        iteration["stage"] = "batch_run"
        batch_args = ["python3", "run_product_batch.py"]
        if args.batch_limit > 0:
            batch_args.extend(["--limit", str(args.batch_limit)])
        iteration["batch"] = run_command(batch_args)
        pending_after = pending_slugs()
        iteration["pending_after"] = len(pending_after)
        iteration["finished_at"] = utc_now_iso()
        status["iterations"].append(iteration)
        save_status(status)

        if pending_after == 0:
            continue

        if last_pending_count is not None and len(pending_after) >= last_pending_count:
            stalled_rounds += 1
        else:
            stalled_rounds = 0
        last_pending_count = len(pending_after)

        if stalled_rounds >= 3:
            status["phase"] = "stalled"
            status["finished_at"] = utc_now_iso()
            save_status(status)
            raise SystemExit("连续三轮没有推进，watchdog 停止。")

        if args.max_iterations and iteration_count >= args.max_iterations:
            status["phase"] = "max_iterations_reached"
            status["finished_at"] = utc_now_iso()
            save_status(status)
            print("达到测试轮数上限，watchdog 退出。")
            return

        time.sleep(args.sleep_seconds)


if __name__ == "__main__":
    main()
