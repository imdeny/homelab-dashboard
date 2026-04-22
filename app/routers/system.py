from fastapi import APIRouter
import psutil, time

router = APIRouter()


def _read_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read().strip()) / 1000, 1)
    except OSError:
        return None


@router.get("")
def get_system_stats():
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime_seconds = int(time.time() - psutil.boot_time())

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "ram": {
            "total_mb": round(vm.total / 1024 / 1024),
            "used_mb": round(vm.used / 1024 / 1024),
            "percent": vm.percent,
        },
        "disk": {
            "total_gb": round(disk.total / 1024 / 1024 / 1024, 1),
            "used_gb": round(disk.used / 1024 / 1024 / 1024, 1),
            "percent": disk.percent,
        },
        "temperature_c": _read_temp(),
        "uptime_seconds": uptime_seconds,
    }
