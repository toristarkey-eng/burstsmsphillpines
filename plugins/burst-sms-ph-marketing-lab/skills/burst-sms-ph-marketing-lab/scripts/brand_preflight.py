#!/usr/bin/env python3
"""Verify the local Work bundle before any creative production."""
import sys
from render_creative import main

if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "preflight"]))
