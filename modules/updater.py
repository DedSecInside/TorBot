import subprocess

__all__ = ['updateTor']

def updateTor():
	print("Checking for latest stable release")
	isGit = subprocess.Popen("git branch",stdout=subprocess.PIPE,shell=True)
	(output,err)=isGit.communicate()
	branch = output[2:8].decode("utf-8")
	if branch == 'master':
		update = subprocess.Popen(["git","pull","origin","master"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		update_out = update.stdout.read()
		if update_out[85:104].decode("utf-8") == 'Already up-to-date.' :
			print("TorBot Already up-to-date.")
		else:
			print("TorBot has succesfully updated to latest stable version.")	
	else:
		subprocess.Popen(["git","init"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		subprocess.Popen(["git","remote","add","origin","https://github.com/DedSecInside/TorBoT.git"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		update = subprocess.Popen(["git","pull","origin","master"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		update_out = update.stdout.read()
		if update_out[85:104].decode("utf-8") == 'Already up-to-date.' :
			print("TorBot Already up-to-date.")
		else:
			print("TorBot has succesfully updated to latest stable version.")		
	return 0
	
