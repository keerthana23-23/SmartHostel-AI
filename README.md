# 🏨 Hostel Management System

**Author:** Keerthana M S  
**Institute:** JnanaVikas Institute Of Technology  

A web-based Hostel Management System developed using Python (Flask) and MySQL.

## Features
- Student Management
- Room Allocation
- Fee Tracking
- Complaint System

## Technologies
- Python (Flask)
- MySQL
- HTML, CSS

## Run Project
1. Import database/hostel_db.sql
2. pip install -r requirements.txt
3. python app.py


### AI Complaint Analysis (LLM)
This feature uses an LLM API to classify hostel complaints (category, priority, summary).
If API quota is unavailable, the app falls back to a mock analyzer (rule-based) to keep the demo runnable.

Enable mock mode:
USE_MOCK_AI=true

