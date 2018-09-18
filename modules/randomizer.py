"""
Module for randomizing tor identity
"""
import socket

def randomize_IP(HOST, PORT, PWD):

	try:
    	tor_c = socket.create_connection((HOST, PORT))
    	tor_c.send('AUTHENTICATE "{}"\r\nSIGNAL NEWNYM\r\n'.format(PWD))
    	response = tor_c.recv(1024)
    	if response != '250 OK\r\n250 OK\r\n':
        	sys.stderr.write('Unexpected response from Tor control port: {}\n'.format(response))
	except Exception, e:
    	sys.stderr.write('Error connecting to Tor control port: {}\n'.format(repr(e)))



#def randomize_header():	



