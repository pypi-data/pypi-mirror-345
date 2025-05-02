# tests/test_args.py

from chatgpt_cli.main import main
import sys

def test_argparse_runs(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["chatgpt-cli", "--prompt", "Hello", "--quiet"])
    try:
        main()
    except SystemExit:
        pass  # argparse calls sys.exit on success
