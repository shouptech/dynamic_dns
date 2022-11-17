#!/usr/bin/env python3

import argparse
import requests


class CloudFlare:
    def __init__(self, dnsname, authemail, authkey):
        self.dnsname = dnsname
        self.authemail = authemail
        self.authkey = authkey
        self.record_id = None
        self._set_zone_id()

    def _set_zone_id(self):
        """Return zone id"""
        headers = {"X-Auth-Email": self.authemail, "X-Auth-Key": self.authkey}
        params = {"name": "%s.%s" % tuple(self.dnsname.split(".")[-2:])}
        url = "https://api.cloudflare.com/client/v4/zones"
        response = requests.get(url, headers=headers, params=params)
        self.zone_id = response.json()["result"][0]["id"]

    def get_dns_record(self):
        """Get DNS record address and id"""
        headers = {"X-Auth-Email": self.authemail, "X-Auth-Key": self.authkey}
        params = {"name": self.dnsname, "type": "A"}
        url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records" % self.zone_id
        response = requests.get(url, headers=headers, params=params)

        if response.json()["result_info"]["total_count"] > 0:
            results = {
                "id": response.json()["result"][0]["id"],
                "address": response.json()["result"][0]["content"],
            }
            self.record_id = results["id"]
            return results
        return None

    def create_dns(self, ip):
        """Create DNS record"""
        headers = {"X-Auth-Email": self.authemail, "X-Auth-Key": self.authkey}
        payload = {
            "type": "A",
            "name": self.dnsname,
            "content": ip,
            "ttl": 120,
            "proxied": False,
        }
        url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records" % self.zone_id
        response = requests.post(url, headers=headers, json=payload)
        return response

    def update_dns(self, ip):
        """Update DNS record"""
        headers = {"X-Auth-Email": self.authemail, "X-Auth-Key": self.authkey}
        payload = {"type": "A", "name": self.dnsname, "content": ip}
        url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s" % (
            self.zone_id,
            self.record_id,
        )
        response = requests.put(url, headers=headers, json=payload)
        return response


def get_ip(ipurl):
    """Retrieves current IP"""
    response = requests.get(ipurl)
    return response.text.strip()


def main():
    """Parse arguments and update IP as needed"""

    parser = argparse.ArgumentParser(
        description="Update DNS record in cloudflare to current IP"
    )
    parser.add_argument(
        "-i",
        "--ipurl",
        default="http://ifconfig.me/ip",
        help="URL to query for current IP address",
    )
    parser.add_argument("dnsname", help="DNS Name to update")
    parser.add_argument("authemail", help="Cloudflare Auth Email")
    parser.add_argument("authkey", help="Cloudflare Auth Key")
    args = parser.parse_args()

    cloudflare = CloudFlare(args.dnsname, args.authemail, args.authkey)
    myip = get_ip(args.ipurl)

    curdns = cloudflare.get_dns_record()

    if curdns == None:
        print("DNS record does not exist. Creating record:")
        print("%s - %s" % (args.dnsname, myip))
        response = cloudflare.create_dns(myip)
        print(response.json())

    elif myip == curdns["address"]:
        print("IPs match: %s == %s, doing nothing" % (myip, curdns["address"]))

    else:
        print("DNS record does not match current IP. Updating record:")
        print("Old value: %s - %s" % (args.dnsname, curdns["address"]))
        print("New value: %s - %s" % (args.dnsname, myip))
        response = cloudflare.update_dns(myip)
        print(response.json())


if __name__ == "__main__":
    main()
