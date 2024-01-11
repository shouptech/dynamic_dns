# DynamicDNS Script

A script to create/update a DNS A record in with your current public IP address. This is
intended in dynamic IP scenarios, such as a home Internet connection with an IP that can
change.

This script supports both CloudFlare and Gandi LiveDNS as DNS providers.

## Usage

```shell
usage: dynamic_dns.py [-h] [-i IPURL] {cloudflare,gandi} dnsname authemail authkey

Update DNS record in cloudflare to current IP

positional arguments:
  {cloudflare,gandi}    Which DNS provider to use
  dnsname               DNS Name to update
  authemail             Account Email, only needed for cloudflare. Value is not used for Gandi.
  authkey               API Key for provider

options:
  -h, --help            show this help message and exit
  -i IPURL, --ipurl IPURL
                        URL to query for current IP address
```

## Example

### CloudFlare Usage

```shell
./dynamic_dns.py cloudflare home.example.com foo@bar.com secretkey
```

### Gandi Usage

This script supports a personal access token, not the deprecated API keys.

```shell
./dynamic_dns.py gandi home.example.com foo@bar.com personaltoken
```
