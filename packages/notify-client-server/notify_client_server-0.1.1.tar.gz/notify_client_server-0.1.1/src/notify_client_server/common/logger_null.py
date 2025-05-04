# --------------------
## logger instance with no output
class LoggerNull:
    # --------------------
    ## initialize
    def __init__(self):
        pass

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
        pass

    # --------------------
    ## write line with no prefix
    #
    # @param msg  the message to log
    # @return None
    def line(self, msg):
        pass

    # --------------------
    ## write an error line
    #
    # @param msg  the message to log
    # @return None
    def err(self, msg):
        pass

    # --------------------
    ## write a debug line
    #
    # @param msg  the message to log
    # @return None
    def dbg(self, msg):
        pass

    # --------------------
    ## write the message to stdout and save to the array for later processing
    #
    # @param msg  the message to log
    # @return None
    def info(self, msg):
        pass
