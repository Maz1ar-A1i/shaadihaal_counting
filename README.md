# Multi-Camera People Counting System

Overview
---
This project implements a multi-camera people counting system using Meta SAM 3 for detection. It captures images at intervals, averages the counts, and provides a dashboard for analytics.

Structure
---
- `backend/`: FastAPI application handling camera streams, inference, and data storage.
- `frontend/`: React application for the user interface.
- `docker/`: Docker configuration files.

Prerequisites
---
- Python 3.10+
- Node.js 18+
- Docker (optional)

Setup
---
1. cd backend && pip install -r requirements.txt
2. cd frontend && npm install
