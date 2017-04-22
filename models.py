from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

engine = create_engine('mysql+pymysql://root:root@localhost:3306/hackcu', echo=False)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# Models

class UserInfo(Base):
    __tablename__ = "UserInfo"

    user_id = Column(Integer, primary_key=True)
    name = Column(String(120))
    age = Column(Integer)
    gender = Column(String(120))
    email_id = Column(String(120))
    fb_id = Column(String(120))
    friends_list = relationship("FriendsList", foreign_keys='FriendsList.user_id')
    route_list = relationship("UserRouteInfo", foreign_keys='UserRouteInfo.user_id')

    def __repr__(self):
        return "<UserInfo: " + self.user_id + ">"


class FriendsList(Base):
    __tablename__ = "FriendsList"

    user_id = Column(Integer, ForeignKey('UserInfo.user_id'), primary_key=True)
    friend_id = Column(Integer, ForeignKey('UserInfo.user_id'), primary_key=True)

    def __repr__(self):
        return "<FriendsList: " + self.user_id + "," + self.friend_id + ">"


class RouteInfo(Base):
    __tablename__ = "RouteInfo"

    route_id = Column(Integer, primary_key=True)
    from_lat = Column(Float, primary_key=True)
    from_lng = Column(Float, primary_key=True)
    to_lat = Column(Float, primary_key=True)
    to_lng = Column(Float, primary_key=True)
    info = Column(String(10000))

    def __repr__(self):
        return "<RouteInfo: " + self.from_lat + " " + self.from_lng + "," + self.to_lat + " " + self.to_lng + ">"


class UserRouteInfo(Base):
    __tablename__ = "UserRouteInfo"

    info_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('UserInfo.user_id'))
    trip_date = Column(Date)
    route_id = Column(Integer, ForeignKey('RouteInfo.route_id'))

    def __repr__(self):
        return "<UserRouteInfo: " + self.user_id + "," + self.date + ">"


class UserInfoSchema(ModelSchema):
    class Meta:
        model = UserInfo
    friends_list = fields.Nested("FriendsListSchema", many=True)
    route_list = fields.Nested("UserRouteInfoSchema", many=True)


class FriendsListSchema(ModelSchema):
    class Meta:
        model = FriendsList


class RouteInfoSchema(ModelSchema):
    class Meta:
        model = RouteInfo


class UserRouteInfoSchema(ModelSchema):
    class Meta:
        model = UserRouteInfo


# Create tables.
Base.metadata.create_all(bind=engine)
