# cfcommander

**cfcommander** is a simple CLI tool for managing DNS records in Cloudflare. After installing via `pip`, you can use it with the `cf` command.

## Installation

```bash
pip install cfcommander
```

## Configuration

Before using the tool, configure your Cloudflare API credentials:

```bash
cf config your_email@example.com your_api_key
```

This saves your credentials to `~/.cfcli_config.json`.

## Usage

### Add a DNS record

```bash
cf add example.com A home 192.0.2.1 yes 120
```

- `example.com` – The zone name (your domain).
- `A` – Record type (A, CNAME, etc.).
- `home` – Subdomain (creates `home.example.com`).
- `192.0.2.1` – The record value (e.g., an IP address).
- `yes` – Whether the record is proxied through Cloudflare (`yes/no`).
- `120` – TTL (Time-To-Live in seconds).

### Edit a DNS record

```bash
cf edit example.com A home 198.51.100.42 no 300
```

### Delete a DNS record

```bash
cf del example.com A home
```

### List all DNS records for a domain

```bash
cf list example.com
```

### List all manageable domains

```bash
cf domains
```

## Examples

```bash
# Configure API credentials
cf config user@example.com my_api_key

# Add an A record for home.example.com
cf add example.com A home 203.0.113.10 no 3600

# Modify an existing record
cf edit example.com A home 198.51.100.42 yes 1800

# Delete a record
cf del example.com A home

# List all DNS records for a domain
cf list example.com

# List all domains under your Cloudflare account
cf domains
```

## Dependencies

- Python 3.6+
- Required libraries: `requests`, `argparse`, `tabulate`, `json`, `sys`, `os`, `textwrap`

## License

MIT License © Jakub Jim Zacek
