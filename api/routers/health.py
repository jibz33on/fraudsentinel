from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "agents": {
            "detector":     "online",
            "investigator": "online",
            "decision":     "online",
        },
    }
