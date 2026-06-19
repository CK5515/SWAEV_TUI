#!/usr/bin/env python3
"""
Entry point for both `swaev` console command (via pip) and `python -m swaev`.
Locates client.py inside the installed package and delegates to run_tui().
"""
import importlib.util
import os
import sys


def main() -> None:
    client_path = os.path.join(os.path.dirname(__file__), "client.py")
    if not os.path.exists(client_path):
        sys.exit(
            "GoldBEAM client not found. Re-install with: pip install --upgrade swaev"
        )
    spec = importlib.util.spec_from_file_location("swaev._client", client_path)
    mod = importlib.util.module_from_spec(spec)   # type: ignore[arg-type]
    spec.loader.exec_module(mod)                   # type: ignore[union-attr]
    try:
        mod.run_tui()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
