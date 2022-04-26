import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Category(SqlAlchemyBase):
    __tablename__ = 'categories'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    goods = orm.relation("Goods", back_populates='category')