import logging
import socket
from typing import List, Dict, Optional

import dns.query
import dns.resolver
import dns.zone
import geoip2.database

from constants import SOCKET_TIMEOUT

logger = logging.getLogger(__name__)


def get_NS_records(domain: str) -> List[Dict[str, str]]:
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        return [{"hostname": str(rdata.target)} for rdata in answers]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        logger.info(f"No NS records for {domain}")
        return []
    except Exception as e:
        logger.error(f"Error fetching NS records for {domain}: {e}")
        return []


def get_MX_records(domain: str) -> List[Dict[str, str]]:
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return [{"hostname": str(rdata.exchange), "preference": str(rdata.preference)} for rdata in answers]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        logger.info(f"No MX records for {domain}")
        return []
    except Exception as e:
        logger.error(f"Error fetching MX records for {domain}: {e}")
        return []


def get_A_records(domain: str) -> List[Dict[str, str]]:
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return [{"ip": str(rdata.address)} for rdata in answers]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        logger.info(f"No A records for {domain}")
        return []
    except Exception as e:
        logger.error(f"Error fetching A records for {domain}: {e}")
        return []


def get_SPF_record(domain: str) -> Optional[Dict[str, str]]:
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            txt = str(rdata).strip('"')
            if txt.startswith('v=spf1'):
                return {"spf": txt}
        return None
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        logger.info(f"No SPF records for {domain}")
        return None
    except Exception as e:
        logger.error(f"Error fetching SPF record for {domain}: {e}")
        return None


def get_PTR_record(ip: str) -> Optional[Dict[str, str]]:
    try:
        answers = dns.resolver.resolve(dns.reversename.from_address(ip), 'PTR')
        return {"hostname": str(answers[0].target)}
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        logger.info(f"No PTR record for {ip}")
        return None
    except Exception as e:
        logger.error(f"Error fetching PTR record for {ip}: {e}")
        return None


def check_zone_transfer(domain: str, ns_servers: List[Dict[str, str]]) -> List[Dict[str, str]]:
    results = []
    for ns in ns_servers:
        ns_hostname = ns["hostname"]
        try:
            socket.setdefaulttimeout(SOCKET_TIMEOUT)
            zone = dns.zone.from_xfr(dns.query.xfr(ns_hostname, domain))
            for name, rdata in zone.iterate_rdatas('A'):
                results.append({"hostname": str(name), "ip": str(rdata.address)})
        except (dns.exception.FormError, dns.query.TransferError, socket.timeout):
            logger.info(f"Zone transfer failed for {domain} on {ns_hostname}")
        except Exception as e:
            logger.error(f"Error checking zone transfer for {domain} on {ns_hostname}: {e}")
    return results


def get_geoip_info(ip: str) -> Optional[Dict[str, str]]:
    try:
        with geoip2.database.Reader('GeoLite2-Country.mmdb') as reader:
            response = reader.country(ip)
            return {"country": response.country.name or "Unknown"}
    except Exception as e:
        logger.error(f"Error fetching GeoIP for {ip}: {e}")
        return None
