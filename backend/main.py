from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Database 
# password="Sadman@123"
DATABASE_URL = f"postgresql://postgres:Sadman%40123@localhost/SDS"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Authentication 
SECRET_KEY = "0097b95edbdd88ead59e5ff7ffc1ce1aafb66536c05eab78cfa1f4623f0b7973"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    bookmarks = relationship("Bookmark", back_populates="user")

class HotelBooking(Base):
    __tablename__ = "hotels_bookingdotcom" 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    image = Column(String)
    stars = Column(Integer)
    price = Column(String)
    city = Column(String)
    booking_url = Column(String)


class HotelAgoda(Base):
    __tablename__ = "hotels_agoda"  
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    image = Column(String)
    stars = Column(Integer)
    price = Column(String)
    city = Column(String)
    booking_url = Column(String)

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hotel_booking_id = Column(Integer, ForeignKey("hotels_bookingdotcom.id"), nullable=True)
    hotel_agoda_id = Column(Integer, ForeignKey("hotels_agoda.id"), nullable=True)
    
    user = relationship("User", back_populates="bookmarks")
    
    hotel_booking = relationship("HotelBooking")
    hotel_agoda = relationship("HotelAgoda")

Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

from sqlalchemy.exc import SQLAlchemyError

# Routes
@app.post("/signup")
def signup(username: str, email: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_password = get_password_hash(password)

    new_user = User(username=username, email=email, password_hash=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "username": new_user.username}


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/hotels/booking")
def get_hotels_booking(db: Session = Depends(get_db)):
    return db.query(HotelBooking).all()

@app.get("/hotels/agoda")
def get_hotels_agoda(db: Session = Depends(get_db)):
    return db.query(HotelAgoda).all()

@app.post("/bookmark/{hotel_id}")
def bookmark_hotel(hotel_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = db.query(User).filter(User.username == jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    bookmark = Bookmark(user_id=user.id, hotel_id=hotel_id)
    db.add(bookmark)
    db.commit()
    return {"message": "Hotel bookmarked"}

@app.get("/bookmarks")
def get_bookmarks(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = db.query(User).filter(User.username == jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user.id).all()
    
    result = []
    for bookmark in bookmarks:
        if bookmark.hotel_booking:
            result.append(bookmark.hotel_booking) 
        elif bookmark.hotel_agoda:
            result.append(bookmark.hotel_agoda)  
    
    return result

