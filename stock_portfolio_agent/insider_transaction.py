
import datetime
from database_base import Base
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class InsiderTransaction(Base):
    __tablename__ = "insider_transaction"
    __table_args__ = {"schema": "raw_data"}
    
    id: Mapped[str] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10))
    date: Mapped[datetime.date] = mapped_column(Date)
    purchases: Mapped[int]
    sales: Mapped[int]
    insider_shares_held: Mapped[int]
