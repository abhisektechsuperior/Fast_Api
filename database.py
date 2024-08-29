from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URl_DATABASE = 'postgresql://postgres:Abhisek2002@localhost:5432/Abhisek'

engine = create_engine(URl_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

