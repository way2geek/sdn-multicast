from ofhelper import FlowEntry, GroupEntry
import json


# allocate variable names (see topology files in common dir for format)
switches = {}	# switches
hosts = {}		# all hosts, including low-capacity hosts but not transcoders
low_hosts = []	# low-capacity hosts
tees = {}		# transcoders
dpids = {}		# datapath id for each switch

# for each source host, store the list of output ports for each switch in tree
# used to build and track group entries
ports = {}
ports_lq = {}	# rooted at T

# shortest paths, from each switch
sp = {}

# different groups may be installed on each switch (one for each source-specific
# tree traversing the switch): keep track of the next available group id
gid = {}

# the multicast address reserved to this group
MCAST_ADDR = "239.192.0.1"
DSCP_VALUE = 63


def load_json_topology (filename):

	global switches
	global hosts
	global low_hosts
	global tees
	global dpids
	global gid

	filejson = open(filename)
	topojson = json.load(filejson)

	switches = topojson['switches']
	hosts = topojson['hosts']
	low_hosts = topojson['low_hosts']
	tees = topojson['tees']
	dpids = topojson['dpids']

	for sw in switches:
		gid[sw] = 1


def get_next_gid (sw):
	g = gid[sw]
	gid[sw] += 1
	return g


# Dijkstra's algorithm from switch src
def shortest_paths (src):

	dist = {}
	prev = {}

	tovisit = switches.keys()
	for node in tovisit:
		dist[node] = float('inf')
		prev[node] = None
	dist[src] = 0

	while len(tovisit) > 0:
		# extract node u closest to the set of visited nodes
		tovisit.sort(key = lambda x: dist[x])
		u = tovisit.pop(0)
		# for each neighbor v of u still unvisited, update distances
		for v in switches[u]:
			if v in tovisit:
				tmp = dist[u] + 1
				if tmp < dist[v]:
					dist[v] = tmp
					prev[v] = u

	return prev


def shortest_paths_all():
	for s in switches:
		sp[s] = shortest_paths(s)


def tree_ports_hq (sh): # source host
	done = set() # switches already part of the tree
	treeports = {}
	src = hosts[sh]['switch'] # source switch
	for dh in hosts: # high-capacity destination hosts
		if dh != sh and dh not in low_hosts:
			dst = hosts[dh]['switch'] # destination switch
			# walk back towards source until root (pre is None)
			# or another switch is found that is already part of the tree
			cur = dst # current switch
			pre = sp[src][cur] # parent of current switch
			while pre is not None and cur not in done:
				port = switches[pre][cur]
				if pre not in treeports:
					treeports[pre] = set()
				treeports[pre].add(port)
				# next iteration
				done.add(cur) # mark current switch as added to the tree
				cur = pre
				pre = sp[src][cur]
			# add destination host
			if dst not in treeports:
				treeports[dst] = set()
			treeports[dst].add(hosts[dh]['port'])
	for t in tees: # transcoders (also part of multicast group)
		dst = tees[t]['switch'] # destination switch
		# walk back towards source until root (pre is None)
		# or another switch is found that is already part of the tree
		cur = dst # current switch
		pre = sp[src][cur] # parent of current switch
		while pre is not None and cur not in done:
			port = switches[pre][cur]
			if pre not in treeports:
				treeports[pre] = set()
			treeports[pre].add(port)
			# next iteration
			done.add(cur) # mark current switch as added to the tree
			cur = pre
			pre = sp[src][cur]
		# add destination host
		if dst not in treeports:
			treeports[dst] = set()
		treeports[dst].add(tees[t]['port'])
	return treeports


def tree_ports_hq_all():
	for sh in hosts: # source host
		ports[sh] = tree_ports_hq(sh)


def tree_ports_lq (t): # source transcoder
	done = set() # switches already part of the tree
	treeports = {}
	src = tees[t]['switch'] # source switch
	for dh in low_hosts: # low-capacity destination hosts
		dst = hosts[dh]['switch'] # destination switch
		# walk back towards source until root (pre is None)
		# or another switch is found that is already part of the tree
		cur = dst # current switch
		pre = sp[src][cur] # parent of current switch
		while pre is not None and cur not in done:
			port = switches[pre][cur]
			if pre not in treeports:
				treeports[pre] = set()
			treeports[pre].add(port)
			# next iteration
			done.add(cur) # mark current switch as added to the tree
			cur = pre
			pre = sp[src][cur]
		# add destination host
		if dst not in treeports:
			treeports[dst] = set()
		treeports[dst].add(hosts[dh]['port'])
	return treeports


def tree_ports_lq_all():
	for t in tees:
		ports_lq[t] = tree_ports_lq(t)


def reverse_path_port (host, switch):
	root = host['switch'] # root switch of h's tree
	pre = sp[root][switch] # parent switch of current switch
	if pre is None: # current switch is root switch
		return host['port'] # local port towards host
	else:
		return switches[switch][pre] # local port towards parent switch


def install_hq_flows():
	for h in ports: # for each high-capacity source host
		for sw in ports[h]: # for each switch in the tree
			# group entry
			newgid = get_next_gid(sw)
			g = GroupEntry(dpids[sw], newgid, "ALL")
			i = 0
			for p in ports[h][sw]: # for each switch port in the tree
				g.addBucket()
				g.addAction(i, "OUTPUT", port=p)
				i += 1
			g.install()
			# flow entry (also match on in_port for reverse path check)
			f = FlowEntry(dpids[sw])
			f.addMatch("in_port", reverse_path_port(hosts[h],sw))
			f.addMatch("dl_type", 0x800)
			f.addMatch("nw_src", hosts[h]['ip'])
			f.addMatch("nw_dst", MCAST_ADDR)
			f.addAction("GROUP", group_id=newgid)
			f.install()


def install_lq_flows():
	for t in ports_lq: # for each transcoder as source
		for sw in ports_lq[t]: # for each switch in the tree
			# group entry
			newgid = get_next_gid(sw)
			g = GroupEntry(dpids[sw], newgid, "ALL")
			i = 0
			for p in ports_lq[t][sw]: # for each switch port in the tree
				g.addBucket()
				g.addAction(i, "OUTPUT", port=p)
				i += 1
			g.install()
			# flow entry (also match on in_port for reverse path check)
			# do not install on transcoder switch, tos is not set by T
			if not sw == tees[t]['switch']:
				f = FlowEntry(dpids[sw])
				f.addMatch("in_port", reverse_path_port(tees[t],sw))
				f.addMatch("dl_type", 0x800)
				f.addMatch("ip_dscp", DSCP_VALUE)
				f.addMatch("nw_src", tees[t]['ip'])
				f.addMatch("nw_dst", MCAST_ADDR)
				f.addAction("GROUP", group_id=newgid)
				f.install()
		# set ip_dscp when coming from T
		# the last group added to T's switch refers to the low-capacity tree
		tsw = tees[t]['switch']
		lastgid = gid[tsw]-1
		# flow entry (match on in_port, not nw_src, because original IP address
		# should be kept)
		f = FlowEntry(dpids[tsw])
		f.addMatch("in_port", tees[t]['port'])
		f.addMatch("dl_type", 0x800)
		f.addMatch("nw_dst", MCAST_ADDR)
		f.addAction("SET_FIELD", field="ip_dscp", value=DSCP_VALUE)
		f.addAction("GROUP", group_id=lastgid)
		f.install()


def dump_sp():
	for s in sp:
		# print "sp[%s]:" % (s, sp[s])
		print "sp[%s]: %s " % (s, sp[s])
	print #newline


def dump_ss_trees():
	for sh in hosts: # source host
		src = hosts[sh]['switch'] # source switch
		print "source: %s (%s)" % (sh,src)
		for dh in hosts: # destination hosts
			if dh != sh:
				dst = hosts[dh]['switch'] # destination switch
				print "  dest: %s (%s)" % (dh,dst)
				if dh not in low_hosts:
					print "    pre[%s]=%s, port=%d" % (dh,dst,hosts[dh]['port'])
				# walk back until root (pre is None)
				cur = dst # current switch
				pre = sp[src][cur] # parent of current switch
				while pre is not None:
					port = switches[pre][cur]
					print "    pre[%s]=%s, port=%d" % (cur,pre,port)
					cur = pre
					pre = sp[src][cur]

		for t in tees: # transcoders (also part of multicast group)
			dst = tees[t]['switch'] # destination switch
			print "  dest: %s (%s)" % (t,dst)
			# walk back towards source until root (pre is None)
			cur = dst # current switch
			pre = sp[src][cur] # parent of current switch
			while pre is not None:
				port = switches[pre][cur]
				print "    pre[%s]=%s, port=%d" % (cur,pre,port)
				cur = pre
				pre = sp[src][cur]

		portbuf = "ports:"
		for sw in ports[sh]:
			for port in ports[sh][sw]:
				portbuf += " %s-eth%d" % (sw,port)
		print portbuf
		print #newline


def dump_low_trees():
	for t in tees: # source transcoder
		src = tees[t]['switch'] # source switch
		print "source: %s (%s)" % (t,src)
		for dh in low_hosts: # destination low-capacity hosts
			dst = hosts[dh]['switch'] # destination switch
			print "  dest: %s (%s)" % (dh,dst)
			print "    pre[%s]=%s, port=%d" % (dh,dst,hosts[dh]['port'])
			# walk back until root (pre is None)
			cur = dst # current switch
			pre = sp[src][cur] # parent of current switch
			while pre is not None:
				port = switches[pre][cur]
				print "    pre[%s]=%s, port=%d" % (cur,pre,port)
				cur = pre
				pre = sp[src][cur]
		portbuf = "ports:"
		for sw in ports_lq[t]:
			for port in ports_lq[t][sw]:
				portbuf += " %s-eth%d" % (sw,port)
		print portbuf
		print #newline


def menu():

	options = [
		{'str': "Quit", 'action': None},
		{'str': "Dump shortest paths", 'action': dump_sp},
		{'str': "Dump source-specific trees", 'action': dump_ss_trees},
		{'str': "Dump low-capacity trees", 'action': dump_low_trees}
	]

	while True: # until quit
		while True: # while bad input

			for i in range(len(options)):
				print "  %d - %s" % (i, options[i]['str'])
			print #newline

			try:
				choice = int(raw_input("Choose an option: "))
				if choice < 0 or choice >= len(options):
					raise ValueError
				break
			except ValueError:
				print "Invalid choice: enter a number between 0 and %d" \
				  % (len(options)-1)
			except (EOFError, KeyboardInterrupt):
				print #newline
				choice = 0
				break

		print #newline

		if choice == 0: # quit
			break

		if not options[choice]['action'] is None:
			options[choice]['action']()


if __name__ == "__main__":
	print "** Loading topology **"
	load_json_topology("topo/topo1.json")
	print "** Generating shortest paths (source-specific trees) **"
	shortest_paths_all()
	print "** Generating port sets for high-capacity trees **"
	tree_ports_hq_all()
	print "** Generating port sets for low-capacity trees **"
	tree_ports_lq_all()
	print "** Installing flows for high-quality traffic **"
	install_hq_flows()
	print "** Installing flows for low-quality traffic **"
	install_lq_flows()
	menu()
