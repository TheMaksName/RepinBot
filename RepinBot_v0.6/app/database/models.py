from sqlalchemy import String, Boolean, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Базовый класс для всех моделей
class Base(DeclarativeBase):
    ...


# Модель для активных пользователей
class ActiveUser(Base):
    __tablename__ = 'active_user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)  # Уникальный идентификатор пользователя
    name: Mapped[str] = mapped_column(String(150), nullable=False)  # Имя пользователя
    school: Mapped[str] = mapped_column(String(100), nullable=False)  # Школа пользователя
    phone_number: Mapped[str] = mapped_column(String(12), nullable=False)  # Номер телефона
    mail: Mapped[str] = mapped_column(String(50), nullable=False)  # Электронная почта
    name_mentor: Mapped[str] = mapped_column(String(150), nullable=False)  # Имя наставника
    post_mentor: Mapped[str] = mapped_column(String(100), nullable=False)  # Должность наставника
    theme: Mapped[str] = mapped_column(String(150), nullable=True, default="Не выбрана")  # Тема работы


# Модель для всех пользователей
class AllUser(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)  # Уникальный идентификатор пользователя
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)  # Никнейм пользователя
    reg_status: Mapped[bool] = mapped_column(Boolean, default=False)  # Статус регистрации


# Модель для новостей
class News(Base):
    __tablename__ = 'news'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(unique=True)  # Уникальный идентификатор поста
    text: Mapped[str] = mapped_column(Text, default=None)  # Текст новости
    image: Mapped[str] = mapped_column(String(150))  # Ссылка на изображение
    date: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())  # Дата создания/обновления


# Модель для администраторов
class Admins(Base):
    __tablename__ = 'admin'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)  # Уникальный идентификатор администратора
    nickname: Mapped[str] = mapped_column(String(50))  # Никнейм администратора


# Модель для категорий тем
class Category_themes(Base):
    __tablename__ = "category_theme"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)  # Название категории

    # Связь с темами (одна категория может иметь много тем)
    themes: Mapped[list['Themes']] = relationship("Themes", back_populates='category')


# Модель для тем
class Themes(Base):
    __tablename__ = 'theme'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)  # Название темы
    technique: Mapped[str] = mapped_column(String(50), nullable=False)
    # Внешний ключ для связи с категорией
    category_id: Mapped[int] = mapped_column(ForeignKey('category_theme.id'))

    # Связь с категорией (тема принадлежит одной категории)
    category: Mapped['Category_themes'] = relationship('Category_themes', back_populates='themes')

class Materials(Base):
    __tablename__ = "material"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str] = mapped_column(String(150), nullable=False)
