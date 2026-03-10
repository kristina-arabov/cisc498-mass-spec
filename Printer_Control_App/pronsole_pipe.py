"""
Wrapper to run pronsole with piped stdin/stdout support.
Sets use_rawinput=False so pronsole reads from stdin.readline()
instead of input(), which fails when stdin is not a TTY.
"""
import sys
from printrun.pronsole import pronsole

interp = pronsole()
interp.use_rawinput = False
interp.parse_cmdline(sys.argv[1:])
interp.cmdloop()
