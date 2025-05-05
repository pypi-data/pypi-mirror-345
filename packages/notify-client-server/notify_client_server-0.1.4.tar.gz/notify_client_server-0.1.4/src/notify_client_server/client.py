import datetime

import requests

from .cfg import cfg
from .common.logger_null import LoggerNull
from .os_specific import OsSpecific


# --------------------
## send various notifications to the server
class NotifyClient:
    # --------------------
    ## constructor
    # @param logger   (optional) the logger to use
    def __init__(self, logger=None):
        cfg.load()
        ## holds logger instance
        if logger:
            self._log = logger
        else:
            self._log = LoggerNull()

    # --------------------
    ## send a ping post
    #
    # @return response from the post
    def ping(self):
        # TODO do notify to macos and windows
        # os.system(f'notify-send "ping" "sent to {cfg.server_url}"')

        url = f'{cfg.server_url}/ping'

        # gather data to send
        data = {
            'refresh-page': True,
        }
        # uncomment to debug
        # self._log.dbg(f'json_data: {data}')

        return self._send_it(url, data)

    # --------------------
    ## send a notify post with the given info
    #
    # @param tag      the notification name
    # @param status   the status: 'ok', 'err' or 'warn'
    # @param desc     additional description for the notification
    # @return response from the post
    def notify(self, tag, status, desc):
        url = f'{cfg.server_url}/notify'

        # gather data to send
        dts = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        data = {
            'dts': dts,  # -                      DTS received (or sent?)
            'source': OsSpecific.hostname,  # -   hostname that sent the notification
            'tag': tag,  # -                      notification name e.g. backup_nas
            'status': status,  # -                ok, err, warn
            'desc': desc,  # -                    (optional) additional description of what happened
        }

        # uncomment to debug
        # self._log.dbg(f'json_data: {data}')

        return self._send_it(url, data)

    # --------------------
    ## send POST request with the given data
    #
    # @param url    the url to post to
    # @param data   the data to send
    # @return the response
    def _send_it(self, url, data):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers, timeout=1)

        # check response
        status = response.status_code
        self._log.line(f"{response.text: <20} POST {status} {cfg.server_url}")
        return response
