import sys
import os

path_info = "info_openflow.txt"

def abrir_archivo(un_path):
  archivo = None
  archivo = open(path_info,"r")
  if archivo.mode == 'r':
    print("Archivo abierto bien")
  return archivo
      
def cerrar_archivo(un_archivo):
  un_archivo.close()          
          
# def leer_una_linea(un_archivo):
#   lineas = archivo.readlines()
#   for lin in lineas:
#     return lin

def interpretar_regla(un_archivo):
    pass
    return regla

def interpretar_regla(linea):
    pass
    return comando

def aplicar_regla(una_regla, un_switch):
    pass

if __name__ == '__main__':
  path_info = "info_openflow.txt"
  output_script = abrir_archivo(path_info)
  for linea in output_script.readlines:
    

  cerrar_archivo(output_script)





#AYUDA

sudo ovs-ofctl --help
ovs-ofctl: OpenFlow switch management utility
usage: ovs-ofctl [OPTIONS] COMMAND [ARG...]

For OpenFlow switches:
  show SWITCH                 show OpenFlow information
  dump-desc SWITCH            print switch description
  dump-tables SWITCH          print table stats
  dump-table-features SWITCH  print table features
  dump-table-desc SWITCH      print table description (OF1.4+)
  mod-port SWITCH IFACE ACT   modify port behavior
  mod-table SWITCH MOD        modify flow table behavior
      OF1.1/1.2 MOD: controller, continue, drop
      OF1.4+ MOD: evict, noevict, vacancy:low,high, novacancy
  get-frags SWITCH            print fragment handling behavior
  set-frags SWITCH FRAG_MODE  set fragment handling behavior
      FRAG_MODE: normal, drop, reassemble, nx-match
  dump-ports SWITCH [PORT]    print port statistics
  dump-ports-desc SWITCH [PORT]  print port descriptions
  dump-flows SWITCH           print all flow entries
  dump-flows SWITCH FLOW      print matching FLOWs
  dump-aggregate SWITCH       print aggregate flow statistics
  dump-aggregate SWITCH FLOW  print aggregate stats for FLOWs
  queue-stats SWITCH [PORT [QUEUE]]  dump queue stats
  add-flow SWITCH FLOW        add flow described by FLOW
  add-flows SWITCH FILE       add flows from FILE
  mod-flows SWITCH FLOW       modify actions of matching FLOWs
  del-flows SWITCH [FLOW]     delete matching FLOWs
  replace-flows SWITCH FILE   replace flows with those in FILE
  diff-flows SOURCE1 SOURCE2  compare flows from two sources
  packet-out SWITCH IN_PORT ACTIONS PACKET...
                              execute ACTIONS on PACKET
  monitor SWITCH [MISSLEN] [invalid_ttl] [watch:[...]]
                              print packets received from SWITCH
  snoop SWITCH                snoop on SWITCH and its controller
  add-group SWITCH GROUP      add group described by GROUP
  add-groups SWITCH FILE      add group from FILE
  [--may-create] mod-group SWITCH GROUP   modify specific group
  del-groups SWITCH [GROUP]   delete matching GROUPs
  insert-buckets SWITCH [GROUP] add buckets to GROUP
  remove-buckets SWITCH [GROUP] remove buckets from GROUP
  dump-group-features SWITCH  print group features
  dump-groups SWITCH [GROUP]  print group description
  dump-group-stats SWITCH [GROUP]  print group statistics
  queue-get-config SWITCH [PORT]  print queue config for PORT
  add-meter SWITCH METER      add meter described by METER
  mod-meter SWITCH METER      modify specific METER
  del-meters SWITCH [METER]   delete meters matching METER
  dump-meters SWITCH [METER]  print METER configuration
  meter-stats SWITCH [METER]  print meter statistics
  meter-features SWITCH       print meter features
  add-tlv-map SWITCH MAP      add TLV option MAPpings
  del-tlv-map SWITCH [MAP] delete TLV option MAPpings
  dump-tlv-map SWITCH      print TLV option mappings
  dump-ipfix-bridge SWITCH    print ipfix stats of bridge
  dump-ipfix-flow SWITCH      print flow ipfix of a bridge
  ct-flush-zone SWITCH ZONE   flush conntrack entries in ZONE

For OpenFlow switches and controllers:
  probe TARGET                probe whether TARGET is up
  ping TARGET [N]             latency of N-byte echos
  benchmark TARGET N COUNT    bandwidth of COUNT N-byte echos
SWITCH or TARGET is an active OpenFlow connection method.

Other commands:
  ofp-parse FILE              print messages read from FILE
  ofp-parse-pcap PCAP         print OpenFlow read from PCAP

Active OpenFlow connection methods:
  tcp:HOST[:PORT]         PORT (default: 6653) at remote HOST
  ssl:HOST[:PORT]         SSL PORT (default: 6653) at remote HOST
  unix:FILE               Unix domain socket named FILE
PKI configuration (required to use SSL):
  -p, --private-key=FILE  file with private key
  -c, --certificate=FILE  file with certificate for private key
  -C, --ca-cert=FILE      file with peer CA certificate

Daemon options:
  --detach                run in background as daemon
  --monitor               creates a process to monitor this daemon
  --user=username[:group] changes the effective daemon user:group
  --no-chdir              do not chdir to '/'
  --pidfile[=FILE]        create pidfile (default: /var/run/openvswitch/ovs-ofctl.pid)
  --overwrite-pidfile     with --pidfile, start even if already running

OpenFlow version options:
  -V, --version           display version information
  -O, --protocols         set allowed OpenFlow versions
                          (default: OpenFlow10, OpenFlow11, OpenFlow12, OpenFlow13, OpenFlow14)

Logging options:
  -vSPEC, --verbose=SPEC   set logging levels
  -v, --verbose            set maximum verbosity level
  --log-file[=FILE]        enable logging to specified FILE
                           (default: /var/log/openvswitch/ovs-ofctl.log)
  --syslog-method=(libc|unix:file|udp:ip:port)
                           specify how to send messages to syslog daemon
  --syslog-target=HOST:PORT  also send syslog msgs to HOST:PORT via UDP

Other options:
  --strict                    use strict match for flow commands
  --read-only                 do not execute read/write commands
  --readd                     replace flows that haven't changed
  -F, --flow-format=FORMAT    force particular flow format
  -P, --packet-in-format=FRMT force particular packet in format
  -m, --more                  be more verbose printing OpenFlow
  --timestamp                 (monitor, snoop) print timestamps
  -t, --timeout=SECS          give up after SECS seconds
  --sort[=field]              sort in ascending order
  --rsort[=field]             sort in descending order
  --names                     show port names instead of numbers
  --no-names                  show port numbers, but not names
  --unixctl=SOCKET            set control socket name
  --color[=always|never|auto] control use of color in output
  -h, --help                  display this help message
  -V, --version               display version information
