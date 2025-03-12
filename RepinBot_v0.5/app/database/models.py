from sqlalchemy import String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class ActiveUser(Base):
    __tablename__ = 'active_user'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    school: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(12), nullable=False)
    mail: Mapped[str] = mapped_column(String(50), nullable=False)
    name_mentor: Mapped[str] = mapped_column(String(150), nullable=False)
    post_mentor: Mapped[str] = mapped_column(String(100), nullable=False)

class AllUser(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    reg_status: Mapped[bool] = mapped_column(Boolean, default=False)


