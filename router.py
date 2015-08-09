# router parameter setting for updateros.py

# the router's IP for router access
edge_router_ip = '192.168.0.1'
# the public gateway IP (or its external IP in NATed))
edge_router_public_ip = '123.123.123.1'
# preferred source IP for IPIP tunnels
pref_source = '44.0.0.254'
# router's ssh port
ssh_port = 22
# router access credentials
username = 'admin'
password = 'password'
# default distance for IPIP routes
# allows more specific ones to take precedence
distance = 30

# your own networks
own_networks = [
    "44.182.0.0/16",    # all YO announcement
]


# blacklist BGP-announced networks with direct-routing agreements
bgp_networks = [
    "44.24.240.0/20",   # HamWAN Puget Sound
    "44.34.128.0/21",   # HamWAN Memphis
    "44.103.0.0/19",    # W8CMN Mi6WAN
]

