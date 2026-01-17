# SCORAC Backend 🎯

**Student Code Review and Assessment Center** - An AI-powered automated code grading system for educational institutions.

---

## Table of Contents
- [What is SCORAC?](#what-is-scorac-eli5---explain-like-im-5)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [User Roles & Permissions](#user-roles--permissions)
- [Database Models](#database-models)
- [AI Grading System](#ai-grading-system)
- [File Structure](#file-structure)

---

## What is SCORAC? (ELI5 - Explain Like I'm 5)

Imagine you're a teacher with a **magic robot helper** 🤖 that can read your students' homework and give them a score!

That's exactly what SCORAC does:

1. **Teachers** create assignments with grading criteria
2. **Students** upload their Python code
3. **The AI Robot** (Google Gemini) reads the code and gives detailed feedback!

It's like having a tireless teaching assistant who can grade code homework 24/7! ⏰

```
📝 Teacher creates assignment → 📤 Student uploads code → 🤖 AI grades it → 📊 Student gets detailed feedback!
```

---

## Features

### ✅ Core Features
- **User Authentication** - JWT-based secure login system
- **Role-Based Access Control** - Admin, Teacher, and Student roles
- **Assignment Management** - Create, edit, delete assignments
- **AI-Powered Grading** - Automatic code evaluation using Google Gemini
- **Submission Tracking** - Complete history of all submissions
- **Detailed Feedback** - Strengths, weakpoints, and cheating detection

### ✅ AI Feedback Includes
| Field | Description |
|-------|-------------|
| `score` | Overall grade (0-100) |
| `feedback` | Brief summary of the submission |
| `strengths` | List of 2-5 things the student did well |
| `weakpoints` | List of 2-5 areas for improvement |
| `cheating_detected` | Boolean flag for suspected plagiarism |
| `cheating_reason` | Explanation if cheating is detected |
| `reasoning` | Detailed AI thought process |

### ✅ Cheating Detection
The AI analyzes code for:
- Overly sophisticated solutions for assignment complexity
- Unusual coding patterns suggesting copy-paste
- AI-generated code patterns (generic names, overly verbose)
- Suspiciously perfect or template-like solutions

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python web framework |
| **SQLAlchemy** | Database ORM for SQLite |
| **Pydantic** | Data validation and serialization |
| **JWT (python-jose)** | Secure authentication tokens |
| **bcrypt** | Password hashing |
| **Google Gemini** | AI-powered code grading (via OpenRouter) |
| **pydantic-ai** | AI agent framework |

---

## Quick Start

### Prerequisites
- Python 3.9+
- OpenRouter API Key (for AI grading)

### 1. Clone and Install
```bash
git clone <repository-url>
cd SCORAC_BACKEND
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
SECRET_KEY=your_jwt_secret_key_here
```

### 3. Run the Server
```bash
uvicorn app.main:app --reload
```

### 4. Access the API
- **Interactive Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 5. Default Admin Account
| Field | Value |
|-------|-------|
| Email | `admin@example.com` |
| Password | `admin123` |

> ⚠️ **Security Warning:** Change the default admin password in production!

---

## API Reference

### Authentication

#### Login
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Register Student (Public)
```http
POST /register
Content-Type: application/json

{
  "email": "student@university.edu",
  "password": "securepassword123",
  "name": "John Doe",
  "matric_number": "CSC/2024/001"
}
```

---

### Users

#### Get Current User
```http
GET /users/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "student@university.edu",
  "name": "John Doe",
  "matric_number": "CSC/2024/001",
  "role": "student"
}
```

#### Create User (Admin Only)
```http
POST /users/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "email": "teacher@university.edu",
  "password": "teacherpass123",
  "name": "Prof. Smith",
  "role": "teacher"
}
```

---

### Assignments

#### List All Assignments
```http
GET /assignments/
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Factorial Function",
    "description": "Write a recursive function to calculate factorial",
    "criteria": "Must handle n=0, use recursion, include docstring"
  }
]
```

#### Get Single Assignment
```http
GET /assignments/{id}
```

#### Create Assignment (Admin/Teacher)
```http
POST /assignments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Hello World Program",
  "description": "Write a program that prints 'Hello, World!'",
  "criteria": "Must print exactly 'Hello, World!' to stdout. Deduct points for missing punctuation."
}
```

#### Update Assignment (Admin/Teacher)
```http
PUT /assignments/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "criteria": "Updated grading criteria"
}
```

#### Delete Assignment (Admin/Teacher)
```http
DELETE /assignments/{id}
Authorization: Bearer <token>
```

---

### Submissions

#### Submit Assignment (Upload Code)
```http
POST /assignments/{id}/submit
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <python_file.py>
```

**Response:**
```json
{
  "id": 1,
  "assignment_id": 1,
  "user_id": 5,
  "student_name": "John Doe",
  "matric_number": "CSC/2024/001",
  "score": 85,
  "feedback": "Good implementation with minor improvements needed.",
  "strengths": [
    "Correct recursive implementation",
    "Handles edge case n=0",
    "Clean variable naming"
  ],
  "weakpoints": [
    "Missing docstring",
    "No input validation for negative numbers"
  ],
  "cheating_detected": false,
  "cheating_reason": null,
  "reasoning": "The solution demonstrates understanding of recursion...",
  "created_at": "2026-01-17T14:30:00Z"
}
```

#### View All Submissions (Admin/Teacher)
```http
GET /submissions/
Authorization: Bearer <token>
```

#### View My Submissions (Student)
```http
GET /submissions/me
Authorization: Bearer <token>
```

---

## User Roles & Permissions

| Permission | Admin | Teacher | Student |
|------------|:-----:|:-------:|:-------:|
| Login | ✅ | ✅ | ✅ |
| View assignments | ✅ | ✅ | ✅ |
| Create assignments | ✅ | ✅ | ❌ |
| Edit/Delete assignments | ✅ | ✅ | ❌ |
| Submit code | ✅ | ✅ | ✅ |
| View own submissions | ✅ | ✅ | ✅ |
| View all submissions | ✅ | ✅ | ❌ |
| Create users (any role) | ✅ | ❌ | ❌ |
| Self-register | N/A | N/A | ✅ (`POST /register`) |

---

## Database Models

### User
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `email` | String | Unique email address |
| `password` | String | Hashed password (bcrypt) |
| `name` | String | Full name (optional) |
| `matric_number` | String | Student ID (unique, optional) |
| `role` | String | `admin`, `teacher`, or `student` |

### Assignment
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `title` | String | Assignment title |
| `description` | String | Detailed description |
| `criteria` | Text | Grading criteria for AI |

### Submission
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `assignment_id` | Integer | Foreign key to Assignment |
| `user_id` | Integer | Foreign key to User |
| `score` | Integer | Grade (0-100) |
| `feedback` | Text | AI-generated feedback summary |
| `strengths` | Text (JSON) | List of positive aspects |
| `weakpoints` | Text (JSON) | List of areas for improvement |
| `cheating_detected` | Boolean | Plagiarism flag |
| `cheating_reason` | Text | Explanation if cheating detected |
| `reasoning` | Text | AI reasoning process |
| `created_at` | DateTime | Submission timestamp |

---

## AI Grading System

### How It Works
1. **Student uploads** a Python file to an assignment
2. **System retrieves** the assignment's grading criteria
3. **AI Agent** (Google Gemini via OpenRouter) analyzes:
   - Code correctness and functionality
   - Adherence to grading criteria
   - Code quality and style
   - Potential plagiarism indicators
4. **Structured response** is generated with score and detailed feedback
5. **Submission is saved** to database with all feedback

### Grading Criteria Guidelines
When creating assignments, write clear criteria for the AI:

**Good Example:**
```
Function must be named 'factorial'.
Must handle n=0 returning 1.
Must use recursion (not loops).
Deduct 10 points for missing docstring.
Deduct 20 points for not handling negative numbers.
```

**Poor Example:**
```
Write good code.
```

---

## File Structure

```
SCORAC_BACKEND/
├── app/
│   ├── __init__.py       # Package marker
│   ├── main.py           # 🚪 FastAPI application & routes
│   ├── models.py         # 📦 SQLAlchemy database models
│   ├── schemas.py        # ✅ Pydantic validation schemas
│   ├── database.py       # 💾 Database connection & session
│   ├── oauth2.py         # 🔐 JWT authentication logic
│   ├── utils.py          # 🔧 Password hashing utilities
│   └── ai_agent.py       # 🤖 AI grading agent (pydantic-ai)
├── .env                  # 🔑 Environment variables (not in git)
├── .gitignore            # 📝 Git ignore rules
├── requirements.txt      # 📋 Python dependencies
├── test.db               # 🗃️ SQLite database file
├── verify_app.py         # 🧪 Integration test script
└── README.md             # 📖 This documentation
```

---

## Environment Variables

| Variable | Required | Description |
|----------|:--------:|-------------|
| `OPENROUTER_API_KEY` | ✅ | API key for OpenRouter (AI grading) |
| `SECRET_KEY` | ⚠️ | JWT signing key (uses default if not set) |
| `ALGORITHM` | ❌ | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | Token expiry (default: `30`) |

---

## Testing

### Run Integration Tests
```bash
python verify_app.py
```

This script tests:
- Admin login
- Teacher registration
- Assignment creation
- Assignment listing
- Code submission and AI grading

---

## Deployment Notes

### Database Migration
When updating models, delete the SQLite database and restart:
```bash
del test.db  # Windows
rm test.db   # Linux/Mac
uvicorn app.main:app --reload
```

### Production Recommendations
1. **Change default admin password** immediately
2. **Set a strong SECRET_KEY** in environment
3. **Use PostgreSQL** instead of SQLite for production
4. **Enable HTTPS** in production
5. **Restrict CORS origins** (currently allows all)

---

## Error Handling

| Status Code | Meaning |
|-------------|---------|
| `200` | Success |
| `201` | Created successfully |
| `204` | Deleted successfully (no content) |
| `400` | Bad request (validation error) |
| `401` | Unauthorized (invalid/missing token) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Not found |
| `500` | Server error (check AI service) |

---

## Example Workflow

### For Teachers
1. **Login** → `POST /login`
2. **Create assignment** → `POST /assignments/`
3. **View submissions** → `GET /submissions/`
4. **Review flagged submissions** → Check `cheating_detected` field

### For Students
1. **Register** → `POST /register` (include name and matric number)
2. **Login** → `POST /login`
3. **View assignments** → `GET /assignments/`
4. **Submit code** → `POST /assignments/{id}/submit`
5. **View feedback** → `GET /submissions/me`

---

## License

MIT License - Feel free to use and modify for educational purposes.

---

*Made with ❤️ for educators and students*
