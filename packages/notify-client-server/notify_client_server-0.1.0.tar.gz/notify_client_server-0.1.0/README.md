* website: <https://arrizza.com/notify-client-server.html>
* installation: see <https://arrizza.com/setup-common.html>

*** Under Construction ***

* setup windows/msys2

* Ensure OpenSSH server is running on windows
  * Open Services
  * goto "OpenSSh Server"
    * Ensure Startup Type == "Automatic"
    * if Status is not "Running", right click and select "Start"

```bash
# see https://www.msys2.org/wiki/Setting-up-SSHd/
$ nano /c/msys64/sshd_default_shell.cmd
    # add one line:
    @C:\msys64\msys2_shell.cmd -defterm -here -no-start -mingw64
```


# set registry entry HKEY_LOCAL_MACHINE\SOFTWARE\OpenSSH\DefaultShell to the path of that batch file.
 * click start memu
 * enter regedit into search
 * click on "run as administrator" in the Registry Editor pane
 * click Yes to allow app to make changes to your device
 * click on HKEY_LOCAL_MACHINE
 * click on SOFTWARE
 * click on OpenSSH
 * should only be "Agent"
 * right click on OpenSSh
 * get menu; click on New
 * get submenu; click on Key
 * get "New Key #1" as a folder inside OpenSSH; rename it to "DefaultShell"
 * click on new DefaultShell
 * right click on "(Default)"
 * get dlgbox; set "Value data:" to C:\msys64\sshd_default_shell.cmd

Windows Firewall
* open Start menu; enter "firewall" into search; open "Windows Defender Firewall"
  * click "Allow an app or feature..."
  * find "OpenSSH Server" and confirm that it is allowed in Private networks
* open Start menu; enter "firewall" into search; open "Windows Defender Firewall"
  * click "Advanced settings"
  * 


```
# DOESN'T WORK
$ cd /c/projects   # or a directory to create the script
$ nano msys2-sshd-setup.sh
  # cut-n-paste text from the website above
$ ./msys2-sshd-setup.sh

# If you get "The user name could not be found."



$ pacman -Syu
$ pacman -S openssh
$ pacman -S cygrunsrv
$ pacman -S mingw-w64-x86_64-editrights

$ ssh-host-config
    # You'll be prompted with several questions.  
    #  It's generally safe to accept the default values (just press Enter) 
    # unless you have specific requirements
$ nano /etc/ssh/sshd_config
    # Port 22               :  # confirm
    # ListenAddress 0.0.0.0 :  # confirm
    # PasswordAuthentication yes :  # For initial testing, you might want to enable password authentication.  
                                    # However, for security, it's highly recommended to switch to 
                                    # public key authentication as soon as possible.
    # Subsystem       sftp    /usr/bin/sftp-server:  Make sure this line is not commented out
    # StrictModes no        :  You might need to set this to no to avoid permission errors.

$ cygservice -S sshd

# Configure Windows Firewall
#   allow port 22

TODO check Windows username
TODO set up ssh auth 
#   ~/.ssh/authorized_keys
```

* run do_server