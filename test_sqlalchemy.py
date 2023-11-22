from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import Session

from dawnlite import model

engine = create_engine("sqlite:///instance/alarms.db")

Alarm = model.Alarm

with Session(engine) as session:
    result = session.query(Alarm).all()
    for row in result:
        print(row, type(row))
        print(row.id, row.repeat_days)



