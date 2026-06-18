from datetime import datetime
from sqlalchemy import Numeric

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from app.db.database import Base


class CompanySettings(Base):

    __tablename__ = "company_settings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_name = Column(
        String(255),
        nullable=False
    )

    gst_number = Column(
        String(100),
        nullable=True
    )

    cin_number = Column(
        String(100),
        nullable=True
    )

    support_email = Column(
        String(255),
        nullable=True
    )

    website = Column(
        String(255),
        nullable=True
    )

    address_line_1 = Column(
        String(255),
        nullable=True
    )

    address_line_2 = Column(
        String(255),
        nullable=True
    )

    city = Column(
        String(100),
        nullable=True
    )

    state = Column(
        String(100),
        nullable=True
    )

    country = Column(
        String(100),
        nullable=True
    )

    postal_code = Column(
        String(20),
        nullable=True
    )

    bank_name = Column(
        String(255),
        nullable=True
    )

    account_holder_name = Column(
        String(255),
        nullable=True
    )

    account_number = Column(
        String(255),
        nullable=True
    )

    ifsc_code = Column(
        String(100),
        nullable=True
    )

    logo_url = Column(
        String(500),
        nullable=True
    )

    invoice_footer = Column(
        String(1000),
        nullable=True
    )

    terms_and_conditions = Column(
        String(5000),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    tax_percentage = Column(
        Numeric(5, 2),
        default=18.00,
        nullable=False
    )

    invoice_prefix = Column(
        String(50),
        default="INV",
        nullable=False
    )

    currency_code = Column(
        String(10),
        default="INR",
        nullable=False
    )

    currency_symbol = Column(
        String(10),
        default="₹",
        nullable=False
    )