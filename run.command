#!/bin/sh
cd "$(dirname "$0")"
pythonw "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/gui.py
