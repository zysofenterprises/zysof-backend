# ============================================================
#  main.py — ZYSOF FastAPI Application
#  Run with:  uvicorn main:app --reload
#  Docs at:   http://localhost:8000/docs
# ============================================================

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from decimal import Decimal

from database import get_db, engine, Base
from models import Part, Customer, Supplier, Inventory, Quotation, QuotationItem, Invoice
from schemas import (
    PartCreate, PartUpdate, PartResponse, PartListResponse,
    CustomerCreate, CustomerUpdate, CustomerResponse,
    SupplierResponse,
    QuotationCreate, QuotationResponse,
    InvoiceResponse,
    InventoryResponse, InventoryUpdate,
    WebsiteProductResponse,
)

# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(
    title="ZYSOF Enterprises ERP API",
    description="""
## ZYSOF Enterprises — Internal ERP System

This API powers the ZYSOF ERP system for managing:
- **Parts & Products** — spare parts catalogue
- **Customers & Suppliers** — business contacts
- **Quotations & Invoices** — sales documents
- **Inventory** — stock tracking
- **Website** — product catalogue (no prices exposed publicly)

> All prices are internal only. The website module never exposes cost or selling prices.
    """,
    version="1.0.0",
    contact={"name": "ZYSOF Development Team"},
)

# Allow frontend (React/etc) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/", tags=["System"])
def root():
    return {
        "system": "ZYSOF Enterprises ERP API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Check if the API and database are connected and working."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================
# PARTS
# ============================================================

@app.get("/api/parts", response_model=list[PartListResponse], tags=["Parts"])
def list_parts(
    active_only: bool = True,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List all parts. Filter by active status or category."""
    query = db.query(Part)
    if active_only:
        query = query.filter(Part.is_active == True)
    if category_id:
        query = query.filter(Part.category_id == category_id)
    return query.order_by(Part.part_number).all()


@app.get("/api/parts/{part_id}", response_model=PartResponse, tags=["Parts"])
def get_part(part_id: int, db: Session = Depends(get_db)):
    """Get a single part by ID."""
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail=f"Part {part_id} not found")
    return part


@app.post("/api/parts", response_model=PartResponse, status_code=201, tags=["Parts"])
def create_part(data: PartCreate, db: Session = Depends(get_db)):
    """Create a new part."""
    existing = db.query(Part).filter(Part.part_number == data.part_number).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Part number '{data.part_number}' already exists")
    part = Part(**data.model_dump())
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


@app.patch("/api/parts/{part_id}", response_model=PartResponse, tags=["Parts"])
def update_part(part_id: int, data: PartUpdate, db: Session = Depends(get_db)):
    """Update a part. Only send the fields you want to change."""
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail=f"Part {part_id} not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(part, field, value)
    db.commit()
    db.refresh(part)
    return part


@app.delete("/api/parts/{part_id}", tags=["Parts"])
def deactivate_part(part_id: int, db: Session = Depends(get_db)):
    """Deactivate a part (soft delete — data is preserved)."""
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail=f"Part {part_id} not found")
    part.is_active = False
    db.commit()
    return {"message": f"Part {part_id} deactivated successfully"}


# ============================================================
# CUSTOMERS
# ============================================================

@app.get("/api/customers", response_model=list[CustomerResponse], tags=["Customers"])
def list_customers(active_only: bool = True, db: Session = Depends(get_db)):
    """List all customers."""
    query = db.query(Customer)
    if active_only:
        query = query.filter(Customer.is_active == True)
    return query.order_by(Customer.company_name).all()


@app.get("/api/customers/{customer_id}", response_model=CustomerResponse, tags=["Customers"])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a single customer by ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer


@app.post("/api/customers", response_model=CustomerResponse, status_code=201, tags=["Customers"])
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer."""
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@app.patch("/api/customers/{customer_id}", response_model=CustomerResponse, tags=["Customers"])
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    """Update a customer."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


# ============================================================
# SUPPLIERS
# ============================================================

@app.get("/api/suppliers", response_model=list[SupplierResponse], tags=["Suppliers"])
def list_suppliers(active_only: bool = True, db: Session = Depends(get_db)):
    """List all suppliers."""
    query = db.query(Supplier)
    if active_only:
        query = query.filter(Supplier.is_active == True)
    return query.order_by(Supplier.company_name).all()


@app.get("/api/suppliers/{supplier_id}", response_model=SupplierResponse, tags=["Suppliers"])
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Get a single supplier by ID."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Supplier {supplier_id} not found")
    return supplier


# ============================================================
# INVENTORY
# ============================================================

@app.get("/api/inventory", response_model=list[InventoryResponse], tags=["Inventory"])
def list_inventory(low_stock_only: bool = False, db: Session = Depends(get_db)):
    """
    List all inventory records.
    Set low_stock_only=true to see only parts below their minimum alert level.
    """
    query = db.query(Inventory)
    if low_stock_only:
        query = query.filter(Inventory.quantity <= Inventory.min_stock_alert)
    return query.all()


@app.get("/api/inventory/{part_id}", response_model=InventoryResponse, tags=["Inventory"])
def get_inventory_for_part(part_id: int, db: Session = Depends(get_db)):
    """Get the inventory record for a specific part."""
    inv = db.query(Inventory).filter(Inventory.part_id == part_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"No inventory record for part {part_id}")
    return inv


@app.patch("/api/inventory/{part_id}", response_model=InventoryResponse, tags=["Inventory"])
def update_inventory(part_id: int, data: InventoryUpdate, db: Session = Depends(get_db)):
    """Update stock quantity, alert level, or location for a part."""
    inv = db.query(Inventory).filter(Inventory.part_id == part_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"No inventory record for part {part_id}")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, field, value)
    db.commit()
    db.refresh(inv)
    return inv


# ============================================================
# QUOTATIONS
# ============================================================

@app.get("/api/quotations", response_model=list[QuotationResponse], tags=["Quotations"])
def list_quotations(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all quotations. Filter by customer or status."""
    query = db.query(Quotation)
    if customer_id:
        query = query.filter(Quotation.customer_id == customer_id)
    if status:
        query = query.filter(Quotation.status == status)
    return query.order_by(Quotation.created_at.desc()).all()


@app.get("/api/quotations/{quotation_id}", response_model=QuotationResponse, tags=["Quotations"])
def get_quotation(quotation_id: int, db: Session = Depends(get_db)):
    """Get a single quotation with all its line items."""
    q = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not q:
        raise HTTPException(status_code=404, detail=f"Quotation {quotation_id} not found")
    return q


# ============================================================
# INVOICES
# ============================================================

@app.get("/api/invoices", response_model=list[InvoiceResponse], tags=["Invoices"])
def list_invoices(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all invoices. Filter by customer or payment status."""
    query = db.query(Invoice)
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    if status:
        query = query.filter(Invoice.status == status)
    return query.order_by(Invoice.issue_date.desc()).all()


@app.get("/api/invoices/{invoice_id}", response_model=InvoiceResponse, tags=["Invoices"])
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get a single invoice by ID."""
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    return inv


# ============================================================
# WEBSITE CATALOGUE  (no prices)
# ============================================================

@app.get("/api/website/products", response_model=list[WebsiteProductResponse], tags=["Website"])
def list_website_products(
    featured_only: bool = False,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Public product catalogue. No prices are returned — ZYSOF is quotation-based.
    Customers submit inquiries and receive custom quotes.
    """
    from models import WebsiteProduct
    query = db.query(WebsiteProduct)
    if featured_only:
        query = query.filter(WebsiteProduct.is_featured == True)
    if category_id:
        query = query.filter(WebsiteProduct.website_category_id == category_id)
    return query.order_by(WebsiteProduct.sort_order).all()
