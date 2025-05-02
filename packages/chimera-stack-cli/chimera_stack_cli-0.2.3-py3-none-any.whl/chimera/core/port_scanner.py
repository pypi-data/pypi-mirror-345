"""
Docker port and network scanner for ChimeraStack CLI
"""
import docker
from typing import Dict, Set, List

class PortScanner:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.used_ports: Set[int] = set()
        self.container_names: Set[str] = set()

    def scan(self) -> Dict[str, Set]:
        self.used_ports.clear()
        self.container_names.clear()

        containers = self.docker_client.containers.list(all=True)
        for container in containers:
            config = container.attrs
            ports = config['NetworkSettings']['Ports'] or {}
            bindings = config['HostConfig']['PortBindings'] or {}

            for ports_map in [ports, bindings]:
                for binding in ports_map.values():
                    if binding and binding[0].get('HostPort'):
                        self.used_ports.add(int(binding[0]['HostPort']))

            self.container_names.add(container.name)

        return {
            'ports': self.used_ports,
            'names': self.container_names
        }

    def is_port_used(self, port: int) -> bool:
        return port in self.used_ports

    def get_project_containers(self, project_prefix: str) -> List[str]:
        return [name for name in self.container_names
                if name.startswith(project_prefix)]
