# Tor Configuration Guide

This guide covers Tor configuration for both native installations and Docker deployments.

## Native Tor Installation

Look at your torrc for the following configuration options...

Tor uses a text file called torrc that contains configuration instructions for how your Tor program should behave. The default configuration should work fine for most Tor users.

### Locating torrc

**Windows (Tor Browser):**
- Path: `Browser/TorBrowser/Data/Tor/torrc` inside your Tor Browser directory

**macOS (Tor Browser):**
- Path: `~/Library/Application Support/TorBrowser-Data/Tor`
- To access: Press `cmd-shift-g` in Finder and paste the directory

**Linux (System Tor):**
- Source install: `/usr/local/etc/tor/torrc`
- Package install: `/etc/tor/torrc` or `/etc/torrc`

**Docker with Tor:**
When using Docker, you can use the official Tor Docker image or configure your host's Tor service.

## Docker Configuration

### Option 1: Using Host Tor (Recommended)
Run TorBot container with host network to use your existing Tor service:

```bash
docker run --rm --network="host" torbot:latest -u https://example.onion --depth 2
```

### Option 2: Tor as Sidecar Container
Use Docker Compose with Tor as a service:

```yaml
version: '3.8'
services:
  tor:
    image: dperson/torproxy:latest
    ports:
      - "9050:9050"
    restart: unless-stopped
    
  torbot:
    image: torbot:latest
    depends_on:
      - tor
    environment:
      - SOCKS5_HOST=tor
      - SOCKS5_PORT=9050
    command: -u https://example.onion --depth 2 --visualize tree
```

### Option 3: Tor in Same Container
For development/testing, you can install Tor in the TorBot container:

```dockerfile
FROM torbot:latest
RUN apt-get update && apt-get install -y tor
RUN echo "SOCKSPort 9050" >> /etc/tor/torrc
RUN echo "ControlPort 9051" >> /etc/tor/torrc
RUN echo "CookieAuthentication 1" >> /etc/tor/torrc
EXPOSE 9050 9051
```

## Configuration Files

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
