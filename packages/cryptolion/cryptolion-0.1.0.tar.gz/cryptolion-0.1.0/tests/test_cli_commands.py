import subprocess, sys

def test_backtest_help():
    res = subprocess.run([
        sys.executable, '-m', 'backtester', 'backtest', '--help'
    ], capture_output=True)
    assert res.returncode == 0

def test_walk_help():
    res = subprocess.run([
        sys.executable, '-m', 'backtester', 'walk', '--help'
    ], capture_output=True)
    assert res.returncode == 0

def test_report_help():
    res = subprocess.run([
        sys.executable, '-m', 'backtester', 'report', '--help'
    ], capture_output=True)
    assert res.returncode == 0
