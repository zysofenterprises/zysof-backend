# ============================================================
#  schemas.py — Pydantic schemas
#  These define what data goes IN (request) and OUT (response)
#  for each API endpoint. Separate from ORM models.
# ============================================================

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from models import (
    QuotationStatusEnum, InvoiceStatusEnum, RFQStatusEnum,
    POStatusEnum, PurchaseTypeEnum, DeliveryStatusEnum,
    ReturnTypeEnum, ReturnStatusEnum, ReturnReasonEnum
)


# ============================================================
# SHARED BASE
# ============================================================

class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# PARTS
# ============================================================

class PartBase(OrmBase):
    part_number:     str
    description:     str
    category_id:     Optional[int]   = None
    supplier_id:     Optional[int]   = None
    unit:            Optional[str]   = "pcs"
    cost_price:      Decimal         = Decimal("0")
    selling_price:   Decimal         = Decimal("0")
    image_url:       Optional[str]   = None
    is_active:       bool            = True
    show_on_website: bool            = False

class PartCreate(PartBase):
    pass

class PartUpdate(OrmBase):
    description:     Optional[str]     = None
    category_id:     Optional[int]     = None
    supplier_id:     Optional[int]     = None
    unit:            Optional[str]     = None
    cost_price:      Optional[Decimal] = None
    selling_price:   Optional[Decimal] = None
    image_url:       Optional[str]     = None
    is_active:       Optional[bool]    = None
    show_on_website: Optional[bool]    = None

class PartResponse(PartBase):
    id:         int
    created_at: datetime
    updated_at: datetime

class PartListResponse(OrmBase):
    id:          int
    part_number: str
    description: str
    unit:        Optional[str]
    is_active:   bool
    category_id: Optional[int]


# ============================================================
# CUSTOMERS
# ============================================================

class CustomerBase(OrmBase):
    company_name:   str
    contact_person: Optional[str] = None
    email:          Optional[str] = None
    phone:          Optional[str] = None
    city:           Optional[str] = None
    country:        Optional[str] = "Saudi Arabia"
    address:        Optional[str] = None
    vat_number:     Optional[str] = None
    payment_terms:  Optional[str] = None
    notes:          Optional[str] = None
    is_active:      bool          = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(OrmBase):
    company_name:   Optional[str]  = None
    contact_person: Optional[str]  = None
    email:          Optional[str]  = None
    phone:          Optional[str]  = None
    city:           Optional[str]  = None
    country:        Optional[str]  = None
    address:        Optional[str]  = None
    vat_number:     Optional[str]  = None
    payment_terms:  Optional[str]  = None
    notes:          Optional[str]  = None
    is_active:      Optional[bool] = None

class CustomerResponse(CustomerBase):
    id:         int
    created_at: datetime
    updated_at: datetime


# ============================================================
# QUOTATIONS
# ============================================================

class QuotationItemCreate(OrmBase):
    part_id:     Optional[int]     = None
    part_number: Optional[str]     = None
    description: str
    quantity:    Decimal
    unit:        Optional[str]     = None
    cost_price:  Decimal           = Decimal("0")
    unit_price:  Decimal
    sort_order:  int               = 0

class QuotationItemResponse(QuotationItemCreate):
    id:          int
    total_price: Decimal

class QuotationCreate(OrmBase):
    customer_id:    int
    valid_until:    Optional[date]  = None
    payment_terms:  Optional[str]   = None
    delivery_terms: Optional[str]   = None
    city:           Optional[str]   = None
    vat_rate:       Decimal         = Decimal("15.00")
    notes:          Optional[str]   = None
    items:          list[QuotationItemCreate] = []

class QuotationResponse(OrmBase):
    id:               int
    quotation_number: str
    customer_id:      int
    created_by:       int
    issue_date:       date
    valid_until:      Optional[date]
    payment_terms:    Optional[str]
    delivery_terms:   Optional[str]
    city:             Optional[str]
    status:           QuotationStatusEnum
    subtotal:         Decimal
    vat_rate:         Decimal
    vat_amount:       Decimal
    total_amount:     Decimal
    notes:            Optional[str]
    items:            list[QuotationItemResponse] = []
    created_at:       datetime
    updated_at:       datetime


# ============================================================
# INVOICES
# ============================================================

class InvoiceResponse(OrmBase):
    id:             int
    invoice_number: str
    quotation_id:   Optional[int]
    customer_id:    int
    issue_date:     date
    due_date:       Optional[date]
    status:         InvoiceStatusEnum
    subtotal:       Decimal
    vat_rate:       Decimal
    vat_amount:     Decimal
    total_amount:   Decimal
    amount_paid:    Decimal
    notes:          Optional[str]
    created_at:     datetime


# ============================================================
# INVENTORY
# ============================================================

class InventoryResponse(OrmBase):
    id:              int
    part_id:         int
    quantity:        Decimal
    min_stock_alert: Decimal
    location:        Optional[str]
    last_updated:    datetime

class InventoryUpdate(OrmBase):
    quantity:        Optional[Decimal] = None
    min_stock_alert: Optional[Decimal] = None
    location:        Optional[str]     = None


# ============================================================
# WEBSITE PRODUCTS  (no prices exposed)
# ============================================================

class WebsiteProductResponse(OrmBase):
    id:                  int
    part_id:             int
    website_category_id: Optional[int]
    slug:                str
    title:               str
    description:         Optional[str]
    image_url:           Optional[str]
    is_featured:         bool
    sort_order:          int
    meta_title:          Optional[str]
    meta_description:    Optional[str]


# ============================================================
# SUPPLIERS
# ============================================================

class SupplierResponse(OrmBase):
    id:             int
    company_name:   str
    contact_person: Optional[str]
    email:          Optional[str]
    phone:          Optional[str]
    city:           Optional[str]
    country:        Optional[str]
    is_active:      bool
