import re
import requests
from pathlib import Path

HOSTS_URL = "https://raw.githubusercontent.com/Internet-Helper/GeoHideDNS/refs/heads/main/hosts/hosts"

# пути относительно корня репозитория
DOMAINS_FILE = Path("domains.txt")
OUTPUT_FILE = Path("hosts")


def build_regex(domains):
    escaped = [re.escape(d.strip().lower()) for d in domains if d.strip()]
    domains_part = "|".join(escaped)

    pattern = rf"""
        ^\s*
        (\d{{1,3}}(?:\.\d{{1,3}}){{3}})
        \s+
        ({domains_part})
        \s*$
    """
    return re.compile(pattern, re.IGNORECASE | re.MULTILINE | re.VERBOSE)


def main():
    domains = DOMAINS_FILE.read_text(encoding="utf-8").splitlines()
    regex = build_regex(domains)

    response = requests.get(HOSTS_URL, timeout=20)
    response.raise_for_status()

    matches = regex.findall(response.text)

    OUTPUT_FILE.write_text(
        "\n".join(f"{ip} {domain.lower()}" for ip, domain in matches),
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
