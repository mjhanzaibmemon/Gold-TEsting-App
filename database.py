from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Local SQLite file
DATABASE_URL = "sqlite:///tezab_gold.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    serial_no = Column(String)
    client_name = Column(String)
    date_time = Column(String)
    gold_rate_tola = Column(Float)
    gold_rate_gram = Column(Float)
    weight_air = Column(Float)
    weight_water = Column(Float)
    purity = Column(Float)
    karat = Column(Float)
    pure_gold = Column(Float)
    impurities = Column(Float)
    estimated_value = Column(Float)

# Create the table
Base.metadata.create_all(bind=engine)
