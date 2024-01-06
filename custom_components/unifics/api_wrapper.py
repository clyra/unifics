import logging
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
import ssl
from enum import Enum
from pyunifi import controller

_LOGGER = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

def create_client( host, port, username, password, site, cert, udm):
    '''create a controller and return a error code if any'''

    if cert == True:
       ssl_verify = True
    else:
       ssl_verify = False           
    
    if udm == True:
        server_type = "UDMP-unifiOS"
    else:
      server_type = "v5"

    try:
        _LOGGER.debug('host={}, port={}, username={}, site={}, cert={}, udm={}'.format(host, port, username, site, ssl_verify, udm))
        client = controller.Controller ( host,
                              username,
                              password, 
                              port = port,
                              site_id = site,
                              ssl_verify = ssl_verify,
                              version = server_type 
                             )
    except Exception as e:
        _LOGGER.error("pyunify error: %s", e)
        if udm == True:
            _LOGGER.error("changing version to unifiOS and trying again")
            try:
                server_type = "unifiOS"
                client = controller.Controller ( host,
                              username,
                              password, 
                              port = port,
                              site_id = site,
                              ssl_verify = ssl_verify,
                              version = server_type 
                             )
            except Exception as e:
                _LOGGER.error("pyunify error: %s", e)

    _LOGGER.debug("unificontrol: OK") 
    return { 'client': client, 'error': 'ok'}

def client_get_data(client):
    '''receive a unifi client and returns a dictionary with all ap/wlans/clients'''

    data = {}
    try: 
      data["aps"] = client.get_aps()
      data["wlans"] = client.get_wlan_conf()
      data["clients"] = client.get_clients()
    except Exception as e:
        _LOGGER.error("pyunify error: %s", e)
        
    return data