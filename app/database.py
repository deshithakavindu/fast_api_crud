
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

 # if this dockerize use this url 
 # db_url = "postgresql://postgres:root@postgres-db:5432/testing"


 #normally use this 
db_url = "postgresql://postgres:root@localhost:5432/testing"
engine = create_engine(db_url)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)