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

messages = {
    "RecordFound": "The {resource} has been found successfully",
    "RecordCreated": "The {resource} has been created successfully",
    "RecordUpdated": "The {resource} with id '{id}' has been updated successfully",
    "RecordDeleted": "The {resource} with id '{id}'has been deleted successfully",
    "RecordNotFound": "The {resource} with id '{id}' has not been found",
    "RecordAlreadyExists": "The {resource} already exists",
    "InternalError": "An error occurred during your request, please try again"
}


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
        offset = app.current_request.query_params.get("offset", 1)
        limit = app.current_request.query_params.get("limit", 10)
        unitMeasures = []

        with Session(engine) as session:
            for data in session.query(UnitMeasure).offset(offset).limit(limit).all():
                unitMeasures.append(UnitMeasureSchema().dump(data))
                totalRecords = session.query(UnitMeasure).count()

        return MakeResponsePaginate(
            message=messages.get("RecordFound").format(resource="unit measures"),
            data=unitMeasures,
            totalRecords=totalRecords
        )
    except KeyError as e:
        return e


@app.route('/unit-measure/{id}', methods=['GET'])
def show(id):
    try:
        with Session(engine) as session:
            data = session.query(UnitMeasure).where(UnitMeasure.id == id).first()
            if data is None:
                return MakeResponse(
                    message=messages.get("RecordNotFound").format(resource="unit measure", id=id),
                    status_code=400
                )
            unitMeasure = UnitMeasureSchema().dump(data)

        return MakeResponse(
            message=messages.get("RecordFound").format(resource="unit measure"),
            data=unitMeasure
        )
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

        return MakeResponse(
            message=messages.get("RecordCreated").format(resource="unit measure"),
            data=unitMeasure
        )
    except KeyError as e:
        return e


@app.route('/unit-measure/{id}', methods=['PUT'])
def update(id):
    try:
        json_body = app.current_request.json_body

        with Session(engine) as session:
            unitMeasure = session.query(UnitMeasure).where(UnitMeasure.id == id).first()
            if unitMeasure is None:
                return MakeResponse(
                    message=messages.get("RecordNotFound").format(resource="unit measure", id=id),
                    status_code=400
                )
            unitMeasure.name = json_body.get("name")
            unitMeasure = UnitMeasureSchema().dump(unitMeasure)
            session.query(UnitMeasure).where(UnitMeasure.id == id).update(unitMeasure)
            session.commit()

        return MakeResponse(
            message=messages.get("RecordUpdated").format(resource="unit measure", id=id),
            data=unitMeasure
        )
    except KeyError as e:
        return e


@app.route('/unit-measure/{id}', methods=['DELETE'])
def destroy(id):
    try:
        with Session(engine) as session:
            unitMeasure = session.query(UnitMeasure).where(UnitMeasure.id == id).first()
            if unitMeasure is None:
                return MakeResponse(
                    message=messages.get("RecordNotFound").format(resource="unit measure", id=id),
                    status_code=400
                )
            unitMeasure = session.query(UnitMeasure).where(UnitMeasure.id == id).delete()
            session.commit()

        return MakeResponse(
            message=messages.get("RecordDeleted").format(resource="unit measure", id=id),
        )
    except KeyError as e:
        return e


def MakeResponse(message, data=None, status_code=200, error=None):
    status = "OK"
    if status_code == 400:
        status = "BadRequest"
    elif status_code == 500:
        status = "InternalServerError"

    return Response(body={
        "status": status,
        "code": status_code,
        "message": message,
        "error": error,
        "data": data,
    })


def MakeResponsePaginate(message, data, totalRecords):
    return Response(body={
        "status": "OK",
        "code": 200,
        "message": message,
        "error": None,
        "data": data,
        "total_records": totalRecords,
    })
