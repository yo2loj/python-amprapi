# AMPR API settings

# Be sure to include trailing slash in API_URL
API_URL = 'https://portal.ampr.org/api/'
API_USER = 'user'
API_KEY = 'SOMEAPIKEY'
CHECK_VERSION = True

# ROS API setting

edge_router_ip = '192.168.0.1'
username = 'admin'
password = 'password'

# router settings

edge_router_public_ip = '1.2.3.4'
pref_source = '44.x.y.z'
distance = 30

# own networks and BGP
ignore_networks = [
    "44.24.240.0/20",   # HamWAN Puget Sound
    "44.34.128.0/21",   # HamWAN Memphis
    "44.103.0.0/19",    # W8CMN Mi6WAN
]

