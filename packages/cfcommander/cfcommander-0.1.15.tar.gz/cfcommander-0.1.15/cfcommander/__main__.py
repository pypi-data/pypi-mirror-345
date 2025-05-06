#!/usr/bin/env python3

import argparse
import requests
import json
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from tabulate import tabulate
from .__about__ import __version__

# Configuration file path in the user's home directory
CONFIG_FILE = os.path.join(Path.home(), ".cfcli_config.json")

# ------------------------------------------------------------------------------
# Load / Save Configuration
# ------------------------------------------------------------------------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            if "api_key" not in config:
                print(f"Invalid configuration. Ensure 'api_key' is present in {CONFIG_FILE}.")
                sys.exit(1)
            return config
    else:
        print(f"Configuration file not found at {CONFIG_FILE}.")
        sys.exit(1)

def save_config(email, api_key):
    config = {"api_key": api_key, "email": email}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to {CONFIG_FILE}.")

# ------------------------------------------------------------------------------
# Utility: Get Zone ID
# ------------------------------------------------------------------------------
def get_zone_id(api_key, email, zone):
    url = f"https://api.cloudflare.com/client/v4/zones?name={zone}"
    headers = {
        "X-Auth-Email": email,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['success'] and len(data['result']) > 0:
            return data['result'][0]['id']
        else:
            print(f"Zone {zone} not found or invalid response: {data}")
            sys.exit(1)
    else:
        print(f"Failed to fetch zone ID: {response.text}")
        sys.exit(1)

# ------------------------------------------------------------------------------
# Add DNS Record
# ------------------------------------------------------------------------------

def add_record(api_key, email, zone, record_type, name, content, proxy, ttl):
    zone_id = get_zone_id(api_key, email, zone)
    list_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    url = f"{list_url}"
    headers = {
        "X-Auth-Email": email,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # 1) Fetch existing records
    existing_resp = requests.get(list_url, headers=headers)
    if existing_resp.status_code != 200:
        print(f"Failed to retrieve DNS records for pre-check: {existing_resp.text}")
        sys.exit(1)

    existing_records = existing_resp.json().get("result", [])
    fqdn = f"{name}.{zone}".lower()

    # 2) Check if the same name & type already exist
    found_same_name_type = next(
        (r for r in existing_records
         if r["type"] == record_type and r["name"].lower() == fqdn),
        None
    )
    if found_same_name_type:
        print(f"A DNS record for '{fqdn}' ({record_type}) already exists.")
        print("Use 'edit' to update it, 'del' to remove it, or choose a different name.")
        sys.exit(1)

    # If we get here, no duplicate name/type, so we proceed with creation
    today_str = datetime.now().strftime("%d/%m/%Y")
    data = {
        "type": record_type,
        "name": name,
        "content": content,
        "ttl": int(ttl),
        "proxied": (proxy.lower() == "yes"),
        "comment": f"cf autoadded record on {today_str} by {email}"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"DNS record added: {response.json()}")
    else:
        print(f"Failed to add DNS record: {response.text}")



# ------------------------------------------------------------------------------
# Edit (Update) DNS Record
# ------------------------------------------------------------------------------
def edit_record(api_key, email, zone, record_type, name, content, proxy, ttl):
    """
    Find the existing DNS record matching (record_type, name) and update it
    with new values (content, proxied, ttl), including a static comment.
    """
    zone_id = get_zone_id(api_key, email, zone)
    list_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "X-Auth-Email": email,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # First, get all records to find the matching record ID
    list_response = requests.get(list_url, headers=headers)
    if list_response.status_code == 200:
        records = list_response.json().get('result', [])
        fqdn = f"{name}.{zone}"
        matching_record = next(
            (r for r in records if r['type'] == record_type and r['name'].lower() == fqdn.lower()),
            None
        )

        if not matching_record:
            print(f"DNS record not found: {fqdn} ({record_type}).")
            sys.exit(1)

        record_id = matching_record['id']
        edit_url = f"{list_url}/{record_id}"

        # Current date in dd/mm/yyyy format
        today_str = datetime.now().strftime("%d/%m/%Y")

        update_data = {
            "type": record_type,
            "name": name,
            "content": content,
            "ttl": int(ttl),
            "proxied": (proxy.lower() == "yes"),
            # Automatically set a comment (description) with date + user's email
            "comment": f"cf autoedited record on {today_str} by {email}"
        }

        # Use PUT to overwrite record data
        edit_response = requests.put(edit_url, headers=headers, json=update_data)
        if edit_response.status_code == 200:
            edit_resp_json = edit_response.json()
            if edit_resp_json.get('success'):
                print(f"DNS record updated: {fqdn} ({record_type}).")
            else:
                print(f"Failed to update DNS record: {edit_resp_json}")
        else:
            print(f"Failed to update DNS record: {edit_response.text}")
    else:
        print(f"Failed to fetch DNS records: {list_response.text}")
        sys.exit(1)

# ------------------------------------------------------------------------------
# Delete DNS Record
# ------------------------------------------------------------------------------
def delete_record(api_key, email, zone, record_type, name):
    zone_id = get_zone_id(api_key, email, zone)
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "X-Auth-Email": email,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        records = response.json().get('result', [])
        fqdn = f"{name}.{zone}"
        record_id = next((r['id'] for r in records if r['type'] == record_type and r['name'].lower() == fqdn.lower()), None)
        if record_id:
            delete_url = f"{url}/{record_id}"
            delete_response = requests.delete(delete_url, headers=headers)
            if delete_response.status_code == 200:
                print(f"DNS record deleted: {name} ({record_type}).")
            else:
                print(f"Failed to delete DNS record: {delete_response.text}")
        else:
            print(f"DNS record not found: {name} ({record_type}).")
    else:
        print(f"Failed to fetch DNS records: {response.text}")

# ------------------------------------------------------------------------------
# List All DNS Records (with Description Column)
# ------------------------------------------------------------------------------
def list_records(api_key, email, zone):
    zone_id = get_zone_id(api_key, email, zone)
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "X-Auth-Email": email,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        records = response.json().get('result', [])
        if records:
            print(f"DNS records for zone {zone}:")

            grouped_records = defaultdict(list)
            for record in records:
                ttl_display = "Automatic" if record['ttl'] == 1 else record['ttl']
                wrapped_name = "\n".join(textwrap.wrap(record['name'], width=30))
                wrapped_content = "\n".join(textwrap.wrap(record['content'], width=50))

                # Safely handle 'comment' to avoid NoneType errors
                comment_text = record.get('comment') or 'N/A'
                wrapped_comment = "\n".join(textwrap.wrap(comment_text, width=30))

                grouped_records[record['type']].append([
                    wrapped_name,
                    wrapped_content,
                    ttl_display,
                    "Yes" if record['proxied'] else "No",
                    wrapped_comment
                ])

            for record_type, entries in grouped_records.items():
                print(f"\n{record_type} Records:")
                table_headers = ["Name", "Content", "TTL", "Proxied", "Description"]
                print(tabulate(entries, headers=table_headers, tablefmt="grid"))
        else:
            print(f"No DNS records found for zone {zone}.")
    else:
        print(f"Failed to fetch DNS records: {response.text}")

# ------------------------------------------------------------------------------
# List All Manageable Domains
# ------------------------------------------------------------------------------
def list_domains(api_key, email):
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {
        "X-Auth-Email": email,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            zones = data.get('result', [])
            if zones:
                print("Manageable Domains (Zones):")
                table_data = [[zone['id'], zone['name'], zone['status']] for zone in zones]
                print(tabulate(table_data, headers=["Zone ID", "Domain", "Status"], tablefmt="grid"))
            else:
                print("No manageable domains found.")
        else:
            print(f"Failed to fetch domains: {data}")
    else:
        print(f"Failed to fetch domains: {response.text}")

# ------------------------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Cloudflare DNS Management CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Configure command
    config_parser = subparsers.add_parser("config", help="Configure API credentials")
    config_parser.add_argument("email", help="Cloudflare account email")
    config_parser.add_argument("api_key", help="Cloudflare API key")

    # Add record command
    add_parser = subparsers.add_parser("add", help="Add a DNS record")
    add_parser.add_argument("zone", help="Zone name (e.g., example.com)")
    add_parser.add_argument("type", help="Record type (e.g., A, CNAME)")
    add_parser.add_argument("name", help="Record name (e.g., home)")
    add_parser.add_argument("content", help="Record content (e.g., IP address)")
    add_parser.add_argument("proxy", help="Proxy status (yes or no)")
    add_parser.add_argument("ttl", help="Time to live (TTL) in seconds")

    # Edit record command
    edit_parser = subparsers.add_parser("edit", help="Edit (update) a DNS record")
    edit_parser.add_argument("zone", help="Zone name (e.g., example.com)")
    edit_parser.add_argument("type", help="Record type (e.g., A, CNAME)")
    edit_parser.add_argument("name", help="Record name (e.g., home)")
    edit_parser.add_argument("content", help="New record content (e.g., new IP address)")
    edit_parser.add_argument("proxy", help="New proxy status (yes or no)")
    edit_parser.add_argument("ttl", help="New TTL in seconds")

    # Delete record command
    del_parser = subparsers.add_parser("del", help="Delete a DNS record")
    del_parser.add_argument("zone", help="Zone name (e.g., example.com)")
    del_parser.add_argument("type", help="Record type (e.g., A, CNAME)")
    del_parser.add_argument("name", help="Record name (e.g., home)")

    # List records command
    list_parser = subparsers.add_parser("list", help="List all DNS records for a zone")
    list_parser.add_argument("zone", help="Zone name (e.g., example.com)")

    # List domains command
    domains_parser = subparsers.add_parser("domains", help="List all manageable domains (zones)")

    # Print versioin
    domains_parser = subparsers.add_parser("version", help="Show cf version")

    args = parser.parse_args()

    # No command? Show help & examples
    if not args.command:
        parser.print_help()
        print("\nExamples:")
        print("  Configure API key:")
        print("    cf config your_email@example.com your_api_key")
        print("  Add DNS record:")
        print("    cf add example.com A home 192.0.2.1 yes 120")
        print("    cf add example.com CNAME www target.example.com no 300")
        print("  Edit DNS record:")
        print("    cf edit example.com A home 198.51.100.42 no 300")
        print("  Delete DNS record:")
        print("    cf del example.com A home")
        print("  List DNS records:")
        print("    cf list example.com")
        print("  List domains:")
        print("    cf domains")
        sys.exit(1)

    

    if args.command == "config":
        save_config(args.email, args.api_key)
    else:
        config = load_config()
        api_key = config["api_key"]
        email = config.get("email", "")

        
        if args.command == "add":
            add_record(api_key, email, args.zone, args.type, args.name, args.content, args.proxy, args.ttl)
        elif args.command == "edit":
            edit_record(api_key, email, args.zone, args.type, args.name, args.content, args.proxy, args.ttl)
        elif args.command == "version":
            print(f"version: {__version__}")

        elif args.command == "del":
            delete_record(api_key, email, args.zone, args.type, args.name)
        elif args.command == "list":
            list_records(api_key, email, args.zone)
        elif args.command == "domains":
            list_domains(api_key, email)
        else:
            parser.print_help()

if __name__ == "__main__":
    main()

