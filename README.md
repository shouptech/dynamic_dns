# cloudflare_dynamicdns

A script to create/update a DNS A record in CloudFlare with your current public
IP address. This is intended in dynamic IP scenarios, such as a home Internet
connection with an IP that can change.

## Usage

```
usage: cloudflare_dynamicdns.py [-h] [-i IPURL] dnsname authemail authkey

Update DNS record in cloudflare to current IP

positional arguments:
  dnsname               DNS Name to update
  authemail             Cloudflare Auth Email
  authkey               Cloudflare Auth Key

optional arguments:
  -h, --help            show this help message and exit
  -i IPURL, --ipurl IPURL
                        URL to query for current IP address
```

## Example

```
./cloudflare.py home.example.com foo@bar.com secretkey
```
