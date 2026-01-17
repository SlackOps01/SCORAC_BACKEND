# SCORAC Backend 🎯

## What is SCORAC? (ELI5 - Explain Like I'm 5)

Imagine you're a teacher with a **magic robot helper** 🤖 that can read your students' homework and give them a score!

That's exactly what SCORAC does:

1. **Teachers** create assignments with a grading guide (like "Give high score if the code runs without errors")
2. **Students** upload their Python code
3. **The AI Robot** (Google Gemini) reads the code and gives a score from 0-100 with helpful feedback!

It's like having a tireless teaching assistant who can grade code homework 24/7! ⏰

---

## How It Works (The Simple Version) 🧩

```
📝 Teacher creates assignment → 📤 Student uploads code → 🤖 AI grades it → 📊 Student gets score!
```

---

## The Building Blocks 🧱

### 1. **Users** 👥
There are two types of people who can use this:
- **Teachers** - Can create assignments and register students
- **Admins** - Can do everything teachers can do, plus manage other users

### 2. **Assignments** 📚
A homework assignment with:
- **Title** - The name (e.g., "Hello World Program")
- **Description** - What the assignment is about
- **Criteria** - The grading guide (e.g., "Must print 'Hello World'")

### 3. **The AI Grader** 🤖
An AI-powered grading robot that:
- Reads the student's Python code
- Compares it against the grading criteria
- Gives a score (0-100) and helpful feedback

---

## What Can You Do? (API Endpoints Explained Simply) 🎮

| Action | What It Does | Who Can Do It? |
|--------|--------------|----------------|
| **Login** | Get a magic key (token) to access the system | Anyone with an account |
| **Create User** | Add a new teacher to the system | Logged-in users |
| **Create Assignment** | Make a new homework assignment | Teachers & Admins only |
| **View Assignments** | See all available assignments | Anyone |
| **View One Assignment** | Look at a specific assignment | Anyone |
| **Submit Code** | Upload Python code to get graded | Logged-in users |

---

## Tech Stack (What Powers This) ⚡

| Technology | What It's For |
|------------|---------------|
| **FastAPI** | The web framework (how the backend talks to apps) |
| **SQLite** | The database (where we store users & assignments) |
| **Pydantic** | Data validation (makes sure data is correct) |
| **JWT Tokens** | Security (magic keys that prove who you are) |
| **Google Gemini** | The AI brain that grades the code |

---

## Quick Start 🚀

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Your Environment
Create a `.env` file with:
```
OPENROUTER_API_KEY=your_api_key_here
```

### 3. Run the Server
```bash
uvicorn app.main:app --reload
```

### 4. Default Admin Login
- **Email:** `admin@example.com`
- **Password:** `admin123`

> ⚠️ **Important:** Change the default admin password in production!

---

## Try It Out! 🧪

Once the server is running, visit:
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## The Flow Explained Like a Story 📖

1. **Teacher logs in** → Gets a magic token 🔑
2. **Teacher creates an assignment** → "Write a program that says hello" with criteria "Must print exactly 'Hello'" 📝
3. **Student logs in** → Gets their own magic token 🔑
4. **Student uploads their Python file** → The file goes to the AI robot 📤
5. **AI robot reads and grades** → "Score: 95! Great job, but remember to add comments!" 🏆
6. **Student sees their feedback** → Learns and improves! 📈

---

## File Structure (Where Things Live) 📁

```
SCORAC_BACKEND/
├── app/
│   ├── main.py         # 🚪 The front door - handles all requests
│   ├── models.py       # 📦 What data looks like in the database
│   ├── schemas.py      # ✅ Rules for incoming/outgoing data
│   ├── database.py     # 💾 Connects to the database
│   ├── oauth2.py       # 🔐 Login & security stuff
│   ├── utils.py        # 🔧 Helper functions (password hashing)
│   └── ai_agent.py     # 🤖 The AI grading robot!
├── requirements.txt    # 📋 List of required packages
└── test.db            # 🗃️ The SQLite database file
```

---

## In Summary 📌

**SCORAC = Automated Code Grading Made Easy!**

| Who | Does What |
|-----|-----------|
| 👨‍🏫 Teacher | Creates assignments with grading rules |
| 👩‍🎓 Student | Submits code and gets instant feedback |
| 🤖 AI | Reads code, checks against rules, gives scores |

It's like having a super-smart, never-tired TA that can grade Python homework instantly! ✨

---

*Made with ❤️ for educators and students*
