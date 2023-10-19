# Tor Configuration

Look at your torrc for the following configuration options...

 Tor uses a text file called torrc that contains configuration instructions for how your Tor program should behave. The default configuration should work fine for most Tor users.

If you installed Tor Browser on Windows or Linux, look for Browser/TorBrowser/Data/Tor/torrc inside your Tor Browser directory. If you're on macOS, the torrc is in ~/Library/Application Support/TorBrowser-Data/Tor . To get to it, press cmd-shift-g while in Finder and copy/paste that directory into the box that appears.

Otherwise, if you are using Tor without Tor Browser, it looks for the torrc file in /usr/local/etc/tor/torrc if you compiled tor from source, and /etc/tor/torrc or /etc/torrc if you installed a pre-built package.

Once you've created or changed your torrc file, you will need to restart tor for the changes to take effect. (For advanced users, note that you actually only need to send Tor a HUP signal, not actually restart it.) 

## torrc

#This provides a port for our script to talk with. If you set this then be
#sure to also set either CookieAuthentication *or* HashedControlPassword!
#
#You could also use ControlSocket instead of ControlPort, which provides a
#file based socket. You don't need to have authentication if you use
#ControlSocket. For this example however we'll use a port.

ControlPort 9051

#Setting this will make Tor write an authentication cookie. Anything with
#permission to read this file can connect to Tor. If you're going to run
#your script with the same user or permission group as Tor then this is the
#easiest method of authentication to use.

CookieAuthentication 1

#Alternatively we can authenticate with a password. To set a password first
#get its hash...
#
#% tor --hash-password "my_password"
#16:E600ADC1B52C80BB6022A0E999A7734571A451EB6AE50FED489B72E3DF
#
#... and use that for the HashedControlPassword in your torrc.

HashedControlPassword 16:E600ADC1B52C80BB6022A0E999A7734571A451EB6AE50FED489B72E3DF
