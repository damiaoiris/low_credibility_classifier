import os
from collections import namedtuple

import sys

import pyasn
import geoip2.database

import pkg_resources

ASN_DB = 'ipasn_data'
GEO_DB = 'GeoLite2-Country.mmdb'

current_dir = os.path.realpath(__file__)
par_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

class NetworkInfo:
    IpInfo = namedtuple('IpAddressInfo', 'asn, cidr, geoloc')
    
    def __init__(self):

        os.chdir(par_dir)
        self.geodb = geoip2.database.Reader(GEO_DB) 
        self.asndb = pyasn.pyasn('ipasn_data')
        print(self.asndb)

    def ip_lookup(self, ip):
        asn = None,
        cidr = None
        try:
             asn, cidr = self.asndb.lookup(ip)
        except Exception as e:
            pass

        iso = None
        try: 
            response = self.geodb.country(ip)
            if response:
                iso = response.country.iso_code
        except Exception as e:
            pass
    
        return NetworkInfo.IpInfo(asn, cidr, iso)

    def network_lookup(self, cidr):
        pass
