from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, HTTPException, Query, Depends, status, Header, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import hashlib
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import jwt
import redis
import json

SQLALCHEMY_DATABASE_URL = "postgresql://root:root@postgres:5432/arch_db"

Base = declarative_base()

security = HTTPBearer()
r = redis.Redis("redis")


def get_current_user(token: str):
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        current_user = payload["user_id"]
    except:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials")
    return current_user


class Companion(Base):
    __tablename__ = 'recipients'

    recipient_id = Column(Integer, primary_key=True)
    recipient_login = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    second_name = Column(String(255))
    address = Column(String(255))
    password = Column(String(255), nullable=False)

    def to_dict(self):
        return {
            'recipient_id': self.recipient_id,
            'recipient_login': self.recipient_login,
            'first_name': self.first_name,
            'second_name': self.second_name,
            'address': self.address,
            'password': self.password,
        }


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()


@ app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = exc.errors()
    modified_details = []
    for error in details:
        if error["msg"] == "Field required" or error["msg"] == "missing":
            modified_details.append(
                {
                    "message": f"The field {error["loc"][1]} absent in your request",
                }
            )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": modified_details}),
    )


class CompanionCreate(BaseModel):
    recipient_login: str
    first_name: str
    second_name: str = None
    address: str = None
    password: str


class CompanionUpdate(BaseModel):
    recipient_login: str = None
    first_name: str = None
    second_name: str = None
    address: str = None
    password: str = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@ app.post("/create_recipient/")
def create_recipient(recipient: CompanionCreate, db=Depends(get_db)):
    try:

        recipient_data = recipient.model_dump()
        recipient_data['password'] = hashlib.sha256(
            recipient_data['password'].encode()).hexdigest()
        db_recipient = Companion(**recipient_data)
        db.add(db_recipient)
        db.commit()
        db.refresh(db_recipient)
        recipient_data["recipient_id"] = db_recipient.recipient_id
        key = key = f"recipient/{Companion.recipient_id}"
        r.set(key, json.dumps(db_recipient.to_dict()))
        r.expire(key, 300)
        return {"recipient_data": recipient_data}
    except:
        raise HTTPException(
            status_code=400, detail="Companion creating failed. Mayby because login not unique")


@ app.put("/update_recipient")
def update_recipient(recipient_id: int, recipient: CompanionUpdate, db=Depends(get_db), security: HTTPAuthorizationCredentials = Depends(security)):
    try:
        jwt_id = get_current_user(security.credentials)
        if jwt_id != recipient_id:
            raise HTTPException(
                status_code=400, detail="JWT does not match the user")
        db_recipient = db.query(Companion).filter(
            Companion.recipient_id == recipient_id).first()
        if db_recipient is None:
            raise HTTPException(status_code=404, detail="Companion not found")
        recipient_data = recipient.model_dump(exclude_unset=True)
        if recipient_data.get('password'):
            recipient_data['password'] = hashlib.sha256(
                recipient_data['password'].encode()).hexdigest()
        for key, value in recipient_data.items():
            setattr(db_recipient, key, value)
        db.commit()
        return {"message": "Companion updated successfully"}
    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Companion updating failed")


@ app.get("/get_recipient_details")
def get_recipient_details(recipient_id: int, db=Depends(get_db), security: HTTPAuthorizationCredentials = Depends(security)):
    try:
        jwt_id = get_current_user(security.credentials)
        if jwt_id != recipient_id:
            raise HTTPException(
                status_code=400, detail="JWT does not match the user")
        key = f"recipient/{Companion.recipient_id}"
        redis_info = r.get(key)
        if redis_info:
            return {"user": json.loads(redis_info), "from": "redis"}
        db_recipient: Companion = db.query(Companion).filter(
            Companion.recipient_id == recipient_id).first()
        if db_recipient is None:
            raise HTTPException(status_code=404, detail="Companion not found")
        r.set(key, json.dumps(db_recipient.to_dict()))
        r.expire(key, 300)
        return {"user": db_recipient, "from": "postgres"}
    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Companion getting failed, please check id and try again")


@ app.delete("/remove_recipient")
async def remove_user(recipient_id: int, db=Depends(get_db), security: HTTPAuthorizationCredentials = Depends(security)):
    try:
        jwt_id = get_current_user(security.credentials)
        if jwt_id != recipient_id:
            raise HTTPException(
                status_code=400, detail="JWT does not match the user")
        recipient = db.query(Companion).filter(
            Companion.recipient_id == recipient_id).first()
        db.delete(recipient)
        db.commit()
    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to remove user")
    finally:
        db.close()
    return {"message": "User successfully removed"}, 200


@ app.get("/search_by_name")
def search_by_name(first_name: str = Query(None, min_length=1), second_name: str = Query(None, min_length=1), db=Depends(get_db)):
    try:
        results = db.query(Companion).filter(Companion.first_name.ilike(
            f'{first_name}%'), Companion.second_name.ilike(f'{second_name}%')).all()
    except:
        raise HTTPException(
            status_code=400, detail="Bad first name or second name. Check it and try again")
    return results


@ app.get("/search_by_recipient_login/")
def search_by_username(recipient_login: str = Query(None, min_length=1), db=Depends(get_db)):
    try:
        results = db.query(Companion).filter(
            Companion.recipient_login.ilike(f'{recipient_login}%')).all()
    except:
        raise HTTPException(
            status_code=400, detail="Bad first name or second name. Check it and try again")
    return results


@ app.get("/login")
async def login_for_access_token(credentials: HTTPBasicCredentials = Depends(HTTPBasic()), db=Depends(get_db)):
    user: Companion = db.query(Companion).filter(
        Companion.recipient_login == credentials.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Basic"},
        )
    hashed_password = hashlib.sha256(credentials.password.encode()).hexdigest()
    if hashed_password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )
    to_encode = {"user_id": user.recipient_id}
    expiration = datetime.now() + timedelta(minutes=20)
    to_encode.update({"exp": expiration})
    access_token = jwt.encode(to_encode, "secret_key", algorithm="HS256")
    return {"access_token": access_token, "token_type": "bearer"}
