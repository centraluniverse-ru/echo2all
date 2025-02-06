from db.models import Base
from db.methods import UserCRUD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///db.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

database = UserCRUD(session)
