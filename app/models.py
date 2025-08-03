from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for type safety
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class InvestmentType(str, Enum):
    STOCK = "stock"
    BOND = "bond"
    MUTUAL_FUND = "mutual_fund"
    CRYPTOCURRENCY = "cryptocurrency"
    REAL_ESTATE = "real_estate"
    GOLD = "gold"
    OTHER = "other"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    full_name: str = Field(max_length=100)
    password_hash: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    investments: List["Investment"] = Relationship(back_populates="user")
    wallets: List["Wallet"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    type: CategoryType = Field()
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color code
    icon: Optional[str] = Field(default=None, max_length=50)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")

    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")


class Wallet(SQLModel, table=True):
    __tablename__ = "wallets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=100)
    balance: Decimal = Field(default=Decimal("0"), decimal_places=2)
    is_primary: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="wallets")
    transactions: List["Transaction"] = Relationship(back_populates="wallet")


class Budget(SQLModel, table=True):
    __tablename__ = "budgets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    category_id: int = Field(foreign_key="categories.id")
    name: str = Field(max_length=100)
    allocated_amount: Decimal = Field(decimal_places=2)
    spent_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    remaining_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="budgets")
    category: Category = Relationship(back_populates="budgets")


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    category_id: int = Field(foreign_key="categories.id")
    wallet_id: int = Field(foreign_key="wallets.id")
    type: TransactionType = Field()
    amount: Decimal = Field(decimal_places=2)
    description: str = Field(max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="transactions")
    category: Category = Relationship(back_populates="transactions")
    wallet: Wallet = Relationship(back_populates="transactions")


class Investment(SQLModel, table=True):
    __tablename__ = "investments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=100)
    type: InvestmentType = Field()
    initial_amount: Decimal = Field(decimal_places=2)
    current_value: Decimal = Field(decimal_places=2)
    monthly_contribution: Decimal = Field(default=Decimal("0"), decimal_places=2)
    expected_return_rate: Optional[Decimal] = Field(default=None, decimal_places=4)
    description: Optional[str] = Field(default=None, max_length=1000)
    start_date: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="investments")
    investment_transactions: List["InvestmentTransaction"] = Relationship(back_populates="investment")


class InvestmentTransaction(SQLModel, table=True):
    __tablename__ = "investment_transactions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    investment_id: int = Field(foreign_key="investments.id")
    transaction_type: str = Field(max_length=20)  # buy, sell, dividend, etc.
    amount: Decimal = Field(decimal_places=2)
    quantity: Optional[Decimal] = Field(default=None, decimal_places=4)
    price_per_unit: Optional[Decimal] = Field(default=None, decimal_places=4)
    description: str = Field(max_length=500)
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    investment: Investment = Relationship(back_populates="investment_transactions")


class Report(SQLModel, table=True):
    __tablename__ = "reports"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    report_type: str = Field(max_length=50)  # monthly, yearly, category, investment
    title: str = Field(max_length=200)
    parameters: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    generated_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    full_name: str = Field(max_length=100)
    password: str = Field(min_length=8)
    role: UserRole = Field(default=UserRole.USER)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    role: Optional[UserRole] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class UserLogin(SQLModel, table=False):
    username: str = Field(max_length=50)
    password: str = Field(min_length=1)


class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    type: CategoryType = Field()
    color: Optional[str] = Field(default=None, max_length=7)
    icon: Optional[str] = Field(default=None, max_length=50)


class CategoryUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    color: Optional[str] = Field(default=None, max_length=7)
    icon: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = Field(default=None)


class WalletCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    balance: Decimal = Field(default=Decimal("0"), decimal_places=2)
    is_primary: bool = Field(default=False)


class WalletUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    balance: Optional[Decimal] = Field(default=None, decimal_places=2)
    is_primary: Optional[bool] = Field(default=None)


class BudgetCreate(SQLModel, table=False):
    category_id: int = Field()
    name: str = Field(max_length=100)
    allocated_amount: Decimal = Field(decimal_places=2)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000)


class BudgetUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    allocated_amount: Optional[Decimal] = Field(default=None, decimal_places=2)
    is_active: Optional[bool] = Field(default=None)


class TransactionCreate(SQLModel, table=False):
    category_id: int = Field()
    wallet_id: int = Field()
    type: TransactionType = Field()
    amount: Decimal = Field(decimal_places=2)
    description: str = Field(max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)
    transaction_date: Optional[datetime] = Field(default=None)


class TransactionUpdate(SQLModel, table=False):
    category_id: Optional[int] = Field(default=None)
    wallet_id: Optional[int] = Field(default=None)
    amount: Optional[Decimal] = Field(default=None, decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)
    transaction_date: Optional[datetime] = Field(default=None)


class InvestmentCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    type: InvestmentType = Field()
    initial_amount: Decimal = Field(decimal_places=2)
    current_value: Decimal = Field(decimal_places=2)
    monthly_contribution: Decimal = Field(default=Decimal("0"), decimal_places=2)
    expected_return_rate: Optional[Decimal] = Field(default=None, decimal_places=4)
    description: Optional[str] = Field(default=None, max_length=1000)
    start_date: Optional[datetime] = Field(default=None)


class InvestmentUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    current_value: Optional[Decimal] = Field(default=None, decimal_places=2)
    monthly_contribution: Optional[Decimal] = Field(default=None, decimal_places=2)
    expected_return_rate: Optional[Decimal] = Field(default=None, decimal_places=4)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_active: Optional[bool] = Field(default=None)


class InvestmentTransactionCreate(SQLModel, table=False):
    investment_id: int = Field()
    transaction_type: str = Field(max_length=20)
    amount: Decimal = Field(decimal_places=2)
    quantity: Optional[Decimal] = Field(default=None, decimal_places=4)
    price_per_unit: Optional[Decimal] = Field(default=None, decimal_places=4)
    description: str = Field(max_length=500)
    transaction_date: Optional[datetime] = Field(default=None)


class ReportCreate(SQLModel, table=False):
    report_type: str = Field(max_length=50)
    title: str = Field(max_length=200)
    parameters: Dict[str, Any] = Field(default={})
    expires_at: Optional[datetime] = Field(default=None)


# Dashboard and analytics schemas
class DashboardSummary(SQLModel, table=False):
    total_income: Decimal = Field(decimal_places=2)
    total_expenses: Decimal = Field(decimal_places=2)
    net_income: Decimal = Field(decimal_places=2)
    total_budget: Decimal = Field(decimal_places=2)
    budget_remaining: Decimal = Field(decimal_places=2)
    total_investments: Decimal = Field(decimal_places=2)
    wallet_balance: Decimal = Field(decimal_places=2)


class MonthlyTrend(SQLModel, table=False):
    month: int = Field()
    year: int = Field()
    income: Decimal = Field(decimal_places=2)
    expenses: Decimal = Field(decimal_places=2)
    net: Decimal = Field(decimal_places=2)


class CategorySummary(SQLModel, table=False):
    category_id: int = Field()
    category_name: str = Field()
    category_type: CategoryType = Field()
    total_amount: Decimal = Field(decimal_places=2)
    transaction_count: int = Field()
    budget_allocated: Optional[Decimal] = Field(default=None, decimal_places=2)
    budget_remaining: Optional[Decimal] = Field(default=None, decimal_places=2)
