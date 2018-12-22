import subprocess

print subprocess.check_output(['vlc', '/home/wal/Desktop/videotest.mpg', '--sout', '#standard{access= http,mux=ts,dst=localhost:8080'])

# vlc  videotest.mpg --sout '#standard{access= http,mux=ts,dst=localhost:8080'
