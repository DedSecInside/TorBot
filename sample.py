import sys
if __name__ == '__main__':
 from stem.control import Controller
 with Controller.from_port(port = 9051) as controller:
  controller.authenticate() # controller.authenticate("yourpassphrase")
  bytes_read = controller.get_info("traffic/read")
  bytes_written = controller.get_info("traffic/written")
  print("My Tor relay has read %s bytes and written %s." % (bytes_read, bytes_written))

  if not controller:
    sys.exit(1)  # unable to get a connection

  print ("Connection is Working Properly")
  controller.close()

