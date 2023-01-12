import subprocess

def check_version():
    try:
        subprocess.run(["git", "branch"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "init"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/DedSecInside/TorBoT.git"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    print("Checking for latest stable release")
    branch_out = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    branch = branch_out.stdout
    if branch == 'master':
        update_out = subprocess.run(["git", "pull", "origin", "master"], capture_output=True, text=True)
        if 'Already up to date.' in update_out.stdout:
            print("TorBot is already up-to-date.")
        else:
            print("TorBot has succesfully updated to latest stable version.")
    else:
        update_out = subprocess.run(["git", "pull", "origin", "dev"], capture_output=True, text=True)
        if 'Already up to date.' in update_out.stdout:
            print("TorBot is already up-to-date.")
        else:
            print("TorBot has succesfully updated to latest stable version.")
