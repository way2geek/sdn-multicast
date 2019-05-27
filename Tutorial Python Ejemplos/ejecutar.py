# http://docs.python.org/dev/library/subprocess.html#using-the-subprocess-module

# import os
import sys
import subprocess
from subprocess import Popen, PIPE
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController

p1 = subprocess.Popen(["python3", "leer_topo_json.py", "1-topo_linear_pequena.json"], stdout=subprocess.PIPE)
# p2 = subprocess.Popen(["bar", sys.argv[2]], stdin=p1.stdout)
# sys.exit(p1.wait())


# os.system("python3 leer_topo_json.py")

# subprocess.Popen("python3 leer_topo_json.py", shell=False)


# output = Popen(['python','leer_topo_json.py','1-topo_linear_pequena.json'], stdout=PIPE)
# print (output)


# p = Popen("/usr/bin/gnome-terminal", stdin=PIPE)
# p.communicate("python prueba.py")

# pid = subprocess.Popen(args=["gnome-terminal", "--command=python prueba.py"]).pid
# print (pid)


cmd = 'python leer_topo_json.py 1-topo_linear_pequena.json'

# p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
# out, err = p.communicate()
# # result = out.split('\n')
# for lin in out:
#     if not lin.startswith('#'):
#         print(lin)


# ret_value = subprocess.run(["leer_topo_json.py 1-topo_linear_pequena.json"]) FALLA
print ("FIN EJECUTAR...")



# subprocess.run(["ls", "-l"])  # doesn't capture output
# CompletedProcess(args=['ls', '-l'], returncode=0)
#
# >>> subprocess.run("exit 1", shell=True, check=True)
# Traceback (most recent call last):
#   ...
# subprocess.CalledProcessError: Command 'exit 1' returned non-zero exit status 1
#
# >>> subprocess.run(["ls", "-l", "/dev/null"], capture_output=True)
# CompletedProcess(args=['ls', '-l', '/dev/null'], returncode=0,
# stdout=b'crw-rw-rw- 1 root root 1, 3 Jan 23 16:23 /dev/null\n', stderr=b'')
