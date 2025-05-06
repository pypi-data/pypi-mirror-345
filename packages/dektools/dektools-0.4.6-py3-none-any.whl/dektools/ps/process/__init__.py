import time
import shlex
import psutil
from tabulate import tabulate
from ...format import format_duration_hms
from ...output import obj2str


def process_list_all():
    table = []
    headers = ['PID', 'USER', 'TIME', 'COMMAND']
    for proc in psutil.process_iter(['pid', 'name', 'username', 'create_time', 'cmdline']):
        x = proc.info
        command = shlex.join(x['cmdline']) if x['cmdline'] else f"<{x['name']}>"
        ts = format_duration_hms(int(time.time() - x['create_time']) * 1000) if x['create_time'] else ''
        table.append(
            [x['pid'], x['username'], ts, command])
    print(tabulate(table, headers=headers), flush=True)


def process_kill(pid):
    p = psutil.Process(pid)
    p.kill()


def process_detail(pid):
    p = psutil.Process(pid)
    print(obj2str(p.as_dict()), flush=True)
