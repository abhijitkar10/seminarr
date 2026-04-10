# 🖥️ Terminal Commands - Mac & Windows (Copy-Paste Ready)

> **⚡ Tip:** Open new terminal tabs/windows for each command. Keep them running simultaneously.

---

## � Documentation Files (Updated)

**Read these in order:**

1. **[QUICK_START.md](QUICK_START.md)** - 30-second start guide ⭐
2. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was built
3. **[DOCUMENTATION_GUIDE.md](DOCUMENTATION_GUIDE.md)** - Architecture, model rationale, deployment 🆕
4. **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - 6-tab interface walkthrough
5. **[ML_MODEL.md](ML_MODEL.md)** - Model performance & metrics
6. **[DATA_PIPELINE.md](DATA_PIPELINE.md)** - Feature engineering details

---

## �📋 Prerequisites

### Mac

```bash
# Install Python (if not installed)
# Using Homebrew: brew install python3
# Or download from: https://www.python.org/downloads/
python3 --version
```

### Windows

```cmd
# Check if Python is installed
python --version
# Download from: https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

---

## 🚀 Initial Setup (One-time)

### Mac - Setup Virtual Environment

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Windows - Setup Virtual Environment

```cmd
cd C:\path\to\seminarr
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Environment Configuration (One-time)

### Mac

```bash
# Copy the example env file
cp .env.example .env
# Edit .env and add your Okta hook secret
nano .env
```

### Windows

```cmd
# Copy the example env file
copy .env.example .env
# Edit .env and add your Okta hook secret
notepad .env
```

---

## 🏃 Run the Application

### **Option A: Quick Test (No Okta needed)**

#### Mac - Terminal 1: Start API

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

#### Mac - Terminal 2: Start Dashboard

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

#### Windows - Terminal 1: Start API

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

#### Windows - Terminal 2: Start Dashboard

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
streamlit run dashboard/app.py --server.port 8501
```

**Then open in browser:**

- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs

---

### **Option B: With Okta Integration**

#### Mac - Terminal 1: Start API

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

#### Mac - Terminal 2: Start ngrok Tunnel (requires ngrok installed)

```bash
# Install ngrok first: brew install ngrok
ngrok http 8000
```

#### Mac - Terminal 3: Start Dashboard

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

#### Windows - Terminal 1: Start API

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

#### Windows - Terminal 2: Start ngrok Tunnel (requires ngrok installed)

```cmd
REM Download from: https://ngrok.com/download
ngrok http 8000
```

#### Windows - Terminal 3: Start Dashboard

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
streamlit run dashboard/app.py --server.port 8501
```

**Then open in browser:**

- Dashboard: http://localhost:8501

---

## 🧠 Train Models

### Mac - Train Models on Book1.xlsx

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
python scripts/train_all_book2.py
```

### Windows - Train Models on Book1.xlsx

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
python scripts/train_all_book2.py
```

---

## 🧪 Run Tests

### Mac - Run All Tests

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
pytest tests/ -v
```

### Windows - Run All Tests

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
pytest tests/ -v
```

### Mac - Run Specific Test File

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
pytest tests/test_features.py -v
```

### Windows - Run Specific Test File

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
pytest tests/test_features.py -v
```

---

## 🐳 Docker Commands

### Mac - Build and Run with Docker Compose

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
docker-compose up --build
```

### Windows - Build and Run with Docker Compose

```cmd
cd C:\path\to\seminarr
docker-compose up --build
```

### Mac - Stop Docker Compose

```bash
docker-compose down
```

### Windows - Stop Docker Compose

```cmd
docker-compose down
```

---

## 🔍 Type Checking & Linting

### Mac - Run Type Checker

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
mypy ml/ adapters/ dashboard/ app/ models/
```

### Windows - Run Type Checker

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
mypy ml/ adapters/ dashboard/ app/ models/
```

### Mac - Run Linter

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
ruff check .
```

### Windows - Run Linter

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
ruff check .
```

---

## 📊 Generate Sample Data

### Mac - Generate Sample CSV

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
python scripts/generate_sample_csv.py
```

### Windows - Generate Sample CSV

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
python scripts/generate_sample_csv.py
```

### Mac - Simulate Live Stream

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
python scripts/stream_simulator.py
```

### Windows - Simulate Live Stream

```cmd
cd C:\path\to\seminarr
.venv\Scripts\activate
python scripts/stream_simulator.py
```

---

## 🔄 Deactivate Virtual Environment

### Mac

```bash
deactivate
```

### Windows

```cmd
deactivate
```

---

## 💡 Quick Reference: Common Mac Shortcuts

| Action                | Command                                                             |
| --------------------- | ------------------------------------------------------------------- |
| Activate venv         | `source .venv/bin/activate`                                         |
| Deactivate venv       | `deactivate`                                                        |
| Kill port 8000        | `lsof -i :8000 \| grep LISTEN \| awk '{print $2}' \| xargs kill -9` |
| Kill port 8501        | `lsof -i :8501 \| grep LISTEN \| awk '{print $2}' \| xargs kill -9` |
| List running services | `lsof -i -P -n \| grep LISTEN`                                      |

---

## 💡 Quick Reference: Common Windows Shortcuts

| Action                | Command                                                       |
| --------------------- | ------------------------------------------------------------- |
| Activate venv         | `.venv\Scripts\activate`                                      |
| Deactivate venv       | `deactivate`                                                  |
| Kill port 8000        | `netstat -ano \| findstr :8000` then `taskkill /PID <PID> /F` |
| Kill port 8501        | `netstat -ano \| findstr :8501` then `taskkill /PID <PID> /F` |
| List running services | `netstat -ano \| findstr LISTENING`                           |

---

## 📝 Notes

- **Always keep the virtual environment activated** when running commands
- **Use separate terminal tabs/windows** for API, Dashboard, and ngrok
- **On Mac:** Use `source .venv/bin/activate` (note the `source`)
- **On Windows:** Use `.venv\Scripts\activate` (no `source`)
- **Port 8000** is for the API (FastAPI)
- **Port 8501** is for the Dashboard (Streamlit)
- **Replace paths** as needed for your system (especially the `/Users/abhijitkar/Documents/...` part for Mac)

---

**Happy coding! 🎉**
