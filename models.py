# ============================================================
#  models.py — SQLAlchemy ORM models
#  Mirrors the zysof_schema.sql exactly.
#  Each class = one table. Relationships defined at the bottom.
# ============================================================

import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, ForeignKey, Integer,
    Numeric, String, Text, BigInteger, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


# ============================================================
# ENUM TYPES  (mirror the PostgreSQL ENUMs)
# ============================================================

class QuotationStatusEnum(str, enum.Enum):
    draft     = "draft"
    sent      = "sent"
    approved  = "approved"
    rejected  = "rejected"
    converted = "converted"
    expired   = "expired"

class InvoiceStatusEnum(str, enum.Enum):
    unpaid    = "unpaid"
    partial   = "partial"
    paid      = "paid"
    cancelled = "cancelled"

class RFQStatusEnum(str, enum.Enum):
    new       = "new"
    in_review = "in_review"
    quoted    = "quoted"
    closed    = "closed"

class POStatusEnum(str, enum.Enum):
    draft     = "draft"
    sent      = "sent"
    partial   = "partial"
    received  = "received"
    cancelled = "cancelled"

class PurchaseTypeEnum(str, enum.Enum):
    cash          = "cash"
    credit        = "credit"
    international = "international"

class DeliveryStatusEnum(str, enum.Enum):
    pending    = "pending"
    dispatched = "dispatched"
    in_transit = "in_transit"
    delivered  = "delivered"
    failed     = "failed"
    returned   = "returned"

class ReturnTypeEnum(str, enum.Enum):
    customer_return = "customer_return"
    supplier_return = "supplier_return"

class ReturnStatusEnum(str, enum.Enum):
    requested = "requested"
    approved  = "approved"
    rejected  = "rejected"
    received  = "received"
    refunded  = "refunded"
    exchanged = "exchanged"
    closed    = "closed"

class ReturnReasonEnum(str, enum.Enum):
    damaged          = "damaged"
    wrong_item       = "wrong_item"
    excess_quantity  = "excess_quantity"
    quality_issue    = "quality_issue"
    other            = "other"


# ============================================================
# 1. AUTH & USERS
# ============================================================

class Role(Base):
    __tablename__ = "roles"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    name:        Mapped[str]           = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True)
    full_name:     Mapped[str]           = mapped_column(String(100), nullable=False)
    email:         Mapped[str]           = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str]           = mapped_column(String(255), nullable=False)
    role_id:       Mapped[int]           = mapped_column(ForeignKey("roles.id"), nullable=False)
    is_active:     Mapped[bool]          = mapped_column(Boolean, default=True)
    created_at:    Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:    Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role:            Mapped["Role"]               = relationship("Role", back_populates="users")
    quotations:      Mapped[list["Quotation"]]    = relationship("Quotation", back_populates="creator", foreign_keys="Quotation.created_by")
    invoices:        Mapped[list["Invoice"]]      = relationship("Invoice", back_populates="creator", foreign_keys="Invoice.created_by")
    purchase_orders: Mapped[list["PurchaseOrder"]]= relationship("PurchaseOrder", back_populates="creator")
    stock_movements: Mapped[list["StockMovement"]]= relationship("StockMovement", back_populates="creator")


# ============================================================
# 2. CUSTOMERS
# ============================================================

class Customer(Base):
    __tablename__ = "customers"

    id:             Mapped[int]           = mapped_column(Integer, primary_key=True)
    company_name:   Mapped[str]           = mapped_column(String(150), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    email:          Mapped[Optional[str]] = mapped_column(String(150))
    phone:          Mapped[Optional[str]] = mapped_column(String(30))
    city:           Mapped[Optional[str]] = mapped_column(String(100))
    country:        Mapped[Optional[str]] = mapped_column(String(100), default="Saudi Arabia")
    address:        Mapped[Optional[str]] = mapped_column(Text)
    vat_number:     Mapped[Optional[str]] = mapped_column(String(50))
    payment_terms:  Mapped[Optional[str]] = mapped_column(String(100))
    notes:          Mapped[Optional[str]] = mapped_column(Text)
    is_active:      Mapped[bool]          = mapped_column(Boolean, default=True)
    created_at:     Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:     Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    quotations:  Mapped[list["Quotation"]]  = relationship("Quotation", back_populates="customer")
    invoices:    Mapped[list["Invoice"]]    = relationship("Invoice", back_populates="customer")
    rfqs:        Mapped[list["RFQ"]]        = relationship("RFQ", back_populates="customer")
    deliveries:  Mapped[list["Delivery"]]   = relationship("Delivery", back_populates="customer")
    returns:     Mapped[list["Return"]]     = relationship("Return", back_populates="customer", foreign_keys="Return.customer_id")


# ============================================================
# 3. SUPPLIERS
# ============================================================

class Supplier(Base):
    __tablename__ = "suppliers"

    id:             Mapped[int]           = mapped_column(Integer, primary_key=True)
    company_name:   Mapped[str]           = mapped_column(String(150), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    email:          Mapped[Optional[str]] = mapped_column(String(150))
    phone:          Mapped[Optional[str]] = mapped_column(String(30))
    city:           Mapped[Optional[str]] = mapped_column(String(100))
    country:        Mapped[Optional[str]] = mapped_column(String(100))
    address:        Mapped[Optional[str]] = mapped_column(Text)
    vat_number:     Mapped[Optional[str]] = mapped_column(String(50))
    payment_terms:  Mapped[Optional[str]] = mapped_column(String(100))
    notes:          Mapped[Optional[str]] = mapped_column(Text)
    is_active:      Mapped[bool]          = mapped_column(Boolean, default=True)
    created_at:     Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:     Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    parts:           Mapped[list["Part"]]          = relationship("Part", back_populates="supplier")
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="supplier")
    returns:         Mapped[list["Return"]]         = relationship("Return", back_populates="supplier", foreign_keys="Return.supplier_id")


# ============================================================
# 4. PARTS / PRODUCTS
# ============================================================

class Category(Base):
    __tablename__ = "categories"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    name:        Mapped[str]           = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    parts: Mapped[list["Part"]] = relationship("Part", back_populates="category")


class Part(Base):
    __tablename__ = "parts"

    id:              Mapped[int]            = mapped_column(Integer, primary_key=True)
    part_number:     Mapped[str]            = mapped_column(String(100), unique=True, nullable=False)
    description:     Mapped[str]            = mapped_column(Text, nullable=False)
    category_id:     Mapped[Optional[int]]  = mapped_column(ForeignKey("categories.id"))
    supplier_id:     Mapped[Optional[int]]  = mapped_column(ForeignKey("suppliers.id"))
    unit:            Mapped[Optional[str]]  = mapped_column(String(20), default="pcs")
    cost_price:      Mapped[Decimal]        = mapped_column(Numeric(12, 2), default=0)
    selling_price:   Mapped[Decimal]        = mapped_column(Numeric(12, 2), default=0)
    image_url:       Mapped[Optional[str]]  = mapped_column(Text)
    is_active:       Mapped[bool]           = mapped_column(Boolean, default=True)
    show_on_website: Mapped[bool]           = mapped_column(Boolean, default=False)
    created_at:      Mapped[datetime]       = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:      Mapped[datetime]       = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category:         Mapped[Optional["Category"]]      = relationship("Category", back_populates="parts")
    supplier:         Mapped[Optional["Supplier"]]      = relationship("Supplier", back_populates="parts")
    inventory:        Mapped[Optional["Inventory"]]     = relationship("Inventory", back_populates="part", uselist=False)
    stock_movements:  Mapped[list["StockMovement"]]     = relationship("StockMovement", back_populates="part")
    quotation_items:  Mapped[list["QuotationItem"]]     = relationship("QuotationItem", back_populates="part")
    invoice_items:    Mapped[list["InvoiceItem"]]       = relationship("InvoiceItem", back_populates="part")
    website_product:  Mapped[Optional["WebsiteProduct"]]= relationship("WebsiteProduct", back_populates="part", uselist=False)


# ============================================================
# 5. INVENTORY
# ============================================================

class Inventory(Base):
    __tablename__ = "inventory"

    id:              Mapped[int]           = mapped_column(Integer, primary_key=True)
    part_id:         Mapped[int]           = mapped_column(ForeignKey("parts.id"), unique=True, nullable=False)
    quantity:        Mapped[Decimal]       = mapped_column(Numeric(12, 2), default=0)
    min_stock_alert: Mapped[Decimal]       = mapped_column(Numeric(12, 2), default=0)
    location:        Mapped[Optional[str]] = mapped_column(String(100))
    last_updated:    Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())

    part: Mapped["Part"] = relationship("Part", back_populates="inventory")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id:             Mapped[int]           = mapped_column(Integer, primary_key=True)
    part_id:        Mapped[int]           = mapped_column(ForeignKey("parts.id"), nullable=False)
    movement_type:  Mapped[str]           = mapped_column(String(30), nullable=False)
    quantity:       Mapped[Decimal]       = mapped_column(Numeric(12, 2), nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(30))
    reference_id:   Mapped[Optional[int]] = mapped_column(Integer)
    notes:          Mapped[Optional[str]] = mapped_column(Text)
    created_by:     Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    created_at:     Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())

    part:    Mapped["Part"]          = relationship("Part", back_populates="stock_movements")
    creator: Mapped[Optional["User"]]= relationship("User", back_populates="stock_movements")


# ============================================================
# 6. QUOTATIONS
# ============================================================

class Quotation(Base):
    __tablename__ = "quotations"

    id:               Mapped[int]                      = mapped_column(Integer, primary_key=True)
    quotation_number: Mapped[str]                      = mapped_column(String(50), unique=True, nullable=False)
    customer_id:      Mapped[int]                      = mapped_column(ForeignKey("customers.id"), nullable=False)
    created_by:       Mapped[int]                      = mapped_column(ForeignKey("users.id"), nullable=False)
    issue_date:       Mapped[date]                     = mapped_column(Date, nullable=False)
    valid_until:      Mapped[Optional[date]]           = mapped_column(Date)
    payment_terms:    Mapped[Optional[str]]            = mapped_column(String(100))
    delivery_terms:   Mapped[Optional[str]]            = mapped_column(String(100))
    city:             Mapped[Optional[str]]            = mapped_column(String(100))
    status:           Mapped[QuotationStatusEnum]      = mapped_column(Enum(QuotationStatusEnum), default=QuotationStatusEnum.draft)
    subtotal:         Mapped[Decimal]                  = mapped_column(Numeric(12, 2), default=0)
    vat_rate:         Mapped[Decimal]                  = mapped_column(Numeric(5, 2), default=15.00)
    vat_amount:       Mapped[Decimal]                  = mapped_column(Numeric(12, 2), default=0)
    total_amount:     Mapped[Decimal]                  = mapped_column(Numeric(12, 2), default=0)
    notes:            Mapped[Optional[str]]            = mapped_column(Text)
    created_at:       Mapped[datetime]                 = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:       Mapped[datetime]                 = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer: Mapped["Customer"]           = relationship("Customer", back_populates="quotations")
    creator:  Mapped["User"]               = relationship("User", back_populates="quotations", foreign_keys=[created_by])
    items:    Mapped[list["QuotationItem"]]= relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    invoices: Mapped[list["Invoice"]]      = relationship("Invoice", back_populates="quotation")
    rfqs:     Mapped[list["RFQ"]]          = relationship("RFQ", back_populates="quotation")


class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id:           Mapped[int]            = mapped_column(Integer, primary_key=True)
    quotation_id: Mapped[int]            = mapped_column(ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    part_id:      Mapped[Optional[int]]  = mapped_column(ForeignKey("parts.id"))
    part_number:  Mapped[Optional[str]]  = mapped_column(String(100))
    description:  Mapped[str]            = mapped_column(Text, nullable=False)
    quantity:     Mapped[Decimal]        = mapped_column(Numeric(12, 2), nullable=False)
    unit:         Mapped[Optional[str]]  = mapped_column(String(20))
    cost_price:   Mapped[Decimal]        = mapped_column(Numeric(12, 2), default=0)
    unit_price:   Mapped[Decimal]        = mapped_column(Numeric(12, 2), nullable=False)
    sort_order:   Mapped[int]            = mapped_column(Integer, default=0)

    quotation: Mapped["Quotation"]    = relationship("Quotation", back_populates="items")
    part:      Mapped[Optional["Part"]] = relationship("Part", back_populates="quotation_items")

    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.unit_price


# ============================================================
# 7. INVOICES
# ============================================================

class Invoice(Base):
    __tablename__ = "invoices"

    id:             Mapped[int]                 = mapped_column(Integer, primary_key=True)
    invoice_number: Mapped[str]                 = mapped_column(String(50), unique=True, nullable=False)
    quotation_id:   Mapped[Optional[int]]       = mapped_column(ForeignKey("quotations.id"))
    customer_id:    Mapped[int]                 = mapped_column(ForeignKey("customers.id"), nullable=False)
    created_by:     Mapped[int]                 = mapped_column(ForeignKey("users.id"), nullable=False)
    issue_date:     Mapped[date]                = mapped_column(Date, nullable=False)
    due_date:       Mapped[Optional[date]]      = mapped_column(Date)
    status:         Mapped[InvoiceStatusEnum]   = mapped_column(Enum(InvoiceStatusEnum), default=InvoiceStatusEnum.unpaid)
    payment_terms:  Mapped[Optional[str]]       = mapped_column(String(100))
    subtotal:       Mapped[Decimal]             = mapped_column(Numeric(12, 2), default=0)
    vat_rate:       Mapped[Decimal]             = mapped_column(Numeric(5, 2), default=15.00)
    vat_amount:     Mapped[Decimal]             = mapped_column(Numeric(12, 2), default=0)
    total_amount:   Mapped[Decimal]             = mapped_column(Numeric(12, 2), default=0)
    amount_paid:    Mapped[Decimal]             = mapped_column(Numeric(12, 2), default=0)
    notes:          Mapped[Optional[str]]       = mapped_column(Text)
    created_at:     Mapped[datetime]            = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:     Mapped[datetime]            = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer:   Mapped["Customer"]          = relationship("Customer", back_populates="invoices")
    quotation:  Mapped[Optional["Quotation"]]= relationship("Quotation", back_populates="invoices")
    creator:    Mapped["User"]              = relationship("User", back_populates="invoices", foreign_keys=[created_by])
    items:      Mapped[list["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    deliveries: Mapped[list["Delivery"]]   = relationship("Delivery", back_populates="invoice")
    returns:    Mapped[list["Return"]]     = relationship("Return", back_populates="invoice", foreign_keys="Return.invoice_id")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    invoice_id:  Mapped[int]           = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    part_id:     Mapped[Optional[int]] = mapped_column(ForeignKey("parts.id"))
    part_number: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[str]           = mapped_column(Text, nullable=False)
    quantity:    Mapped[Decimal]       = mapped_column(Numeric(12, 2), nullable=False)
    unit:        Mapped[Optional[str]] = mapped_column(String(20))
    unit_price:  Mapped[Decimal]       = mapped_column(Numeric(12, 2), nullable=False)
    sort_order:  Mapped[int]           = mapped_column(Integer, default=0)

    invoice: Mapped["Invoice"]       = relationship("Invoice", back_populates="items")
    part:    Mapped[Optional["Part"]]= relationship("Part", back_populates="invoice_items")

    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.unit_price


# ============================================================
# 8. RFQ
# ============================================================

class RFQ(Base):
    __tablename__ = "rfqs"

    id:             Mapped[int]              = mapped_column(Integer, primary_key=True)
    rfq_number:     Mapped[str]              = mapped_column(String(50), unique=True, nullable=False)
    customer_id:    Mapped[Optional[int]]    = mapped_column(ForeignKey("customers.id"))
    customer_name:  Mapped[Optional[str]]    = mapped_column(String(150))
    contact_email:  Mapped[Optional[str]]    = mapped_column(String(150))
    received_date:  Mapped[date]             = mapped_column(Date, server_default=func.current_date())
    status:         Mapped[RFQStatusEnum]    = mapped_column(Enum(RFQStatusEnum), default=RFQStatusEnum.new)
    quotation_id:   Mapped[Optional[int]]    = mapped_column(ForeignKey("quotations.id"))
    notes:          Mapped[Optional[str]]    = mapped_column(Text)
    created_by:     Mapped[Optional[int]]    = mapped_column(ForeignKey("users.id"))
    created_at:     Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:     Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer:  Mapped[Optional["Customer"]] = relationship("Customer", back_populates="rfqs")
    quotation: Mapped[Optional["Quotation"]]= relationship("Quotation", back_populates="rfqs")
    items:     Mapped[list["RFQItem"]]      = relationship("RFQItem", back_populates="rfq", cascade="all, delete-orphan")


class RFQItem(Base):
    __tablename__ = "rfq_items"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    rfq_id:      Mapped[int]           = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False)
    part_number: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[str]           = mapped_column(Text, nullable=False)
    quantity:    Mapped[Optional[Decimal]]= mapped_column(Numeric(12, 2))
    unit:        Mapped[Optional[str]] = mapped_column(String(20))
    notes:       Mapped[Optional[str]] = mapped_column(Text)

    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="items")


# ============================================================
# 9. PURCHASING
# ============================================================

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id:            Mapped[int]               = mapped_column(Integer, primary_key=True)
    po_number:     Mapped[str]               = mapped_column(String(50), unique=True, nullable=False)
    supplier_id:   Mapped[int]               = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    created_by:    Mapped[int]               = mapped_column(ForeignKey("users.id"), nullable=False)
    purchase_type: Mapped[PurchaseTypeEnum]  = mapped_column(Enum(PurchaseTypeEnum), default=PurchaseTypeEnum.cash)
    issue_date:    Mapped[date]              = mapped_column(Date, server_default=func.current_date())
    expected_date: Mapped[Optional[date]]    = mapped_column(Date)
    status:        Mapped[POStatusEnum]      = mapped_column(Enum(POStatusEnum), default=POStatusEnum.draft)
    subtotal:      Mapped[Decimal]           = mapped_column(Numeric(12, 2), default=0)
    vat_rate:      Mapped[Decimal]           = mapped_column(Numeric(5, 2), default=15.00)
    vat_amount:    Mapped[Decimal]           = mapped_column(Numeric(12, 2), default=0)
    total_amount:  Mapped[Decimal]           = mapped_column(Numeric(12, 2), default=0)
    notes:         Mapped[Optional[str]]     = mapped_column(Text)
    created_at:    Mapped[datetime]          = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:    Mapped[datetime]          = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    supplier: Mapped["Supplier"]                = relationship("Supplier", back_populates="purchase_orders")
    creator:  Mapped["User"]                    = relationship("User", back_populates="purchase_orders")
    items:    Mapped[list["PurchaseOrderItem"]]  = relationship("PurchaseOrderItem", back_populates="po", cascade="all, delete-orphan")
    returns:  Mapped[list["Return"]]            = relationship("Return", back_populates="po", foreign_keys="Return.po_id")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id:                Mapped[int]           = mapped_column(Integer, primary_key=True)
    po_id:             Mapped[int]           = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    part_id:           Mapped[Optional[int]] = mapped_column(ForeignKey("parts.id"))
    part_number:       Mapped[Optional[str]] = mapped_column(String(100))
    description:       Mapped[str]           = mapped_column(Text, nullable=False)
    quantity:          Mapped[Decimal]       = mapped_column(Numeric(12, 2), nullable=False)
    quantity_received: Mapped[Decimal]       = mapped_column(Numeric(12, 2), default=0)
    unit:              Mapped[Optional[str]] = mapped_column(String(20))
    unit_cost:         Mapped[Decimal]       = mapped_column(Numeric(12, 2), nullable=False)
    sort_order:        Mapped[int]           = mapped_column(Integer, default=0)

    po: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="items")

    @property
    def total_cost(self) -> Decimal:
        return self.quantity * self.unit_cost


# ============================================================
# 10. WEBSITE
# ============================================================

class WebsiteCategory(Base):
    __tablename__ = "website_categories"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    name:        Mapped[str]           = mapped_column(String(100), unique=True, nullable=False)
    slug:        Mapped[str]           = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url:   Mapped[Optional[str]] = mapped_column(Text)
    sort_order:  Mapped[int]           = mapped_column(Integer, default=0)
    is_visible:  Mapped[bool]          = mapped_column(Boolean, default=True)

    products: Mapped[list["WebsiteProduct"]] = relationship("WebsiteProduct", back_populates="website_category")


class WebsiteProduct(Base):
    __tablename__ = "website_products"

    id:                  Mapped[int]           = mapped_column(Integer, primary_key=True)
    part_id:             Mapped[int]           = mapped_column(ForeignKey("parts.id"), unique=True, nullable=False)
    website_category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("website_categories.id"))
    slug:                Mapped[str]           = mapped_column(String(150), unique=True, nullable=False)
    title:               Mapped[str]           = mapped_column(String(200), nullable=False)
    description:         Mapped[Optional[str]] = mapped_column(Text)
    image_url:           Mapped[Optional[str]] = mapped_column(Text)
    is_featured:         Mapped[bool]          = mapped_column(Boolean, default=False)
    sort_order:          Mapped[int]           = mapped_column(Integer, default=0)
    meta_title:          Mapped[Optional[str]] = mapped_column(String(200))
    meta_description:    Mapped[Optional[str]] = mapped_column(Text)
    created_at:          Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:          Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    part:             Mapped["Part"]                    = relationship("Part", back_populates="website_product")
    website_category: Mapped[Optional["WebsiteCategory"]]= relationship("WebsiteCategory", back_populates="products")


class WebsiteInquiry(Base):
    __tablename__ = "website_inquiries"

    id:               Mapped[int]           = mapped_column(Integer, primary_key=True)
    name:             Mapped[str]           = mapped_column(String(100), nullable=False)
    email:            Mapped[str]           = mapped_column(String(150), nullable=False)
    phone:            Mapped[Optional[str]] = mapped_column(String(30))
    company:          Mapped[Optional[str]] = mapped_column(String(150))
    message:          Mapped[Optional[str]] = mapped_column(Text)
    part_id:          Mapped[Optional[int]] = mapped_column(ForeignKey("parts.id"))
    is_read:          Mapped[bool]          = mapped_column(Boolean, default=False)
    converted_to_rfq: Mapped[Optional[int]] = mapped_column(ForeignKey("rfqs.id"))
    created_at:       Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())


# ============================================================
# 11. DELIVERIES
# ============================================================

class Delivery(Base):
    __tablename__ = "deliveries"

    id:               Mapped[int]                  = mapped_column(Integer, primary_key=True)
    delivery_number:  Mapped[str]                  = mapped_column(String(50), unique=True, nullable=False)
    invoice_id:       Mapped[Optional[int]]        = mapped_column(ForeignKey("invoices.id"))
    customer_id:      Mapped[int]                  = mapped_column(ForeignKey("customers.id"), nullable=False)
    created_by:       Mapped[Optional[int]]        = mapped_column(ForeignKey("users.id"))
    status:           Mapped[DeliveryStatusEnum]   = mapped_column(Enum(DeliveryStatusEnum), default=DeliveryStatusEnum.pending)
    carrier_name:     Mapped[Optional[str]]        = mapped_column(String(100))
    tracking_number:  Mapped[Optional[str]]        = mapped_column(String(100))
    dispatch_date:    Mapped[Optional[date]]       = mapped_column(Date)
    estimated_date:   Mapped[Optional[date]]       = mapped_column(Date)
    delivered_date:   Mapped[Optional[date]]       = mapped_column(Date)
    delivery_address: Mapped[Optional[str]]        = mapped_column(Text)
    city:             Mapped[Optional[str]]        = mapped_column(String(100))
    country:          Mapped[Optional[str]]        = mapped_column(String(100), default="Saudi Arabia")
    recipient_name:   Mapped[Optional[str]]        = mapped_column(String(100))
    recipient_phone:  Mapped[Optional[str]]        = mapped_column(String(30))
    notes:            Mapped[Optional[str]]        = mapped_column(Text)
    created_at:       Mapped[datetime]             = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:       Mapped[datetime]             = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    invoice:    Mapped[Optional["Invoice"]]       = relationship("Invoice", back_populates="deliveries")
    customer:   Mapped["Customer"]                = relationship("Customer", back_populates="deliveries")
    items:      Mapped[list["DeliveryItem"]]      = relationship("DeliveryItem", back_populates="delivery", cascade="all, delete-orphan")
    status_log: Mapped[list["DeliveryStatusLog"]] = relationship("DeliveryStatusLog", back_populates="delivery", cascade="all, delete-orphan")


class DeliveryItem(Base):
    __tablename__ = "delivery_items"

    id:                 Mapped[int]           = mapped_column(Integer, primary_key=True)
    delivery_id:        Mapped[int]           = mapped_column(ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False)
    invoice_item_id:    Mapped[Optional[int]] = mapped_column(ForeignKey("invoice_items.id"))
    part_id:            Mapped[Optional[int]] = mapped_column(ForeignKey("parts.id"))
    part_number:        Mapped[Optional[str]] = mapped_column(String(100))
    description:        Mapped[str]           = mapped_column(Text, nullable=False)
    quantity_ordered:   Mapped[Decimal]       = mapped_column(Numeric(12, 2), nullable=False)
    quantity_delivered: Mapped[Decimal]       = mapped_column(Numeric(12, 2), nullable=False)
    unit:               Mapped[Optional[str]] = mapped_column(String(20))
    notes:              Mapped[Optional[str]] = mapped_column(Text)

    delivery: Mapped["Delivery"] = relationship("Delivery", back_populates="items")


class DeliveryStatusLog(Base):
    __tablename__ = "delivery_status_log"

    id:          Mapped[int]                       = mapped_column(Integer, primary_key=True)
    delivery_id: Mapped[int]                       = mapped_column(ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False)
    old_status:  Mapped[Optional[DeliveryStatusEnum]]= mapped_column(Enum(DeliveryStatusEnum))
    new_status:  Mapped[DeliveryStatusEnum]        = mapped_column(Enum(DeliveryStatusEnum), nullable=False)
    changed_by:  Mapped[Optional[int]]             = mapped_column(ForeignKey("users.id"))
    notes:       Mapped[Optional[str]]             = mapped_column(Text)
    changed_at:  Mapped[datetime]                  = mapped_column(DateTime(timezone=True), server_default=func.now())

    delivery: Mapped["Delivery"] = relationship("Delivery", back_populates="status_log")


# ============================================================
# 12. RETURNS & REFUNDS
# ============================================================

class Return(Base):
    __tablename__ = "returns"

    id:            Mapped[int]                      = mapped_column(Integer, primary_key=True)
    return_number: Mapped[str]                      = mapped_column(String(50), unique=True, nullable=False)
    return_type:   Mapped[ReturnTypeEnum]           = mapped_column(Enum(ReturnTypeEnum), nullable=False)
    status:        Mapped[ReturnStatusEnum]         = mapped_column(Enum(ReturnStatusEnum), default=ReturnStatusEnum.requested)
    reason:        Mapped[Optional[ReturnReasonEnum]]= mapped_column(Enum(ReturnReasonEnum))
    reason_detail: Mapped[Optional[str]]            = mapped_column(Text)
    invoice_id:    Mapped[Optional[int]]            = mapped_column(ForeignKey("invoices.id"))
    customer_id:   Mapped[Optional[int]]            = mapped_column(ForeignKey("customers.id"))
    po_id:         Mapped[Optional[int]]            = mapped_column(ForeignKey("purchase_orders.id"))
    supplier_id:   Mapped[Optional[int]]            = mapped_column(ForeignKey("suppliers.id"))
    requested_by:  Mapped[Optional[int]]            = mapped_column(ForeignKey("users.id"))
    approved_by:   Mapped[Optional[int]]            = mapped_column(ForeignKey("users.id"))
    request_date:  Mapped[date]                     = mapped_column(Date, server_default=func.current_date())
    approved_date: Mapped[Optional[date]]           = mapped_column(Date)
    received_date: Mapped[Optional[date]]           = mapped_column(Date)
    resolution:    Mapped[Optional[str]]            = mapped_column(String(50))
    refund_amount: Mapped[Decimal]                  = mapped_column(Numeric(12, 2), default=0)
    notes:         Mapped[Optional[str]]            = mapped_column(Text)
    created_at:    Mapped[datetime]                 = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:    Mapped[datetime]                 = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    invoice:    Mapped[Optional["Invoice"]]       = relationship("Invoice", back_populates="returns", foreign_keys=[invoice_id])
    customer:   Mapped[Optional["Customer"]]      = relationship("Customer", back_populates="returns", foreign_keys=[customer_id])
    po:         Mapped[Optional["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="returns", foreign_keys=[po_id])
    supplier:   Mapped[Optional["Supplier"]]      = relationship("Supplier", back_populates="returns", foreign_keys=[supplier_id])
    items:      Mapped[list["ReturnItem"]]         = relationship("ReturnItem", back_populates="return_record", cascade="all, delete-orphan")
    status_log: Mapped[list["ReturnStatusLog"]]   = relationship("ReturnStatusLog", back_populates="return_record", cascade="all, delete-orphan")


class ReturnItem(Base):
    __tablename__ = "return_items"

    id:                 Mapped[int]           = mapped_column(Integer, primary_key=True)
    return_id:          Mapped[int]           = mapped_column(ForeignKey("returns.id", ondelete="CASCADE"), nullable=False)
    part_id:            Mapped[Optional[int]] = mapped_column(ForeignKey("parts.id"))
    part_number:        Mapped[Optional[str]] = mapped_column(String(100))
    description:        Mapped[str]           = mapped_column(Text, nullable=False)
    quantity_requested: Mapped[Decimal]       = mapped_column(Numeric(12, 2), nullable=False)
    quantity_approved:  Mapped[Decimal]       = mapped_column(Numeric(12, 2), default=0)
    quantity_received:  Mapped[Decimal]       = mapped_column(Numeric(12, 2), default=0)
    unit:               Mapped[Optional[str]] = mapped_column(String(20))
    unit_price:         Mapped[Decimal]       = mapped_column(Numeric(12, 2), default=0)
    condition:          Mapped[Optional[str]] = mapped_column(String(50))
    notes:              Mapped[Optional[str]] = mapped_column(Text)

    return_record: Mapped["Return"] = relationship("Return", back_populates="items")

    @property
    def total_price(self) -> Decimal:
        return self.quantity_approved * self.unit_price


class ReturnStatusLog(Base):
    __tablename__ = "return_status_log"

    id:          Mapped[int]                     = mapped_column(Integer, primary_key=True)
    return_id:   Mapped[int]                     = mapped_column(ForeignKey("returns.id", ondelete="CASCADE"), nullable=False)
    old_status:  Mapped[Optional[ReturnStatusEnum]]= mapped_column(Enum(ReturnStatusEnum))
    new_status:  Mapped[ReturnStatusEnum]        = mapped_column(Enum(ReturnStatusEnum), nullable=False)
    changed_by:  Mapped[Optional[int]]           = mapped_column(ForeignKey("users.id"))
    notes:       Mapped[Optional[str]]           = mapped_column(Text)
    changed_at:  Mapped[datetime]                = mapped_column(DateTime(timezone=True), server_default=func.now())

    return_record: Mapped["Return"] = relationship("Return", back_populates="status_log")


# ============================================================
# 13. AUDIT LOG
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id:         Mapped[int]           = mapped_column(BigInteger, primary_key=True)
    user_id:    Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    action:     Mapped[str]           = mapped_column(String(50), nullable=False)
    table_name: Mapped[str]           = mapped_column(String(100), nullable=False)
    record_id:  Mapped[Optional[int]] = mapped_column(Integer)
    old_data:   Mapped[Optional[dict]]= mapped_column(JSON)
    new_data:   Mapped[Optional[dict]]= mapped_column(JSON)
    created_at: Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())
