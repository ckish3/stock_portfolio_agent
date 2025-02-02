import datetime
from database_base import Base
import database_actions
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class PriceTarget(Base):
    __tablename__ = "price_target"
    __table_args__ = {"schema": database_actions.DatabaseActions.raw_schema_name}

    id: Mapped[str] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10))
    date: Mapped[datetime.date] = mapped_column(Date)
    current: Mapped[float]
    low: Mapped[float]
    high: Mapped[float]
    mean: Mapped[float]
    median: Mapped[float]

    def __repr__(self) -> str:
        return f"Recommendation(id={self.id}, symbol={self.symbol}, date={self.date}, strong_buy={self.strong_buy}, buy={self.buy}, hold={self.hold}, sell={self.sell}, strong_sell={self.strong_sell})"

