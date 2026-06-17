from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from toutiao_backend.models.base import Base


class RelatedNews(Base):
    __tablename__ = "related_news"
    __table_args__ = (
        UniqueConstraint("news_id", "related_news_id", name="news_related_unique"),
        Index("fk_related_news_news_idx", "news_id"),
        Index("fk_related_news_related_idx", "related_news_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False)
    related_news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False)
