import logging
import subprocess
from pathlib import Path
from typing import List, Dict

from constants import DEFAULT_NMAP_SCANTYPE, ZENMAP_COMMAND

logger = logging.getLogger(__name__)


def check_active_host(ip: str) -> bool:
    try:
        result = subprocess.run(
            ["ping", "-c", "2", "-W", "1", ip],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.info(f"Ping timeout for {ip}")
        return False
    except Exception as e:
        logger.error(f"Error pinging {ip}: {e}")
        return False


def scan_host(ip: str, domain: str, scantype: str = DEFAULT_NMAP_SCANTYPE) -> List[Dict[str, str]]:
    output_dir = Path(domain) / "nmap"
    output_dir.mkdir(parents=True, exist_ok=True)
    xml_output = output_dir / f"{ip}.xml"
    ports = []

    try:
        cmd = ["nmap"] + scantype.split() + ["-oX", str(xml_output), ip]
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        if xml_output.exists():
            with xml_output.open() as f:
                for line in f:
                    if "<port " in line and "state='open'" in line:
                        port_info = line.split("portid=")[1].split(" ")[0].strip('"')
                        protocol = line.split("protocol=")[1].split(" ")[0].strip('"')
                        service = line.split("service name=")[1].split(" ")[0].strip(
                            '"') if "service name=" in line else "unknown"
                        ports.append({"port": f"{port_info}/{protocol}", "service": service})
        return ports
    except subprocess.TimeoutExpired:
        logger.info(f"Nmap scan timeout for {ip}")
        return []
    except Exception as e:
        logger.error(f"Error scanning {ip}: {e}")
        return []


def run_zenmap(domain: str) -> bool:
    output_dir = Path(domain) / "nmap"
    try:
        if not output_dir.exists():
            logger.warning("No nmap output directory found")
            return False
        subprocess.run([ZENMAP_COMMAND, str(output_dir)], check=False, timeout=30)
        return True
    except FileNotFoundError:
        logger.warning("Zenmap not found, skipping")
        return False
    except subprocess.TimeoutExpired:
        logger.info("Zenmap launch timed out")
        return False
    except Exception as e:
        logger.error(f"Error launching Zenmap: {e}")
        return False
