import argparse
import paramiko
from paramiko.py3compat import b, u, decodebytes
import threading
import socket
import traceback
import sys
import base64
from binascii import hexlify

paramiko.util.log_to_file("demo_server.log")

host_key = paramiko.RSAKey(filename="test_rsa.key")
# host_key = paramiko.DSSKey(filename='test_dss.key')

print("Read key: " + u(hexlify(host_key.get_fingerprint())))
class Server(paramiko.ServerInterface):
  data = (
        b"AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp"
        b"fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC"
        b"KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT"
        b"UWT10hcuO4Ks8="
  )
  good_pub_key = paramiko.RSAKey(data=decodebytes(data))
  def __init__(self):
      self.event = threading.Event()
  def check_channel_request(self ,kind, chanid):
    if kind == 'session':
      return paramiko.OPEN_SUCCEEDED
  def check_auth_none(self,username):
    # if username == 'dill':
      return paramiko.AUTH_SUCCESSFUL
  def check_auth_publickey(self, username, key):
    return paramiko.AUTH_SUCCESSFUL
  def check_channel_shell_request(self ,channel):
    self.event.set()
    print("we enter shell")
    return True
  def check_auth_publickey(self, username, key):
        print("Auth attempt with key: " + u(hexlify(key.get_fingerprint())))
        return paramiko.AUTH_SUCCESSFUL


def main():
    parser = argparse.ArgumentParser(description='HONEY POT TIME')
    parser.add_argument('-p' , type=int) # bind this to the server. 
    args = parser.parse_args()
    print("this is the port you selected: " + str(args.p))
    # paramiko.Transport.start_server(server=Server)
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock.bind(("", 22))
      print("we binded that socket")
    except Exception as e:
      print("*** Bind failed: " + str(e))
      traceback.print_exc()
      sys.exit(1) 
    try:
      sock.listen(100)
      print("Listening for connection ...")
      client, addr = sock.accept()
      print(client)
    except Exception as e:
      print("*** Listen/accept failed: " + str(e))
      traceback.print_exc()
      sys.exit(1)  
    print("we connected")

    try:
      t = paramiko.Transport(client)
      paramiko.transport.Transport._preferred_keys += ('ssh-dss',)
      t.set_gss_host(socket.getfqdn(""))
      t.add_server_key(host_key)
      try:
        t.load_server_moduli()
      except:
        print("(Failed to load moduli -- gex will be unsupported.)")
        raise

      server = Server()
      try:
        t.start_server(server=server)
      except paramiko.SSHException:
        print("*** SSH negotiation failed.")
        sys.exit(1)
      chan = t.accept(20)
      if chan is None:
        print("*** No channel.")
        sys.exit(1)
      print("Authenticated!")

      server.event.wait(10)
      if not server.event.is_set():
        print("*** Client never asked for a shell.")
        sys.exit(1)
      chan.send("\r\n\r\nWelcome to my dorky little BBS!\r\n\r\n")
      chan.send(
        "We are on fire all the time!  Hooray!  Candy corn for everyone!\r\n"
      )
      chan.send("Happy birthday to Robot Dave!\r\n\r\n")
      chan.send("Username: ")
      f = chan.makefile("rU")
      username = f.readline().strip("\r\n")
      chan.send("\r\nI don't like you, " + username + ".\r\n")
      #chan.close()
      
      # t.start_server(server=server)
    except Exception as e:
      print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
      traceback.print_exc()


if __name__=='__main__':    
    main() 