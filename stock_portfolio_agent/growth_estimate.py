

import datetime
from database_base import Base
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class GrowthEstimate(Base):
    __tablename__ = "growth_estimate"
    __table_args__ = {"schema": "raw_data"}
    id: Mapped[str] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10))
    date: Mapped[datetime.date] = mapped_column(Date)
    current_quarter: Mapped[float]
    next_quarter: Mapped[float]
    current_year: Mapped[float]
    next_year: Mapped[float]
    
    def __repr__(self) -> str:
        return f"GrowthEstimate(symbol={self.symbol}, date={self.date}, current_quarter={self.current_quarter}, next_quarter={self.next_quarter}, current_year={self.current_year}, next_year={self.next_year})"