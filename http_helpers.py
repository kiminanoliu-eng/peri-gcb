#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess


def http_get(url, timeout=20):
    command = [
        "curl", "-L", "-sS", "--max-time", str(timeout),
        "-w", "\n__STATUS__:%{http_code}", url
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return 0, "", {}

    body, _, status_line = result.stdout.rpartition("\n__STATUS__:")
    status_code = int(status_line.strip()) if status_line.strip().isdigit() else 0
    return status_code, body, {}


def http_head(url, timeout=20):
    command = [
        "curl", "-I", "-L", "-sS", "--max-time", str(timeout),
        "-w", "\n__STATUS__:%{http_code}", url
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return 0, {}

    raw_headers, _, status_line = result.stdout.rpartition("\n__STATUS__:")
    status_code = int(status_line.strip()) if status_line.strip().isdigit() else 0
    headers = {}
    for line in raw_headers.splitlines():
        if ":" not in line or line.startswith("HTTP/"):
            continue
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()
    return status_code, headers
