import io
import csv
from fastapi.testclient import TestClient
from app import app, SessionLocal, Product, Base, engine

client = TestClient(app)

# setup fresh DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

SAMPLE_CSV = """sku,name,brand,color,size,mrp,price,quantity
TSHIRT-RED-001,Classic Cotton T-Shirt,StreamThreads,Red,M,799,499,20
BAD-PRICE,Bad Price,BrandX,Black,L,500,600,3
NO-SKU,,BrandY,Blue,S,999,899,5
"""

def test_upload_and_failures():
    files = {"file": ("test.csv", SAMPLE_CSV)}
    res = client.post("/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["stored"] == 1
    assert len(data["failed"]) == 2

def test_search_and_pagination():
    # upload
    payload = "sku,name,brand,color,size,mrp,price,quantity\n" + \
              "P1,Prod1,BrandA,Red,M,1000,800,5\n" + \
              "P2,Prod2,BrandA,Blue,L,1200,700,2\n"
    files = {"file": ("more.csv", payload)}
    client.post("/upload", files=files)
    res = client.get("/products/search?brand=BrandA&minPrice=600&maxPrice=900")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
