import httplib
import json
import random
import socket
import string
import urllib

PIA_SERVER = 'www.privateinternetaccess.com'

def get_active_local_ip():
    # This needs some extra checking and separating the one-liner into easier to read code.
    # v1.0 code wasn't getting an address and was rather returning a GAI Error
    # Refs
    # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    # https://stackoverflow.com/questions/22851609/python-errno-11001-getaddrinfo-failed
    # Get active local IP
    # tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # tcp_socket.connect((PIA_SERVER, 0))
        # return tcp_socket.getsockname()[0]
        return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    except socket.gaierror:
        print 'ignoring failed address lookup'
#    finally:
#        tcp_socket.close()

def generate_client_id():
    # Generate client ID
    # This is specific for the Windows PIA Manager!  It needs the client id used by the software to get the correct port!
    # Should check was platform the software is being run on and check for pa_manager in the process tree (instead of an openvpn connection)
    with open(r'C:\Program Files\pia_manager\data\client_id.txt', 'r') as f:
        id = f.readline()
    return id
#    return ''.join( random.choice(string.hexdigits) for char in xrange(32) #).lower()

def acquire_port( user_name, password, client_id, local_ip, log ):
    # Set up parameters
    values = urllib.urlencode({'user':user_name,
                               'pass':password,
                               'client_id':client_id,
                               'local_ip':local_ip})

    # Send request
    connection = httplib.HTTPSConnection(PIA_SERVER)
    connection.request('POST', '/vpninfo/port_forward_assignment', values)
    response = connection.getresponse()

    # Process response
    status_code_ok = 200
    if response.status != status_code_ok:
        log( '{}: '.format(response.status) + response.reason )
        return

    # Extract port from json data
    data = json.load(response)

    if 'port' not in data:
        log( data['error'] )
        return

    return data['port']
