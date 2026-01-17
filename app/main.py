from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, get_db, Base
from sqlalchemy.orm import Session
from app import models, schemas, utils, ai_agent, oauth2
from typing import List
import json

# Create tables
Base.metadata.create_all(bind=engine)

# Tags metadata for Swagger UI organization
tags_metadata = [
    {
        "name": "Authentication",
        "description": "Operations for login and token management. **Begin here** to get an access token.",
    },
    {
        "name": "Users",
        "description": "Operations for user management. Students can **self-register**, while Admins can create Teachers.",
    },
    {
        "name": "Assignments",
        "description": "Manage coursework. Teachers create assignments with specific **grading criteria** for the AI.",
    },
    {
        "name": "Submissions",
        "description": "Submit code and view **AI-graded results** with detailed feedback and plagiarism detection.",
    },
]

app = FastAPI(
    title="SCORAC Backend API",
    description="""
    **Student Code Review and Assessment Center (SCORAC)** Backend API.
    
    This API powers the automated grading system that uses AI to evaluate student submissions.
    
    ## Key Features:
    
    * 🔐 **Role-Based Auth**: Admin, Teacher, and Student roles with specific permissions.
    * 📝 **Assignment Management**: Create and manage coding assignments.
    * 🤖 **AI Grading**: Automatic code evaluation using Google Gemini.
    * 📊 **Detailed Feedback**: Strengths, weakpoints, and plagiarism detection.
    """,
    version="1.0.0",
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/login", response_model=schemas.Token, tags=["Authentication"], summary="Login and Get Token")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    access_token = oauth2.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"], summary="Create User (Admin Only)", description="Create a new Teacher or Admin. Only existing Admins can perform this action.")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # Only admin can create users (teachers or other admins)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create users")
    
    # Check if user exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = utils.hash(user.password)
    
    # Ensure teachers/admins don't have matric numbers
    matric_number = user.matric_number
    if user.role != "student":
        matric_number = None
        
    new_user = models.User(
        email=user.email, 
        password=hashed_password, 
        name=user.name,
        matric_number=matric_number,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"], summary="Student Registration", description="Public endpoint for students to register with their name and matric number.")
def register_student(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Public endpoint for student self-registration
    # Force role to be student for security
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = utils.hash(user.password)
    new_user = models.User(
        email=user.email, 
        password=hashed_password, 
        name=user.name,
        matric_number=user.matric_number,
        role="student"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/me", response_model=schemas.UserResponse, tags=["Users"], summary="Get Current User Profile", description="Retrieve details of the currently logged-in user.")
def get_current_user_info(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user

@app.post("/assignments/", response_model=schemas.AssignmentResponse, status_code=status.HTTP_201_CREATED, tags=["Assignments"], summary="Create Assignment", description="Teachers and Admins can create new assignments with grading criteria.")
def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to create assignments")
        
    new_assignment = models.Assignment(**assignment.dict())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

@app.get("/assignments/", response_model=List[schemas.AssignmentResponse], tags=["Assignments"], summary="List All Assignments", description="Retrieve a list of all available assignments.")
def get_assignments(db: Session = Depends(get_db)):
    assignments = db.query(models.Assignment).all()
    return assignments

@app.get("/assignments/{id}", response_model=schemas.AssignmentResponse, tags=["Assignments"], summary="Get Assignment Details", description="Retrieve details of a specific assignment by ID.")
def get_assignment(id: int, db: Session = Depends(get_db)):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@app.put("/assignments/{id}", response_model=schemas.AssignmentResponse, tags=["Assignments"], summary="Update Assignment", description="Update details of an existing assignment. Admin/Teacher only.")
def update_assignment(id: int, assignment_update: schemas.AssignmentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit assignments")
    
    assignment = db.query(models.Assignment).filter(models.Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Update only provided fields
    update_data = assignment_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(assignment, key, value)
    
    db.commit()
    db.refresh(assignment)
    return assignment

@app.delete("/assignments/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Assignments"], summary="Delete Assignment", description="Permanently delete an assignment. Admin/Teacher only.")
def delete_assignment(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete assignments")
    
    assignment = db.query(models.Assignment).filter(models.Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(assignment)
    db.commit()
    return None

@app.post("/assignments/{id}/submit", response_model=schemas.SubmissionResponse, tags=["Submissions"], summary="Submit Code", description="Upload a Python file for automated grading. Returns detailed feedback.")
async def submit_assignment(id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Check validation: One submission per user per assignment
    existing_submission = db.query(models.Submission).filter(
        models.Submission.assignment_id == id,
        models.Submission.user_id == current_user.id
    ).first()
    
    if existing_submission:
        raise HTTPException(status_code=400, detail="You have already submitted this assignment.")

    # Read file content
    content = await file.read()
    try:
        code_str = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a valid text/python file.")

    # Score using AI Agent
    try:
        score_result = await ai_agent.score_submission(code_str, assignment.criteria)
        
        # Save submission to database (serialize lists as JSON strings)
        new_submission = models.Submission(
            assignment_id=id,
            user_id=current_user.id,
            score=score_result.score,
            feedback=score_result.feedback,
            strengths=json.dumps(score_result.strengths),
            weakpoints=json.dumps(score_result.weakpoints),
            cheating_detected=score_result.cheating_detected,
            cheating_reason=score_result.cheating_reason,
            reasoning=score_result.reasoning
        )
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        
        # Return with proper list conversion
        return schemas.SubmissionResponse(
            id=new_submission.id,
            assignment_id=new_submission.assignment_id,
            user_id=new_submission.user_id,
            student_name=current_user.name,
            matric_number=current_user.matric_number,
            score=new_submission.score,
            feedback=new_submission.feedback,
            strengths=json.loads(new_submission.strengths) if new_submission.strengths else [],
            weakpoints=json.loads(new_submission.weakpoints) if new_submission.weakpoints else [],
            cheating_detected=new_submission.cheating_detected,
            cheating_reason=new_submission.cheating_reason,
            reasoning=new_submission.reasoning,
            created_at=new_submission.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring submission: {str(e)}")

def _build_submission_response(s: models.Submission, db: Session) -> schemas.SubmissionResponse:
    """Helper function to build submission response with student info."""
    user = db.query(models.User).filter(models.User.id == s.user_id).first()
    return schemas.SubmissionResponse(
        id=s.id,
        assignment_id=s.assignment_id,
        user_id=s.user_id,
        student_name=user.name if user else None,
        matric_number=user.matric_number if user else None,
        score=s.score,
        feedback=s.feedback,
        strengths=json.loads(s.strengths) if s.strengths else [],
        weakpoints=json.loads(s.weakpoints) if s.weakpoints else [],
        cheating_detected=s.cheating_detected or False,
        cheating_reason=s.cheating_reason,
        reasoning=s.reasoning,
        created_at=s.created_at
    )

@app.get("/submissions/", response_model=List[schemas.SubmissionResponse], tags=["Submissions"], summary="View All Submissions (Admin/Teacher)", description="Retrieve a list of all submissions from all students.")
def get_all_submissions(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # Only teachers and admins can view all submissions
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to view all submissions")
    
    submissions = db.query(models.Submission).all()
    return [_build_submission_response(s, db) for s in submissions]

@app.get("/submissions/me", response_model=List[schemas.SubmissionResponse], tags=["Submissions"], summary="View My Submissions", description="Retrieve a list of submissions made by the currently logged-in user.")
def get_my_submissions(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # Any authenticated user can view their own submissions
    submissions = db.query(models.Submission).filter(models.Submission.user_id == current_user.id).all()
    return [_build_submission_response(s, db) for s in submissions]


