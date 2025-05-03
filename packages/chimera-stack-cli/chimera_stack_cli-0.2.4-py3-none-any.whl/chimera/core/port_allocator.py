"""
Port allocation management for ChimeraStack CLI
"""
from typing import Dict, Optional, Set, Any
from dataclasses import dataclass
from pathlib import Path
import yaml

from .port_scanner import PortScanner


@dataclass
class PortRange:
    start: int
    end: int
    allocated: Set[int] = None

    def __post_init__(self):
        if self.allocated is None:
            self.allocated = set()


class PortAllocator:
    DEFAULT_CONFIG = Path(__file__).resolve(
    ).parent.parent / "config" / "ports.yaml"

    def __init__(self, config_path: str | Path | None = None):
        self.scanner = PortScanner()
        self.ranges = self._load_ranges(config_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_ranges(self, config_path: str | Path | None) -> Dict[str, Dict[str, "PortRange"]]:
        """Load port ranges from YAML; fall back to legacy hard-coded dict."""

        path = Path(config_path) if config_path else self.DEFAULT_CONFIG

        if path.exists():
            try:
                with open(path, "r") as f:
                    data: Dict[str, Any] = yaml.safe_load(f) or {}

                parsed: Dict[str, Dict[str, PortRange]] = {}
                for service_type, entries in data.items():
                    parsed[service_type] = {}
                    for name, rng in entries.items():
                        if isinstance(rng, str) and "-" in rng:
                            start, end = map(int, rng.split("-", 1))
                        elif isinstance(rng, (list, tuple)) and len(rng) == 2:
                            start, end = map(int, rng)
                        else:
                            # bad format – skip
                            continue
                        parsed[service_type][name] = PortRange(start, end)

                if parsed:
                    return parsed
            except Exception:
                # Fall back to legacy dict below
                pass

        # Legacy hard-coded ranges (kept for backward compatibility)
        return {
            'frontend': {
                'react': PortRange(3000, 3999),
                'vue': PortRange(4000, 4999)
            },
            'backend': {
                'php': PortRange(8000, 8999),
                'node': PortRange(9000, 9999)
            },
            'database': {
                'mysql': PortRange(3300, 3399),
                'mariadb': PortRange(3400, 3499),
                'postgres': PortRange(5432, 5632)
            },
            'admin': {
                'phpmyadmin': PortRange(8081, 8180),
                'pgadmin': PortRange(8181, 8280)
            }
        }

    def get_available_port(self, service_type: str, service_name: str) -> Optional[int]:
        if service_type not in self.ranges:
            return None

        ranges = self.ranges[service_type]
        used_ports = self.scanner.scan()['ports']

        # Find specific range for service
        port_range = None
        for key, range_obj in ranges.items():
            if key in service_name.lower():
                port_range = range_obj
                break

        if port_range is None:
            port_range = next(iter(ranges.values()))

        # Find first available port in range
        for port in range(port_range.start, port_range.end + 1):
            if port not in used_ports:
                return port

        return None

    def release_port(self, port: int) -> None:
        for ranges in self.ranges.values():
            for port_range in ranges.values():
                if port_range.start <= port <= port_range.end:
                    port_range.allocated.discard(port)
                    return
