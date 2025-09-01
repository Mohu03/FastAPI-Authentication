from fastapi import  Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database, auth
from database import engine
# from fastapi import APIRouter

app = FastAPI()

# router = APIRouter(prefix="/auth", tags=["Authentication"])
models.Base.metadata.create_all(bind=engine)



@app.post("/register", response_model = schemas.UserResponse)
def register(user: schemas.UserRegister, db: Session = Depends(database.get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code = 400,detail = "Passwords do not match")
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code = 400, detail = "User already exists")

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username = user.username, email = user.email, password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@app.post("/login", response_model = schemas.UserResponse)
def login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code = 400, detail = "Invalid credentails")
    return db_user

@app.post("/forgot-password", response_model = schemas.UserResponse)
def forgot_password(request: schemas.ForgotPassword, db: Session = Depends(database.get_db)): 
    db_user = db.query(models.User).filter(models.User.email == request.email).first()
    if not db_user:
        raise HTTPException(status_code = 400, detail = "Invalid credentials")

    if request.new_password != request.confirm_password:
        raise HTTPException(status_code = 400, detail = "Passwords do not match")
    

    hashed_pw = auth.get_password_hash(request.new_password)
    db_user.password = hashed_pw
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users


