import logging
from typing import List, Dict, Set
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)


def find_robtex_domains(domain: str, ns_servers: List[Dict[str, str]], all_robtex: bool = False) -> Set[str]:
    related_domains = set()
    base_url = "https://www.robtex.com/dns-lookup/"

    for ns in ns_servers:
        ns_hostname = ns["hostname"]
        try:
            query = urlencode({"q": ns_hostname})
            url = f"{base_url}?{query}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            if all_robtex:
                lines = response.text.splitlines()
                for line in lines:
                    if 'href="/dns-lookup/' in line:
                        related_domain = line.split('href="/dns-lookup/')[1].split('"')[0]
                        if related_domain.endswith(domain):
                            related_domains.add(related_domain)
            else:
                if ns_hostname in response.text:
                    related_domains.add(ns_hostname)

        except requests.RequestException as e:
            logger.error(f"Error fetching Robtex data for {ns_hostname}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing Robtex for {ns_hostname}: {e}")

    return related_domains
