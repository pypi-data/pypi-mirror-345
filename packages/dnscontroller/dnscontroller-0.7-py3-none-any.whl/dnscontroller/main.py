import json
import os

import rich_click as click
import yaml
from cloudflare import Cloudflare
from rich.console import Console
from rich.table import Table

console = Console()
_cf_client = None


def get_api_key():
    """
    Credit to https://github.com/danielpigott/cloudflare-cli for the config format specification this script piggybacks
    on.
    """
    # First try to get API key from environment variable
    api_key = os.environ.get("CF_API_KEY")
    if api_key:
        return api_key

    # Fall back to config file
    config_path = os.path.expanduser("~/.cfcli.yml")
    if not os.path.exists(config_path):
        raise click.ClickException(
            f"API key missing. Please set CF_API_KEY environment variable or create {config_path} with your Cloudflare "
            "credentials."
        )

    with open(config_path) as f:
        config = yaml.safe_load(f)

    if not config.get("defaults", {}).get("token"):
        raise click.ClickException(f"Cloudflare API token not found in {config_path}")

    return config["defaults"]["token"]


def get_cf_client():
    global _cf_client
    if _cf_client is None:
        _cf_client = Cloudflare(api_token=get_api_key())
    return _cf_client


def parse_ttl(ttl_str):
    if ttl_str == "auto":
        return 1
    if ttl_str.endswith("min"):
        return int(ttl_str[:-3]) * 60
    if ttl_str.endswith("h"):
        return int(ttl_str[:-1]) * 3600
    if ttl_str.endswith("d"):
        return int(ttl_str[:-1]) * 86400
    return int(ttl_str)


@click.group()
def main():
    """dnscontroller - Manage DNS records in Cloudflare"""
    pass


@main.command()
@click.argument("domain", required=False)
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
def ls(domain, json_output):
    """List DNS records. If domain is not specified, list from all domains."""
    cf = get_cf_client()

    if domain:
        domains = [domain]
    else:
        domains = (zone.name for zone in cf.zones.list())

    all_records = []
    for domain in domains:
        zones = list(cf.zones.list(name=domain))
        if not zones:
            raise click.ClickException(f'Domain (zone) "{domain}" not found')
        zone_id = zones[0].id
        records = list(cf.dns.records.list(zone_id=zone_id))

        if json_output:
            domain_records = []
            for record in records:
                domain_records.append(
                    {
                        "type": record.type,
                        "name": record.name,
                        "content": record.content,
                        "ttl": record.ttl,
                        "proxied": record.proxied,
                        "domain": domain,
                    }
                )
            all_records.extend(domain_records)
        else:
            table = Table(title=f"DNS Records for {domain}")
            table.add_column("Type")
            table.add_column("Name")
            table.add_column("Content")
            table.add_column("TTL")
            table.add_column("CF Proxy")
            for record in records:
                table.add_row(
                    record.type, record.name, record.content, str(record.ttl), "On" if record.proxied else "Off"
                )
            console.print(table)
    if json_output:
        if console.is_interactive:
            console.print(json.dumps(all_records, indent=2))
        else:
            print(json.dumps(all_records, indent=2))


def get_record_info(name, record_type):
    parts = name.split(".")
    if len(parts) < 2:
        raise click.ClickException("Invalid DNS name format")

    domain = ".".join(parts[-2:])
    record_full_name = name if name.endswith(domain) else f"{name}.{domain}"

    cf = get_cf_client()
    zones = list(cf.zones.list(name=domain))
    if not zones:
        raise click.ClickException(f'Domain (zone) "{domain}" not found')

    zone_id = zones[0].id
    records = list(cf.dns.records.list(zone_id=zone_id, name=record_full_name, type=record_type))

    return zone_id, record_full_name, records


@main.command()
@click.argument("record_type")
@click.argument("name")
@click.argument("content")
@click.option("--ttl", default="auto", help="TTL value (e.g. 300, 5min, 1h, 1d, auto)")
@click.option("--proxy/--no-proxy", default=None, help="Enable/disable Cloudflare proxy for this record")
def set(record_type, name, content, ttl, proxy):
    """Set a DNS record. UPSERT semantics."""
    cf = get_cf_client()
    zone_id, record_full_name, records = get_record_info(name, record_type)

    data = {
        "zone_id": zone_id,
        "type": record_type,
        "name": record_full_name,
        "content": content,
        "ttl": parse_ttl(ttl),
    }
    if proxy is not None:
        data["proxied"] = proxy

    if records:
        # Update existing record
        data["dns_record_id"] = records[0].id
        cf.dns.records.update(**data)
        console.print(f"[green]Updated {record_type} record for {record_full_name}[/green]")
    else:
        # Create new record
        cf.dns.records.create(**data)
        console.print(f"[green]Created {record_type} record for {record_full_name}[/green]")


@main.command()
@click.argument("record_type")
@click.argument("name")
def rm(record_type, name):
    """Remove a DNS record."""
    cf = get_cf_client()
    zone_id, record_full_name, records = get_record_info(name, record_type)

    if not records:
        console.print(f"[red]No {record_type} record found for {record_full_name}[/red]")
        return

    record_id = records[0].id
    cf.dns.records.delete(zone_id=zone_id, dns_record_id=record_id)
    console.print(f"[green]Deleted {record_type} record for {record_full_name}[/green]")


if __name__ == "__main__":
    main()
