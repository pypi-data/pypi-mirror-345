import getpass
import os
import platform
import subprocess
import sys

from dataclasses import dataclass


# -------------------
## holds OS specific info; there are four recognized OS:
#    OS      os_name
#  -------   ----------
#  Ubuntu  :  ubuntu
#  Mac     : macos
#  Windows : win
#  RPI     : rpi
@dataclass(frozen=True)
class _OsSpecificInvocation:
    ## holds the OS name
    os_name: str
    ## holds the OS version info
    os_version: str
    ## holds the python version
    python_version: str
    ## projects directory
    proj_dir: str
    ## root directory of projects directory
    root_dir: str
    ## current userid
    userid: str
    ## hostname of the pc
    hostname: str
    ## list of valid OS
    os_valid = ['ubuntu', 'macos', 'win', 'rpi']
    ## used by UTs only
    _ut_mode = False

    # -------------------
    ## selects the current platform and sets impl to it
    #
    # @param ut_os_name  UTs only: use this OS name
    # @return None
    @classmethod
    def set_all_data(cls, ut_os_name=None):
        if ut_os_name is not None:
            cls._ut_mode = True
            # uncomment to debug
            # print(f'ut_os_name:{ut_os_name} ut_mode:{cls._ut_mode}')
        ## holds the implementation class
        os_name = cls.get_os_name(ut_os_name)
        if os_name == 'rpi':
            # TODO confirm this is correct
            os_version = f'RPI {platform.system()} {platform.release()}'
            root_dir = '~'
            proj_dir = os.path.expanduser(os.path.join(root_dir, 'projects'))
        elif os_name == 'win':
            os_version = f'win32 {platform.system()} {platform.release()}'
            root_dir = '/c'  # translates to c:\projects
            proj_dir = os.path.expanduser(os.path.join(os.sep, 'projects'))
        elif os_name == 'macos':
            os_version = f'macOS {platform.mac_ver()[0]}'
            root_dir = '~'
            proj_dir = os.path.expanduser(os.path.join(root_dir, 'projects'))
        elif os_name == 'ubuntu':
            os_version = cls._ubuntu_os_version()
            root_dir = '~'
            proj_dir = os.path.expanduser(os.path.join(root_dir, 'projects'))
        else:
            print(f'BUG  unrecognized OS: "{sys.platform}"')
            sys.stdout.flush()
            sys.exit(1)

        ## holds python version e.g. "Python 3.10"
        python_version = f'Python {sys.version_info.major}.{sys.version_info.minor}'

        hostname = platform.uname().node
        hostname = hostname.lower().replace('.local', '')

        return cls(os_name=os_name,
                   os_version=os_version,
                   python_version=python_version,
                   root_dir=root_dir,
                   proj_dir=proj_dir,
                   userid=getpass.getuser(),
                   hostname=hostname,
                   )

    # -------------------
    ## deprecated; delete when all instances of OsSpecific.init() are deleted
    # @return None
    def init(self):
        pass

    # -------------------
    ## get the current OS tag
    #
    # @param ut_os_name  UTs only: use this OS tag for testing
    # @return the OS tag/name
    @classmethod
    def get_os_name(cls, ut_os_name=None):
        if ut_os_name is not None:
            os_name = ut_os_name
        elif os.path.isfile('/sys/firmware/devicetree/base/model'):  # pragma: no cover
            os_name = 'rpi'
        elif sys.platform == 'win32':  # pragma: no cover
            os_name = 'win'
        elif sys.platform == 'darwin':  # pragma: no cover
            os_name = 'macos'
        elif sys.platform == 'linux':  # pragma: no cover
            os_name = 'ubuntu'
        else:
            os_name = 'unknown'  # pragma: no cover

        return os_name

    # -------------------
    ## run a command in a subprocess
    #
    # @param cmd           the command to run
    # @param working_dir   the working directory to run the command in; default is '.'
    # @param print_cb      callback function used to print output; default is None
    # @return rc - return code, lines - the output as a list of lines
    def run_cmd(self, cmd, working_dir='.', print_cb=None):
        shell = True
        ## see doc above
        if self.os_name == 'win':
            cmd = ['c:/msys64/usr/bin/bash', '-c', cmd]

        proc = subprocess.Popen(cmd,  # pylint: disable=consider-using-with
                                cwd=working_dir,
                                shell=shell,
                                bufsize=0,
                                universal_newlines=True,
                                stdin=None,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        last_line = ''
        lineno = 0
        lines = []
        while True:
            if last_line:
                last_line = last_line.rstrip()
                lines.append(last_line)
                if print_cb:
                    print_cb(lineno, last_line)
                    sys.stdout.flush()
            ret_code = proc.poll()
            if ret_code is not None and last_line == '':
                break
            last_line = proc.stdout.readline()
            lineno += 1

        # proc.wait()
        sys.stdout.flush()
        rc = proc.returncode

        return rc, lines

    # -------------------
    ## holds OS information for Ubuntu
    #
    # @return string indicating OS info
    @classmethod
    def _ubuntu_os_version(cls):
        proc = subprocess.Popen(['lsb_release', '-a'],  # pylint: disable=consider-using-with
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT
                                )
        (out, _) = proc.communicate()
        out = out.decode('utf-8')

        version = 'notset'
        codename = 'notset'
        for line in out.split('\n'):
            # print(f'line: "{line}"')
            args = line.split('\t')
            if args[0] == 'Release:':
                version = args[1]
            elif args[0] == 'Codename:':
                codename = args[1]
        return f'Ubuntu {version} {codename}'


OsSpecific = _OsSpecificInvocation.set_all_data()
