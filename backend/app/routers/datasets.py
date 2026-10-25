from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Dataset
from ..schemas import DatasetListResponse, DatasetOut

router = APIRouter(prefix="/api", tags=["datasets"])


@router.get("/datasets", response_model=DatasetListResponse, dependencies=[Depends(get_current_user)])
def list_datasets(db: Session = Depends(get_db)):
    items = db.query(Dataset).filter(Dataset.status == "ready").order_by(Dataset.id.desc()).all()
    return {"datasets": [DatasetOut.model_validate(d) for d in items], "total": len(items)}


@router.get("/datasets/{dataset_id}/data", dependencies=[Depends(get_current_user)])
def get_table_data(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.type == "table").first()
    if not dataset or not dataset.table_name:
        raise HTTPException(status_code=404, detail="数据集不存在")
    result = db.execute(text(f"SELECT * FROM `{dataset.table_name}`"))
    columns = list(result.keys())
    rows = [list(row) for row in result.fetchall()]
    return {"columns": columns, "rows": rows}
