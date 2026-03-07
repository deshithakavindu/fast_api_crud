from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.database import session, engine
from app import database_models
from app.models import Product

app = FastAPI(
    title="Product API",
    description="FastAPI CRUD API with PostgreSQL",
    version="1.0.0"
)

database_models.Base.metadata.create_all(bind=engine)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample products
sample_products = [
    Product(id=1, name="Phone", description="A smartphone", price=699.99, quantity=50),
    Product(id=2, name="Laptop", description="Powerful laptop", price=999.99, quantity=30),
    Product(id=3, name="Pen", description="Blue ink pen", price=1.99, quantity=100),
    Product(id=4, name="Table", description="Wooden table", price=199.99, quantity=20),
]


# Database dependency
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


# Initialize database on startup
@app.on_event("startup")
def init_db():
    db = session()
    existing_count = db.query(database_models.Product).count()

    if existing_count == 0:
        for product in sample_products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()
        print("Database initialized with sample data")

    db.close()


@app.get("/")
def root():
    return {"message": "Welcome to Product API 🚀"}


# Get all products
@app.get("/products/", response_model=List[Product])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()


# Get single product
@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(database_models.Product).filter(
        database_models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


# Create product
@app.post("/products/", status_code=status.HTTP_201_CREATED)
def create_product(product: Product, db: Session = Depends(get_db)):
    new_product = database_models.Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product created successfully",
        "product": new_product
    }


# Update product
@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product, db: Session = Depends(get_db)):

    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == product_id
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    for key, value in product.model_dump().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    return {
        "message": "Product updated successfully",
        "product": db_product
    }


# Delete product
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):

    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == product_id
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(db_product)
    db.commit()

    return {"message": "Product deleted successfully"}