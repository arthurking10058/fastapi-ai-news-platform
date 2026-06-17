from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from toutiao_backend.models.base import Base


class History(Base):
    __tablename__ = "history"
    __table_args__ = (
        Index("fk_history_user_idx", "user_id"),
        Index("fk_history_news_idx", "news_id"),
        Index("idx_view_time", "view_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False)
    view_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
