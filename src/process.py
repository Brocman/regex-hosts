import re
import requests
from pathlib import Path
from datetime import datetime

# файлы проекта
DOMAINS_FILE = Path("domains.txt")
SOURCES_FILE = Path("sources.txt")
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


def load_sources():
    return [
        line.strip()
        for line in SOURCES_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main():
    # читаем домены
    domains = DOMAINS_FILE.read_text(encoding="utf-8").splitlines()
    regex = build_regex(domains)

    # читаем источники
    sources = load_sources()

    combined_text = []

    for url in sources:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        combined_text.append(response.text)

    full_hosts_text = "\n".join(combined_text)

    # ищем совпадения
    matches = regex.findall(full_hosts_text)

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
