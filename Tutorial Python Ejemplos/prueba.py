flood_addrs = [
    ('01:80:c2:00:00:00', '01:80:c2:00:00:00'), # 802.x Spanning Tree Protocol (for bridges) IEEE 802.1D
    ('01:00:5e:00:00:00', 'ff:ff:ff:00:00:00'), # IPv4 multicast
    ('33:33:00:00:00:00', 'ff:ff:00:00:00:00'), # IPv6 multicast
    ('ff:ff:ff:ff:ff:ff', None) # Ethernet broadcast
]

for i in flood_addrs:
    print flood_addrs[i]
