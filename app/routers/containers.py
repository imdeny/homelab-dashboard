from fastapi import APIRouter, HTTPException
import docker

router = APIRouter()


def _get_client():
    try:
        return docker.from_env()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Docker unavailable: {e}")


@router.get("")
def get_containers():
    client = _get_client()
    result = []
    for c in client.containers.list(all=True):
        tags = c.image.tags
        result.append({
            "id": c.short_id,
            "name": c.name,
            "image": tags[0] if tags else c.image.short_id,
            "status": c.status,
            "running": c.status == "running",
        })
    result.sort(key=lambda x: (not x["running"], x["name"]))
    return result
