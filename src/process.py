import re
import requests
from pathlib import Path
from datetime import datetime

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
    # читаем домены
    domains = DOMAINS_FILE.read_text(encoding="utf-8").splitlines()
    regex = build_regex(domains)

    # скачиваем upstream hosts
    response = requests.get(HOSTS_URL, timeout=20)
    response.raise_for_status()

    # ищем совпадения
    matches = regex.findall(response.text)

    # дата генерации
    generated_date = datetime.utcnow().strftime("%Y-%m-%d")

    # формируем файл hosts
    content = [
        f"# Generated: {generated_date}",
        "",
    ]

    content.extend(f"{ip} {domain.lower()}" for ip, domain in matches)

    OUTPUT_FILE.write_text(
        "\n".join(content),
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
