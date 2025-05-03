import os
import re

from cfg import cfg


# -------------------
## generate any files necessary for use in the service, client, etc.
class Staging:
    # -------------------
    ## generate the service file based on the template
    #
    # @return None
    def gen_service_file(self):
        dst = os.path.join('webhost', cfg.svc_name)
        if os.path.isfile(dst):
            os.remove(dst)

        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template_notify_server.service')
        with open(src, 'r', encoding='utf-8') as src_fp:
            with open(dst, 'w', encoding='utf-8') as dst_fp:
                while True:
                    line = src_fp.readline()
                    if line == '':
                        break
                    line = self._translate(line)
                    dst_fp.write(line)

    # -------------------
    ## translate string with possible markers in them
    # @param line  the line to translate
    # @return translated line
    def _translate(self, line):
        for count in range(0, 5):  # prevent infinite loop
            m = re.search(r'{(.*)}', line)
            if not m:
                break

            var_name = m.group(1)
            if var_name == 'user-name':
                val = cfg.svc_user_name
            elif var_name == 'group-name':
                val = cfg.svc_group_name
            elif var_name == 'working-dir':
                val = cfg.svc_working_dir
            elif var_name == 'do-server-path':
                val = cfg.svc_do_server_path
            else:
                print(f'BUG  {count: >2}] unknown {var_name}')
                break

            # print(f'DBG  {count: >2}] replacing {var_name} with {val}')
            line = line.replace('{' + var_name + '}', val)
        return line
