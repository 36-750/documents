"""Set up PATH and aliases for R and Python.

The Python for Windows installer helpfully has an option to add itself to the
PATH. Unfortunately, R does not do so, and it does not install to a consistent
location -- it installs to a directory that depends on its version number. We
must find the current R location and add it to the path.

Further, R and Python don't work natively under Git Bash; Python is simply
non-responsive, and R crashes after any error instead of reporting it to the
user and letting them handle it. If we alias the commands to use winpty, we
avoid these problems.

Finally, Git Bash sets $HOME to /c/Users/username, whereas RStudio sets it to
/c/Users/username/Documents. This means that if you install packages in
command-line R, they get installed in /c/Users/username/R/, but RStudio puts
them in /c/Users/username/Documents/R/. To avoid this, set $HOME to match
RStudio. Note that the .profile must go in the original $HOME, since it's read
before it resets $HOME.

Alex Reinhart
"""

import glob
import os.path
import sys
import os

if sys.platform != "win32":
    print("ERROR: You don't need to use this script -- you're not using Windows.")
    print("On Macs, you should be able to install R with the normal installer")
    print("and have it be on your PATH automatically. On Linux, use your")
    print("distro's package manager.")
    exit()

PROFILE_PATH = os.path.join(os.environ["HOME"], ".profile")
PROFILE_EXISTS = os.path.exists(PROFILE_PATH)

if PROFILE_EXISTS:
    print("# WARNING: You already have a .profile in your home directory.")
    print("# Check that the recommendations below don't conflict with")
    print("# your current profile.")
    print()

template = """
export PATH="/c/Program Files/R/{R_version}/bin/x64":"~/bin":$PATH

alias R="winpty R"
alias python="winpty python"

export HOME="$HOME/Documents"

cd "$HOME"
"""

R_DIR = "C:/Program Files/R/*"

possible_Rs = [os.path.basename(p) for p in glob.glob(R_DIR)]

if len(possible_Rs) == 0:
    print("ERROR: You don't seem to have R installed! Install it first.")
    print("Looked in {dir} and found nothing.".format(dir=R_DIR))
    exit()

R_version = sorted(possible_Rs, reverse=True)[0]
CONTENTS = template.format(R_version=R_version)

if PROFILE_EXISTS:
    print("# Put this in the file named .profile in {dir}".format(dir=os.environ["HOME"]))
    print(CONTENTS)
else:
    print(CONTENTS, file=open(PROFILE_PATH, "w"))
    print("Successfully installed {loc}".format(loc=PROFILE_PATH))
