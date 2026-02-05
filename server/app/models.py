from sqlalchemy import Text, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from .database import Base


class Template(Base):

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(Text)
    variables: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    embedding = mapped_column(JSON, nullable=True)
