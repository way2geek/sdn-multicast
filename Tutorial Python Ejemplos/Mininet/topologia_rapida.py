import subprocess

print subprocess.check_output(['sudo', 'mn', '--controller=remote,', 'ip=127.0.0.1', '--mac', '-i', '10.0.0.0/24', '--switch=ovsk,protocols=OpenFlow13', '--topo=single,4'])

#sudo mn --controller=remote, ip=127.0.0.1 --mac -i 10.0.0.0/24 --switch=ovsk,protocols=OpenFlow13 --topo=single,4
