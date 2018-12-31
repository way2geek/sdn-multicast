import subprocess

print subprocess.call(['ryu-manager', 'igmpPrueba.py &'])

print subprocess.check_output(['python', 'topologia.py', '&'])
