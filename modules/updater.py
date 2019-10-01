import subprocess


def updateTor():
    """Currently updates Tor by calling terminal commands using subprocess.

    Not a great method and will be replaced in the future.

    Args:
        None

    Returns:
        None: The return value.
    """

    print("Checking for latest stable release")
    isGit = subprocess.Popen(
            ["git", "branch"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    output = isGit.stdout.read()
    branch = output[2:8].decode("utf-8")
    print(branch)
    if branch == 'master':
        update = subprocess.Popen(
                 ["git", "pull", "origin", "master"],
                 stdout=subprocess.PIPE,
                 stderr=subprocess.STDOUT)
        update_out = update.stdout.read()
        if update_out[90:109].decode("utf-8") == 'Already up to date.':
            print("TorBot is already up-to-date.")
        else:
            print("TorBot has succesfully updated to latest stable version.")
    else:
        subprocess.Popen(
            ["git", "init"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        subprocess.Popen(
            ["git", "remote", "add", "origin",
                "https://github.com/DedSecInside/TorBoT.git"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        update = subprocess.Popen(
            ["git", "pull", "origin", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        update_out = update.stdout.read()
        if update_out[90:109].decode("utf-8") == 'Already up to date.':
            print("TorBot is already up-to-date.")
        else:
            print("TorBot has succesfully updated to latest stable version.")
