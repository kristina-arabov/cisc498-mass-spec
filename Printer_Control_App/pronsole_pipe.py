"""
Wrapper to run pronsole with piped stdin/stdout support.
Sets use_rawinput=False so pronsole reads from stdin.readline()
instead of input(), which fails when stdin is not a TTY.
"""
import sys
import io
from printrun.pronsole import pronsole

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, line_buffering=True)

interp = pronsole()
interp.use_rawinput = False
interp.settings.rpc_server = False
interp.parse_cmdline(sys.argv[1:])
interp.cmdloop()
