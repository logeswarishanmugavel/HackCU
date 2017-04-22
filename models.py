from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

engine = create_engine('mysql+pymysql://root:loki123@localhost:3306/hackcu', echo=False)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# Models


# Create tables.
Base.metadata.create_all(bind=engine)
