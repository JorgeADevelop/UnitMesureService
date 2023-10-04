from chalice import Chalice, Response
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from marshmallow import Schema, fields
import os


app = Chalice(app_name='UnitMeasureService')

if os.environ.get("DEBUG", False):
    app.debug = True

db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}", echo=True)


Base = declarative_base()


class UnitMeasure(Base):
    __tablename__ = "unit_measures"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)


class UnitMeasureSchema(Schema):
    id = fields.Integer()
    name = fields.String()


Base.metadata.create_all(engine)


@app.route('/unit-measures', methods=['GET'])
def index():
    try:
        unitMeasures = []

        with Session(engine) as session:
            for data in session.query(UnitMeasure).all():
                unitMeasures.append(UnitMeasureSchema().dump(data))

        return Response(unitMeasures, status_code=200)
    except KeyError as e:
        return e


@app.route('/unit-measure/{id}', methods=['GET'])
def show(id):
    try:
        with Session(engine) as session:
            data = session.query(UnitMeasure).where(UnitMeasure.id == id).first()
            unitMeasure = UnitMeasureSchema().dump(data)

        return Response(unitMeasure, status_code=200)
    except KeyError as e:
        return e


@app.route('/unit-measure', methods=['POST'])
def store():
    try:
        json_body = app.current_request.json_body
        unitMeasure = UnitMeasure(
            name=json_body.get("name")
        )

        with Session(engine) as session:
            session.add(unitMeasure)
            session.flush()
            unitMeasure = UnitMeasureSchema().dump(unitMeasure)
            session.commit()

        return Response(unitMeasure, status_code=200)
    except KeyError as e:
        return e


@app.route('/unit-measure/{id}', methods=['PUT'])
def update(id):
    try:
        json_body = app.current_request.json_body

        with Session(engine) as session:
            unitMeasure = session.query(UnitMeasure).where(UnitMeasure.id == id).first()
            unitMeasure.name = json_body.get("name")
            unitMeasure = UnitMeasureSchema().dump(unitMeasure)
            session.query(UnitMeasure).where(UnitMeasure.id == id).update(unitMeasure)
            session.commit()

        return Response(unitMeasure, status_code=200)
    except KeyError as e:
        return e


@app.route('/unit-measure/{id}', methods=['DELETE'])
def destroy(id):
    try:
        with Session(engine) as session:
            unitMeasure = session.query(UnitMeasure).where(UnitMeasure.id == id).first()
            unitMeasure = session.query(UnitMeasure).where(UnitMeasure.id == id).delete()
            session.commit()

        unitMeasure = UnitMeasureSchema().dump(unitMeasure)
        return Response(unitMeasure, status_code=200)
    except KeyError as e:
        return e
