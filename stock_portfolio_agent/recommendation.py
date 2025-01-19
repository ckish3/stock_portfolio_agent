
import datetime
from database_base import Base
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Recommendation(Base):
    __tablename__ = "recommendation"

    id: Mapped[str] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10))
    date: Mapped[datetime.date] = mapped_column(Date)
    strong_buy: Mapped[int]
    buy: Mapped[int]
    hold: Mapped[int]
    sell: Mapped[int]
    strong_sell: Mapped[int]