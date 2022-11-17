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


class Gandi:
    def __init__(self, dnsname, authkey):
        self.dnsname = dnsname
        self.authheader = {"Authorization": f"Apikey {authkey}"}

        # In Gandi's docs, fqdn is the name of the dns zone
        self.fqdn = ".".join(dnsname.split(".")[-2:])
        self.record = ".".join(dnsname.split(".")[:-2])

        self.api_url = "https://api.gandi.net/v5/livedns"

    def get_dns_record(self):
        """Returns the current address record and id"""
        url = "%s/domains/%s/records/%s/A" % (
            self.api_url,
            self.fqdn,
            self.record,
        )
        response = requests.get(url, headers=self.authheader)
        if response.status_code == 200:
            return {
                "address": response.json()["rrset_values"][0],
                "id": response.json()["rrset_name"],
            }
        if not response.ok and response.status_code != 404:
            response.raise_for_status()
        return None

    def create_dns(self, ip):
        """Creates the dns record with value of ip"""
        url = "%s/domains/%s/records/%s/A" % (
            self.api_url,
            self.fqdn,
            self.record,
        )
        payload = {"rrset_values": [ip], "rrset_ttl": 300}
        response = requests.post(url, headers=self.authheader, json=payload)
        if not response.ok:
            response.raise_for_status()
        return response

    def update_dns(self, ip):
        """Updates the dns record with value of ip"""
        url = "%s/domains/%s/records/%s/A" % (
            self.api_url,
            self.fqdn,
            self.record,
        )
        payload = {"rrset_values": [ip], "rrset_ttl": 300}
        response = requests.put(url, headers=self.authheader, json=payload)
        if not response.ok:
            response.raise_for_status()
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
    parser.add_argument(
        "provider", choices=["cloudflare", "gandi"], help="Which DNS provider to use"
    )
    parser.add_argument("dnsname", help="DNS Name to update")
    parser.add_argument(
        "authemail",
        help="Account Email, only needed for cloudflare. Value is not used for Gandi.",
    )
    parser.add_argument("authkey", help="API Key for provider")
    args = parser.parse_args()

    if args.provider == "gandi":
        provider = Gandi(args.dnsname, args.authkey)
    else:
        provider = CloudFlare(args.dnsname, args.authemail, args.authkey)

    myip = get_ip(args.ipurl)

    curdns = provider.get_dns_record()

    if curdns == None:
        print("DNS record does not exist. Creating record:")
        print("%s - %s" % (args.dnsname, myip))
        response = provider.create_dns(myip)
        print(response.json())

    elif myip == curdns["address"]:
        print("IPs match: %s == %s, doing nothing" % (myip, curdns["address"]))

    else:
        print("DNS record does not match current IP. Updating record:")
        print("Old value: %s - %s" % (args.dnsname, curdns["address"]))
        print("New value: %s - %s" % (args.dnsname, myip))
        response = provider.update_dns(myip)
        print(response.json())


if __name__ == "__main__":
    main()
