from chalice import Chalice
from typing import Optional
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = Chalice(app_name='UnitMeasureService')

app.debug = True

engine = create_engine("postgresql+psycopg2://postgres:salesproject123@sales-project-db.c84otiooqlgg.us-east-1.rds.amazonaws.com:5432/sales_project_dev", echo=True)


class Base(DeclarativeBase):
    pass


class UnitMeasure(Base):
    __tablename__ = "unit_measures"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"UnitMeasure(id={self.id!r}, name={self.name!r}"


Base.metadata.create_all(engine)


@app.route('/')
def index():
    return {'hello': 'world'}
