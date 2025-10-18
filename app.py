from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import csv
import io
from typing import List, Optional

DATABASE_URL = "sqlite:///./products.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI(title="Streamoid Product Uploader")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    color = Column(String)
    size = Column(String)
    mrp = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

REQUIRED_FIELDS = ["sku", "name", "brand", "mrp", "price"]

def validate_row(row: dict):
    errors = []
    # required
    for f in REQUIRED_FIELDS:
        if not row.get(f) or row.get(f).strip() == "":
            errors.append(f"missing {f}")
    # numeric conversions
    try:
        mrp = float(row.get("mrp") or 0)
    except Exception:
        errors.append("invalid mrp")
        mrp = None
    try:
        price = float(row.get("price") or 0)
    except Exception:
        errors.append("invalid price")
        price = None
    try:
        qty = int(row.get("quantity") or 0)
    except Exception:
        errors.append("invalid quantity")
        qty = None
    # business rules
    if mrp is not None and price is not None:
        if price > mrp:
            errors.append("price must be <= mrp")
    if qty is not None:
        if qty < 0:
            errors.append("quantity must be >= 0")
    return errors

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    stored = 0
    failed = []
    session = SessionLocal()
    line_no = 1
    for row in reader:
        line_no += 1
        # strip values
        row = {k.strip(): (v.strip() if v is not None else "") for k, v in row.items()}
        errors = validate_row(row)
        if errors:
            failed.append({"line": line_no, "sku": row.get("sku"), "errors": errors})
            continue
        # duplicate sku
        existing = session.query(Product).filter_by(sku=row.get("sku")).first()
        if existing:
            # update
            existing.name = row.get("name")
            existing.brand = row.get("brand")
            existing.color = row.get("color")
            existing.size = row.get("size")
            existing.mrp = float(row.get("mrp"))
            existing.price = float(row.get("price"))
            existing.quantity = int(row.get("quantity") or 0)
            session.add(existing)
            stored += 1
            continue
        prod = Product(
            sku=row.get("sku"),
            name=row.get("name"),
            brand=row.get("brand"),
            color=row.get("color"),
            size=row.get("size"),
            mrp=float(row.get("mrp")),
            price=float(row.get("price")),
            quantity=int(row.get("quantity") or 0)
        )
        session.add(prod)
        try:
            session.commit()
            stored += 1
        except Exception as e:
            session.rollback()
            failed.append({"line": line_no, "sku": row.get("sku"), "errors": ["db error", str(e)]})
    session.close()
    return JSONResponse({"stored": stored, "failed": failed})

@app.get("/products")
def list_products(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    session = SessionLocal()
    offset = (page - 1) * limit
    q = session.query(Product).offset(offset).limit(limit).all()
    total = session.query(Product).count()
    results = [
        {
            "sku": p.sku,
            "name": p.name,
            "brand": p.brand,
            "color": p.color,
            "size": p.size,
            "mrp": p.mrp,
            "price": p.price,
            "quantity": p.quantity
        }
        for p in q
    ]
    session.close()
    return {"page": page, "limit": limit, "total": total, "items": results}

@app.get("/products/search")
def search_products(
    brand: Optional[str] = None,
    color: Optional[str] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    session = SessionLocal()
    q = session.query(Product)
    if brand:
        q = q.filter(Product.brand == brand)
    if color:
        q = q.filter(Product.color == color)
    if minPrice is not None:
        q = q.filter(Product.price >= minPrice)
    if maxPrice is not None:
        q = q.filter(Product.price <= maxPrice)
    total = q.count()
    offset = (page - 1) * limit
    items = q.offset(offset).limit(limit).all()
    results = [
        {
            "sku": p.sku,
            "name": p.name,
            "brand": p.brand,
            "color": p.color,
            "size": p.size,
            "mrp": p.mrp,
            "price": p.price,
            "quantity": p.quantity
        }
        for p in items
    ]
    session.close()
    return {"page": page, "limit": limit, "total": total, "items": results}


from fastapi import FastAPI, UploadFile, File, HTTPException, Query
return JSONResponse({"stored": stored, "failed": failed})

