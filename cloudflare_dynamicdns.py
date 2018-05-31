#!/usr/bin/env python

import argparse
import requests

def get_ip(ipurl):
    """ Retrieves current IP """
    response = requests.get(ipurl)
    return response.text.strip()

def get_zone_id(dnsname, authemail, authkey):
    """ Return zone id """
    headers = {
        'X-Auth-Email': authemail,
        'X-Auth-Key': authkey
    }
    params = {
        'name': "%s.%s" % tuple(dnsname.split('.')[-2:])
    }
    url = 'https://api.cloudflare.com/client/v4/zones'
    response = requests.get(url, headers=headers, params=params)
    return response.json()['result'][0]['id']

def get_dns_record(zoneid, dnsname, authemail, authkey):
    """ Get DNS record address and id """
    headers = {
        'X-Auth-Email': authemail,
        'X-Auth-Key': authkey
    }
    params = {
        'name': dnsname,
        'type': 'A'
    }
    url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records" % zoneid
    response = requests.get(url, headers=headers, params=params)

    if response.json()['result_info']['total_count'] > 0:
        return {
            'id': response.json()['result'][0]['id'],
            'address': response.json()['result'][0]['content']
        }
    return None

def create_dns(zoneid, dnsname, ip, authemail, authkey):
    """ Create DNS record """
    headers = {
        'X-Auth-Email': authemail,
        'X-Auth-Key': authkey
    }
    payload = {
        'type': 'A',
        'name': dnsname,
        'content': ip,
        'ttl': 120,
        'proxied': False
    }
    url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records" % zoneid
    response = requests.post(url, headers=headers, json=payload)
    return response


def update_dns(zoneid, recordid, dnsname, ip, authemail, authkey):
    """ Update DNS record """
    headers = {
        'X-Auth-Email': authemail,
        'X-Auth-Key': authkey
    }
    payload = {
        'type': 'A',
        'name': dnsname,
        'content': ip
    }
    url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s" % (
        zoneid, recordid)
    response = requests.put(url, headers=headers, json=payload)
    return response

def main():
    """ Parse arguments and update IP as needed """

    parser = argparse.ArgumentParser(
        description='Update DNS record in cloudflare to current IP')
    parser.add_argument('-i', '--ipurl', default='http://v4.ifconfig.co/ip',
        help='URL to query for current IP address')
    parser.add_argument('dnsname', help='DNS Name to update')
    parser.add_argument('authemail', help='Cloudflare Auth Email')
    parser.add_argument('authkey', help='Cloudflare Auth Key')
    args = parser.parse_args()

    zoneid = get_zone_id(args.dnsname, args.authemail, args.authkey)
    myip = get_ip(args.ipurl)

    curdns = get_dns_record(zoneid, args.dnsname, args.authemail, args.authkey)

    if curdns == None:
        print("DNS record does not exist. Creating record:")
        print("%s - %s" % (args.dnsname, myip))
        response = create_dns(
            zoneid, args.dnsname, myip, args.authemail, args.authkey)
        print(response.json())

    elif myip == curdns['address']:
        print("IPs match: %s == %s, doing nothing" % (myip, curdns['address']))

    else:
        print("DNS record does not match current IP. Updating record:")
        print("Old value: %s - %s" % (args.dnsname, curdns['address']))
        print("New value: %s - %s" % (args.dnsname, myip))
        response = update_dns(zoneid,
            curdns['id'], args.dnsname, myip, args.authemail, args.authkey)
        print(response.json())

if __name__ == '__main__':
    main()
