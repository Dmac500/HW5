import argparse
import paramiko
from paramiko.py3compat import b, u, decodebytes
import threading
import socket
import traceback
import sys
import base64
import pathlib
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
  # def check_auth_none(self,username):
  #   # if username == 'dill'
  #     return paramiko.AUTH_SUCCESSFUL
  def check_auth_password(self,username, password):
      username =str(username)
      if str(username) == "Amir71" or str(username) == "devin43" or str(username) == "joy67" or str(username) == "mike134" or str(username) =="sarah63":
        print(username)
          #return paramiko.AUTH_FAILED 
        global Username
        Username = username
        global Bruteforce 
        Bruteforce += 1 
        print(Bruteforce)
        if Bruteforce == 5:
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

  # def check_channel_pty_request(self, channel, term: bytes, width: int, height: int, pixelwidth: int, pixelheight: int, modes: bytes) -> bool:
  #     super().check_channel_pty_request(channel, term, 10, 10, 10, 10, modes)
  #     return True


def main():
    parser = argparse.ArgumentParser(description='HONEY POT TIME')
    parser.add_argument('-p' , type=int) # bind this to the server. 
    args = parser.parse_args()
    print("this is the port you selected: " + str(args.p))
    # paramiko.Transport.start_server(server=Server)
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock.bind(("127.0.0.1", 2200))
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
      
      while True:
        chan = t.accept(20)
        print("start ")
        
        if Bruteforce >= 5:
         break
        
      
        if chan is None:
          print("*** No channel.")
          sock.listen(100)
          print("Listening for connection ...")
          client, addr = sock.accept()
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
      
          

          
        
      print("Authenticated!")
      path = pathlib.Path("root/")
      path.mkdir(parents=True,exist_ok=True)
      # (path / "apple.txt").write_text("this is apple1")
      # (path / "apple2.txt").write_text("this is apple2")
      # (path / "apple3.txt").write_text("this is apple3")
      
      chan.settimeout(60)
      server.event.wait(10)
      if not server.event.is_set():
        print("*** Client never asked for a shell.")
        sys.exit(1)
      running = True
      chan.send("\r\n\r\nWelcome to the sever\r\n\r\n")
      chan.send( "Time to test input!\r\n" )
      while running:
        chan.send(Username+"@honeypot:/$ " )
        f = chan.makefile("rU")
        command = f.readline().strip("\r\n")
        if command == "ls":
          x = list(path.glob("**/*.txt"))
          for i in x:
            name  = str(i).split("/")
            chan.send(str(name[1]) + "  ")
          chan.send("\r\n")
        getCommand = str(command).split(" ")
        print(getCommand)
        if getCommand[0] == "cat":
          if pathlib.PurePath(getCommand[1]).suffix == "":
            chan.send("Unknown file extension \r\n")
          else:
            file = path / getCommand[1]
            if file.exists():
              with file.open() as f:
                chan.send(f.readline())
              chan.send("\r\n")
            else:
              chan.send("File " + getCommand[1] + " not found\r\n")
        if getCommand[0] == "cp":
            file = path / getCommand[1]
            if file.exists():
              print("make it into file")
              with file.open() as f:
                print("try to make a new file")
                (path / getCommand[2]).write_text(f.readline())
            else:
              chan.send("File " + getCommand[1] + " not found\r\n")

      chan.close()
      
      # t.start_server(server=server)
    except Exception as e:
      print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
      traceback.print_exc()


if __name__=='__main__':
    Bruteforce = 0
    Username = ""    
    main() 