from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..schemas import UploadResponse
from ..services import ingest

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse, dependencies=[Depends(require_admin)])
async def upload_file(
    file: UploadFile = File(...),
    type: str = Form("table"),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
    data = await file.read()
    try:
        if type == "doc":
            result = ingest.ingest_doc(db, data, file.filename or "doc", description)
        else:
            result = ingest.ingest_table(db, data, file.filename or "table.csv", description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据入库失败: {e}")
    return result
