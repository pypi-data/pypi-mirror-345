# dnscontroller

A minimal command-line tool for managing DNS records via Cloudflare with a clean and intuitive interface.

For more powerful similar tools I recommend:
- [cfcli](https://github.com/danielpigott/cloudflare-cli)
- [dnscontrol](https://github.com/StackExchange/dnscontrol)


## Installation

The package can be installed using `uv`:

```bash
uv tool install dnscontroller
```

## Configuration

Create a configuration file at `~/.cfcli.yml` with your Cloudflare API token:

```yaml
defaults:
  token: your-cloudflare-api-token
```

## Usage

### List Domains and Records

List all available domains:
```bash
dnscontroller ls
```

List DNS records for a specific domain:
```bash
dnscontroller ls example.com
```

### Manage DNS Records

Create or update a DNS record:
```bash
dnscontroller set A www.example.com 192.168.1.1 --ttl 1h
```

Supported TTL formats:
- `auto` (default)
- Seconds (e.g., `300`)
- Minutes (e.g., `5min`)
- Hours (e.g., `1h`)
- Days (e.g., `1d`)

Delete a DNS record:
```bash
dnscontroller rm A www.example.com
```
