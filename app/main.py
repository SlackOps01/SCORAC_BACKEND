from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from app.database import engine, get_db, Base
from sqlalchemy.orm import Session
from app import models, schemas, utils, ai_agent, oauth2
from typing import List
import io

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
def startup_event():
    # Create default admin user if not exists
    db = next(get_db())
    admin_email = "admin@example.com"
    user = db.query(models.User).filter(models.User.email == admin_email).first()
    if not user:
        hashed_password = utils.hash("admin123")
        new_admin = models.User(email=admin_email, password=hashed_password, role="admin")
        db.add(new_admin)
        db.commit()
        print(f"Created default admin user: {admin_email}")
    else:
        print("Admin user already exists")

@app.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    access_token = oauth2.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # Only allow admin to create generic users? Or allow anyone? 
    # For a school system, maybe only admin adds teachers? 
    # Let's keep it open for now or assume Admin only if requested.
    # The prompt said "endpoint to register teachers".
    
    # Check if user exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = utils.hash(user.password)
    new_user = models.User(email=user.email, password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/assignments/", response_model=schemas.AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to create assignments")
        
    new_assignment = models.Assignment(**assignment.dict())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

@app.get("/assignments/", response_model=List[schemas.AssignmentResponse])
def get_assignments(db: Session = Depends(get_db)):
    assignments = db.query(models.Assignment).all()
    return assignments

@app.get("/assignments/{id}", response_model=schemas.AssignmentResponse)
def get_assignment(id: int, db: Session = Depends(get_db)):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@app.post("/assignments/{id}/submit", response_model=schemas.ScoreResponse)
async def submit_assignment(id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # Students submit, but we haven't strictly defined student role yet.
    # Assuming any authenticated user can submit for now.
    
    assignment = db.query(models.Assignment).filter(models.Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Read file content
    content = await file.read()
    # Decode assuming utf-8, handle errors if necessary
    try:
        code_str = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a valid text/python file.")

    # Score using AI Agent
    try:
        score_result = await ai_agent.score_submission(code_str, assignment.criteria)
        return score_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring submission: {str(e)}")
