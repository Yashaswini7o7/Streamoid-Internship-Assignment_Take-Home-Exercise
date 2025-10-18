from fastapi import FastAPI, UploadFile, File, HTTPException, Query
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
