from sqlalchemy import ForeignKey, Table
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
    __tablename__ = 'UserInfo'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(120))
    age = Column(Integer)
    gender = Column(String(120))
    email_id = Column(String(120))
    fb_id = Column(String(120))
    friends_list = relationship("FriendsList", foreign_keys='FriendsList.user_id')
    route_list = relationship("UserRouteInfo")

    def __repr__(self):
        return "<UserInfo: " + str(self.user_id) + ">"


class FriendsList(Base):
    __tablename__ = 'FriendsList'

    user_id = Column(Integer, ForeignKey('UserInfo.user_id'), primary_key=True)
    friend_id = Column(Integer, ForeignKey('UserInfo.user_id'), primary_key=True)

    def __repr__(self):
        return "<FriendsList: " + str(self.user_id) + "," + str(self.friend_id) + ">"


class RouteInfo(Base):
    __tablename__ = 'RouteInfo'

    route_id = Column(Integer, primary_key=True)
    from_lat = Column(Float)
    from_lng = Column(Float)
    to_lat = Column(Float)
    to_lng = Column(Float)
    info = Column(String(50000))

    def __repr__(self):
        return "<RouteInfo: " + str(self.from_lat) + " " + str(self.from_lng) + "," + str(self.to_lat) + " " + str(self.to_lng) + ">"


class UserRouteInfo(Base):
    __tablename__ = 'UserRouteInfo'

    info_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('UserInfo.user_id'))
    trip_date = Column(Date)
    route_id = Column(Integer, ForeignKey('RouteInfo.route_id'))
    route_info = relationship("RouteInfo")

    def __repr__(self):
        return "<UserRouteInfo: " + str(self.info_id) + ">"


class UserInfoSchema(ModelSchema):
    class Meta:
        model = UserInfo
    friends_list = fields.Nested("FriendsListSchema", many=True)
    route_list = fields.Nested("UserRouteInfoSchema", many=True)


class FriendsListSchema(ModelSchema):
    class Meta:
        fields = ['friend_id']


class RouteInfoSchema(ModelSchema):
    class Meta:
        model = RouteInfo


class UserRouteInfoSchema(ModelSchema):
    class Meta:
        fields = ['trip_date', 'route_id', 'route_info']
    route_info = fields.Nested("RouteInfoSchema")


# Create tables.
Base.metadata.create_all(bind=engine)
