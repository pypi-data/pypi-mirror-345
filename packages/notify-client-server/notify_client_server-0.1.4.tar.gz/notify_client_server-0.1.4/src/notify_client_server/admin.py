import sys

from cfg import cfg
from os_specific import OsSpecific
from staging import Staging


# -------------------
## run a command for the local PC or for a remote PC
class App:
    # -------------------
    ## initialize
    #
    # @return None
    def init(self):
        cfg.load()

        staging = Staging()
        staging.gen_service_file()

    # -------------------
    ## run a command
    #
    # @param cmd  the command to run
    # @return None
    def run(self, cmd):
        fn_map = {
            'test': self.do_test,
            'push': self.do_push,
            # server only
            'install': self.do_server_install,
            'uninstall': self.do_server_uninstall,
            'restart': self.do_server_restart,
            'stop': self.do_server_stop,
            'status': self.do_server_status,
            'journal': self.do_server_journal,
        }
        if cmd not in fn_map:
            print(f'ERR  unknown command: {cmd}')
            print(f'ERR  valid cmds are: {", ".join(fn_map.keys())}')
            return

        fn = fn_map[cmd]
        fn()

    # -------------------
    ## push files to remote PCs
    #
    # @return None
    def do_push(self):
        # do only if remote
        if cfg.is_local:
            print('WARN push is only valid when server is remote')
            return

        print('==== running push')
        opts = ''
        # -r => recursive
        # -v => verbose
        # -h => human-readable sizes
        # -c => skip based on checksum
        # -i => output a change-summary instead of continuous output
        opts += "-rvhci "
        # --delete          => DO NOT USE! remove deleted source files in destination directory
        # --delete-excluded => DO NOT USE! delete any destination directories that match excluded
        # --exclude         => files/directory to exclude
        opts += "--exclude notify_server.db "
        opts += "--exclude __pycache__ "  # don't send cache files
        opts += "--exclude 'pf_*' "  # _    don't send "pf" (personal files)
        opts += "--exclude 'pf_*/' "

        # do push to all PCs
        pc_list = self._get_pc_list()
        for pc in pc_list:
            if pc == OsSpecific.hostname:
                # skip the sender PC
                continue
            path = '{pc}:{working_dir}/webhost'
            path = cfg.translate_for(pc, path)
            lines = f'rsync {opts} webhost/ {path}/'
            print(f' --> pushing to {pc}')
            OsSpecific.run_cmd(lines, print_cb=self._print_cb)

    # -------------------
    ## for test/dev purposes only
    #
    # @return None
    def do_test(self):
        lines = [
            'hostname',
            'pwd',
            'cd {working_dir}',
            'pwd',
            'ls -al ./webhost/',
            'git pull',
        ]
        self._run_on_all('test', lines, skip_local=False)

    # -------------------
    ## run lines on all PCs.
    #
    # @param tag         cmd name for logging
    # @param lines       the command lines to run
    # @param skip_local  (optional) if true skip the local PC, if false do the command on all PCs including this one
    # @return None
    def _run_on_all(self, tag, lines, skip_local=False):
        pc_list = self._get_pc_list()
        print(f'==== running "{tag}" on: {", ".join(pc_list)}')

        for pc in pc_list:
            self._run_on(pc, lines, skip_local=skip_local)

    # -------------------
    ## get list of PCs to run a command on
    #
    # @return the list of PCs
    def _get_pc_list(self):
        # TODO: allow user to choose PC list?
        # do_admin cmd <none>    ; send to all client + server
        # do_admin cmd other     ; to other (not current PC)
        # do_admin j1 j2 etc     ; send to all named destinations

        pc_list = [cfg.server_hostname]
        pc_list.extend(sorted(cfg.clients))
        return pc_list

    # -------------------
    ## run commands on the given PC
    #
    # @param pc          the PC to run the commands on
    # @param lines       the command lines to run
    # @param skip_local  (optional) if true skip the local PC, if false do the command on all PCs including this one
    # @return None
    def _run_on(self, pc, lines, skip_local=False):
        if pc == OsSpecific.hostname:
            tag = 'local'
            if skip_local:
                print(f' --> {tag: <6}: skipping      : {pc}')
                return
            cmd = '\n'.join(lines)
        else:
            tag = 'remote'
            cmd = ''
            cmd += f'ssh arrizza@{pc} "bash -s "<< EOF\n'
            for line in lines:
                line = cfg.translate_for(pc, line)
                cmd += f'{line}\n'
            cmd += 'EOF\n'

        print(f' --> {tag: <6}: running cmd on: {pc}')
        OsSpecific.run_cmd(cmd, print_cb=self._print_cb)

    # === server commands

    # -------------------
    ## install service.
    # assumes do_push was done
    #
    # @return None
    def do_server_install(self):
        lines = [
            f'systemctl enable webhost/{cfg.svc_name}',
            f'systemctl start {cfg.svc_name}',
        ]
        # only do this on the server
        self._run_server_root('install', lines)

    # -------------------
    ## uninstall service
    #
    # @return None
    def do_server_uninstall(self):
        lines = [
            'systemctl daemon-reload',
            f'systemctl stop {cfg.svc_name}',
            f'systemctl disable {cfg.svc_name}',
            f'systemctl show {cfg.svc_name} | grep "Load"',
            f'sudo unlink /etc/systemd/system/{cfg.svc_name}'
            # 'rm /path/to/{cfg.svc_name}'
            # 'systemctl daemon-reload',
            # 'systemctl reset-failed {cfg.svc_name}'
            # 'systemctl list-unit-files --type=service'
        ]
        # only do this on the server
        self._run_server_root('uninstall', lines)

    # -------------------
    ## restart service
    #
    # @return None
    def do_server_restart(self):
        lines = [
            'systemctl daemon-reload',
            f'systemctl restart {cfg.svc_name}',
        ]
        # only do this on the server
        self._run_server_root('restart', lines)

    # -------------------
    ## stop service
    #
    # @return None
    def do_server_stop(self):
        lines = [
            'systemctl daemon-reload',
            f'systemctl stop {cfg.svc_name}',
        ]
        # only do this on the server
        self._run_server_root('stop', lines)

    # -------------------
    ## run service status
    #
    # @return None
    def do_server_status(self):
        lines = f'systemctl status {cfg.svc_name} --no-pager'
        # only do this on the server
        self._run_server_root('status', lines)

    # -------------------
    ## run journalctl to see log output from service
    #
    # @return None
    def do_server_journal(self):
        lines = f'journalctl -u {cfg.svc_name} --no-pager'

        # only do this on the server
        self._run_server_root('journal', lines)

    # -------------------
    ## run one or more command lines in root mode on the local PC or a remote one
    #
    # @param tag         for logging, the command to run on the server
    # @param cmd_lines   the command lines
    # @return None
    def _run_server_root(self, tag, cmd_lines):
        print(f'==== running server {tag} on: {cfg.server_hostname}')

        if isinstance(cmd_lines, str):
            cmd_lines = [cmd_lines]
        elif isinstance(cmd_lines, list):
            pass
        else:
            print(f'ERR  run_root only accepts a string or a list of strings: {cmd_lines}')
            sys.exit(1)

        cmd = ''
        for line in cmd_lines:
            cmd += self._fix_cmdline(line)

        if cfg.is_local:
            OsSpecific.run_cmd(cmd, print_cb=self._print_cb)
        else:
            self._run_remote_server_root(cmd)

    # -------------------
    ## add sudo for local command line to run in sudo mode
    #
    # @param cmd   the command line
    # @return the translated command line
    def _fix_cmdline(self, cmd):
        if cfg.is_local:
            cmd = f'sudo {cmd}'
        cmd = f'{cmd}\n'
        return cmd

    # -------------------
    ## run a set of commands on a remote PC in sudo mode
    #
    # @param cmds    one or more lines to run (bash)
    # @return None
    def _run_remote_server_root(self, cmds):
        cmd = ''
        cmd += f'cat {cfg.server_sudo_pwd_path} - << EOF | ssh "{cfg.server_hostname}" cat \| sudo --prompt="" -S -- su -\n'
        cmd += 'hostname\n'
        cmd += 'whoami\n'
        cmd += f'cd {cfg.svc_working_dir}\n'
        cmd += 'pwd\n'
        cmd += cmds
        cmd += 'EOF\n'
        OsSpecific.run_cmd(cmd, print_cb=self._print_cb)

    # -------------------
    ## callback to print cmd lines
    #
    # @param lineno  the line number
    # @param msg     the line to print
    # @return None
    def _print_cb(self, lineno, msg):
        print(f'@@@@ {lineno: >3}] {msg}')


# -------------------
def main():
    if len(sys.argv) < 2:
        cmd = None
    else:
        cmd = sys.argv[1]

    app = App()
    app.init()
    app.run(cmd)


# -------------------
main()
