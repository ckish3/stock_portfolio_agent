
import datetime
from database_base import Base
import database_actions
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Recommendation(Base):
    __tablename__ = "recommendation"
    __table_args__ = {"schema": database_actions.DatabaseActions.raw_schema_name}


    id: Mapped[str] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10))
    date: Mapped[datetime.date] = mapped_column(Date)
    strong_buy: Mapped[int]
    buy: Mapped[int]
    hold: Mapped[int]
    sell: Mapped[int]
    strong_sell: Mapped[int]

    def __repr__(self) -> str:
        return f"Recommendation(id={self.id}, symbol={self.symbol}, date={self.date}, strong_buy={self.strong_buy}, buy={self.buy}, hold={self.hold}, sell={self.sell}, strong_sell={self.strong_sell})"    
    
    