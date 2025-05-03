import json
import os
import re

import jsmin


# -------------------
## holds configuration data
class Cfg:
    ## flag to indicate dev or remote
    is_local = True
    ## flag to run server in debug mode (auto-refresh) or not
    is_debug = True
    ## server host name
    server_hostname = None
    ## IP port to use
    server_port = 0
    ## IP address for server to listen on
    server_ip = None
    ##  server URL
    server_url = None
    ## location of root pwd file
    server_sudo_pwd_path = None
    ## name of the service file
    svc_name = None
    ## service userid to use
    svc_user_name = None
    ## service group name to use
    svc_group_name = None
    ## service working directory
    svc_working_dir = None
    ## path to service bash file
    svc_do_server_path = None
    ## list of clients
    clients = []
    ## information about the clients
    pc_info = {}

    # -------------------
    ## load Cfg data from JSON file
    #
    # @return None
    def load(self):
        path = os.path.join('webhost', 'notify-server.json')
        with open(path, 'r', encoding='utf-8') as fp:
            # handle comments in the json file
            clean_data = jsmin.jsmin(fp.read())
            j_data = json.loads(clean_data)

            # got to do this first
            setattr(self, 'is_local', j_data['is_local'])

            # choose which set of attrs to use based on is_local flag
            if self.is_local:
                sub_data = j_data['local_mode']
            else:
                sub_data = j_data['remote_mode']

            for key, val in sub_data.items():
                # print(f'cfg json: b4  key: {key} val:{val}')
                val = self._translate(val)
                # print(f'cfg json: aft key: {key} val:{val}')
                setattr(self, key, val)

            # get list of clients
            setattr(self, 'pc_info', j_data['pc_info'])
            for _, info in self.pc_info.items():
                for key, val in info.items():
                    # print(f'cfg json: b4  pc_info client:{client} key: {key} val:{val}')
                    val = self._translate(val, info)
                    # print(f'cfg json: aft pc_info client:{client} key: {key} val:{val}')
                    info[key] = val

        # uncomment to debug
        # import pprint
        # pprint.pprint(vars(self))

    # -------------------
    ## translate a line with possible embedded cfg info names
    #
    # @param pc    the client PC to translate for
    # @param line  the line to translate
    # @return the translated line
    def translate_for(self, pc, line):
        pc_info = self.pc_info[pc]
        return self._translate(line, pc_info, pc)

    # -------------------
    ## translate a line with possible embedded cfg info names
    #
    # @param line     the line to translate
    # @param pc_info  the PC specific info to translate for
    # @param pc       the name of the PC to translate for
    # @return the translated line
    def _translate(self, line, pc_info=None, pc=None):
        for count in range(0, 5):  # prevent infinite loop
            if not isinstance(line, str):
                break

            m = re.search(r'{(.*?)}', line)
            if not m:
                break

            var_name = m.group(1)
            if var_name == 'server_hostname':
                val = self.server_hostname
            elif var_name == 'server_port':
                val = self.server_port
            elif var_name == 'svc_user_name':
                val = self.svc_user_name
            elif var_name == 'svc_group_name':
                val = self.svc_group_name
            elif var_name == 'svc_working_dir':
                val = self.svc_working_dir
            elif var_name == 'svc_do_server_path':
                val = self.svc_do_server_path
            elif pc_info:
                if var_name == 'user_name':
                    val = pc_info['user_name']
                elif var_name == 'working_dir':
                    val = pc_info['working_dir']
                elif var_name == 'pc':
                    val = pc
                else:
                    print(f'BUG  {count: >2}] unknown pc_info {var_name} in: {line}')
                    break
            else:
                print(f'BUG  {count: >2}] unknown {var_name} in: {line}')
                break

            # print(f'DBG  {count: >2}] replacing {var_name} with {val}')
            line = line.replace('{' + var_name + '}', str(val))
        return line


cfg = Cfg()
