import sys
import time
from datetime import datetime


# --------------------
## logger instance
class Logger:
    # --------------------
    ## initialize
    def __init__(self):
        ## holds count of the last time a flush was done
        self._flush_count = 0
        ## holds the last time a full DTS was written to the log
        self._start_time = 0

    # --------------------
    ## initialize
    #
    # @return None
    def init(self):
        pass

    # --------------------
    ## indicate some activity is starting
    #
    # @param msg  the message to log
    # @return None
    def start(self, msg):
        self._log('====', msg)

    # --------------------
    ## write line with no prefix
    #
    # @param msg  the message to log
    # @return None
    def line(self, msg):
        self._log('', msg)

    # --------------------
    ## write an error line
    #
    # @param msg  the message to log
    # @return None
    def err(self, msg):
        self._log('ERR', msg)

    # --------------------
    ## write a debug line
    #
    # @param msg  the message to log
    # @return None
    def dbg(self, msg):
        self._log('DBG', msg)

    # --------------------
    ## write the message to stdout and save to the array for later processing
    #
    # @param msg  the message to log
    # @return None
    def info(self, msg):
        self._log('INFO', msg)

    # --------------------
    ## log a line
    #
    # @param tag    what kind of log line is it
    # @param msg    the text of the log line
    # @return None
    def _log(self, tag, msg):
        elapsed = time.time() - self._start_time
        if elapsed > 3600:
            self._start_time = time.time()
            t_str = datetime.fromtimestamp(self._start_time).strftime('%H:%M:%S.%f')[:12]
            print(f'{t_str} {tag:<4} on {time.strftime("%Y/%m/%d", time.localtime(self._start_time))} ')
            elapsed = time.time() - self._start_time

        # datetime can't use elapsed times and time delta's can't use %f
        t_struct = time.gmtime(elapsed)
        ms = f'{int((elapsed * 1000) % 1000):03d}'[:3]
        t_str = f'{t_struct.tm_hour:02d}:{t_struct.tm_min:02d}:{t_struct.tm_sec:02d}.{ms}'
        print(f'{t_str} {tag:<4} {msg}')

        self._flush_count += 1
        if self._flush_count > 0:
            sys.stdout.flush()
            self._flush_count = 0
