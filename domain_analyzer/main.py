from typing import List, Dict, Set, Any, Optional
import argparse
import logging
import socket
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore
from dns_utils import get_NS_records, get_MX_records, get_A_records, get_SPF_record, get_PTR_record, \
    check_zone_transfer, get_geoip_info
from nmap_utils import check_active_host, scan_host, run_zenmap
from robtex_utils import find_robtex_domains
from output_utils import save_json
from constants import DEFAULT_MAX_CRAWL, COMMON_HOSTNAMES, GTLD_DOMAINS, TLD_DOMAINS, CC_DOMAINS, DEFAULT_NMAP_SCANTYPE

# TODO: Add SSL/TLS check with Shodan API for future implementation

logger = logging.getLogger(__name__)


class DomainAnalyzer:
    def __init__(self, args: argparse.Namespace):
        self.domain = args.domain
        self.output_file = args.output or f"{self.domain}.json"
        self.max_crawl = args.max_amount_to_crawl
        self.download_files = args.download_files
        self.ignore_pattern = args.ignore_host_pattern
        self.nmap_scantype = args.nmap_scantype
        self.no_subdomains = args.not_subdomains
        self.no_zone_transfer = args.not_zone_transfer
        self.no_net_block = args.not_net_block
        self.use_zenmap = args.zenmap
        self.robtex = args.robtex_domains
        self.all_robtex = args.all_robtex
        self.world_domination = args.world_domination
        self.domain_data: Dict[str, Any] = {
            "domain": self.domain,
            "ips": [],
            "domain_info": {"subdomains": [], "emails": []}
        }
        init(autoreset=True)

    async def analyze_domain(self) -> None:
        logger.info(f"{Fore.CYAN}Starting analysis for {self.domain}")
        ns_records = get_NS_records(self.domain)
        mx_records = get_MX_records(self.domain)
        a_records = get_A_records(self.domain)
        spf_record = get_SPF_record(self.domain)

        ip_set: Set[str] = {record["ip"] for record in a_records}
        subdomains: List[str] = [self.domain]

        if not self.no_subdomains:
            subdomains.extend(await self._find_subdomains())

        for subdomain in subdomains:
            self.domain_data["domain_info"]["subdomains"].append(subdomain)
            subdomain_a_records = get_A_records(subdomain)
            ip_set.update(record["ip"] for record in subdomain_a_records)

        if not self.no_zone_transfer:
            zone_transfer_records = check_zone_transfer(self.domain, ns_records)
            ip_set.update(record["ip"] for record in zone_transfer_records)

        with ThreadPoolExecutor() as executor:
            active_ips = [ip for ip in ip_set if executor.submit(check_active_host, ip).result()]

        for ip in active_ips:
            ip_info = self._collect_ip_info(ip, ns_records, mx_records, spf_record)
            self.domain_data["ips"].append(ip_info)

        if self.robtex or self.all_robtex:
            related_domains = find_robtex_domains(self.domain, ns_records, self.all_robtex)
            self.domain_data["domain_info"]["related_domains"] = list(related_domains)

        if self.world_domination:
            await self._world_domination_check()

        if self.use_zenmap:
            run_zenmap(self.domain)

        save_json(self.domain_data, self.output_file)
        logger.info(f"{Fore.GREEN}Analysis complete for {self.domain}")

    async def _find_subdomains(self) -> List[str]:
        subdomains = []
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._check_subdomain(session, f"{hostname}.{self.domain}")
                for hostname in COMMON_HOSTNAMES
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            subdomains.extend([result for result in results if isinstance(result, str)])
        return subdomains

    async def _check_subdomain(self, session: aiohttp.ClientSession, subdomain: str) -> Optional[str]:
        try:
            async with session.get(f"http://{subdomain}", timeout=5) as response:
                if response.status == 200:
                    return subdomain
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass
        return None

    def _collect_ip_info(self, ip: str, ns_records: List[Dict[str, str]], mx_records: List[Dict[str, str]],
                         spf_record: Optional[Dict[str, str]]) -> Dict[str, Any]:
        info = {"ip": ip, "info": []}

        for record in get_A_records(self.domain) + get_A_records(f"www.{self.domain}"):
            if record["ip"] == ip:
                info["info"].append({"hostname": self.domain, "type": "A"})

        geoip = get_geoip_info(ip)
        if geoip:
            info["info"].append(geoip)

        ptr = get_PTR_record(ip)
        if ptr:
            info["info"].append(ptr)

        ports = scan_host(ip, self.domain, self.nmap_scantype)
        if ports:
            info["info"].append({"ports": [f"{p['port']} {p['service']}" for p in ports]})

        # Placeholder for crawler integration
        if not self.no_net_block:
            info["info"].append({"crawler": {"links": [], "files": [], "directories": [], "emails": [], "externals": [],
                                             "directories_with_indexing": []}})

        return info

    async def _world_domination_check(self) -> None:
        tlds = GTLD_DOMAINS + TLD_DOMAINS + list(CC_DOMAINS)
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._check_tld_domain(session, tld)
                for tld in tlds if not self.ignore_pattern or tld not in self.ignore_pattern
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.domain_data["domain_info"]["tld_domains"] = [r for r in results if isinstance(r, str)]

    async def _check_tld_domain(self, session: aiohttp.ClientSession, tld: str) -> Optional[str]:
        test_domain = f"{self.domain.split('.')[0]}.{tld.lstrip('.')}"
        try:
            socket.gethostbyname(test_domain)
            return test_domain
        except socket.gaierror:
            return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Domain analysis tool")
    parser.add_argument("-d", "--domain", required=True, help="Domain to analyze")
    parser.add_argument("-o", "--output", help="Output JSON file")
    parser.add_argument("--max-amount-to-crawl", type=int, default=DEFAULT_MAX_CRAWL, help="Max URLs to crawl")
    parser.add_argument("--download-files", action="store_true", help="Download files during crawling")
    parser.add_argument("--ignore-host-pattern", help="Pattern to ignore hosts")
    parser.add_argument("--nmap-scantype", default=DEFAULT_NMAP_SCANTYPE, help="Nmap scan type")
    parser.add_argument("--not-subdomains", action="store_true", help="Skip subdomain analysis")
    parser.add_argument("--not-zone-transfer", action="store_true", help="Skip zone transfer check")
    parser.add_argument("--not-net-block", action="store_true", help="Skip network block analysis")
    parser.add_argument("--zenmap", action="store_true", help="Launch Zenmap for nmap results")
    parser.add_argument("--robtex-domains", action="store_true", help="Check Robtex for related domains")
    parser.add_argument("--all-robtex", action="store_true", help="Check all Robtex domains")
    parser.add_argument("--world-domination", action="store_true", help="Check TLDs for domain")
    return parser.parse_args()


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=f"{Fore.BLUE}%(asctime)s{Fore.RESET} [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


async def main():
    setup_logging()
    args = parse_args()
    analyzer = DomainAnalyzer(args)
    await analyzer.analyze_domain()


if __name__ == "__main__":
    asyncio.run(main())