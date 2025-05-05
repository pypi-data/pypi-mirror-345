import asyncio
import json
from typing import Dict, Any
import psutil # type: ignore
import platform
import os
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.system_info = {}
        self.log_file = "system_monitor.log"

    async def get_system_info(self) -> Dict[str, Any]:
        """Recopila información del sistema."""
        return {
            'timestamp': datetime.now().isoformat(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free
            }
        }

    async def monitor_system(self):
        """Monitorea y registra información del sistema."""
        while True:
            try:
                system_info = await self.get_system_info()
                self._log_info(system_info)
                print(f"CPU: {system_info['cpu_percent']}% | "
                      f"RAM: {system_info['memory']['percent']}% | "
                      f"Timestamp: {system_info['timestamp']}")
                await asyncio.sleep(5)  # Actualizar cada 5 segundos
            except Exception as e:
                print(f"Error monitoreando sistema: {e}")
                await asyncio.sleep(1)

    def _log_info(self, info: Dict[str, Any]):
        """Guarda la información en un archivo de log."""
        with open(self.log_file, 'a') as f:
            f.write(f"{json.dumps(info)}\n")

async def main():
    monitor = SystemMonitor()
    print("Iniciando monitoreo del sistema...")
    try:
        await monitor.monitor_system()
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario")
    except Exception as e:
        print(f"Error en el monitoreo: {e}")

if __name__ == "__main__":
    asyncio.run(main())