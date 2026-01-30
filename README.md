# Chemical Equipment Parameter Visualizer

This project is a hybrid application designed to help you upload, analyze, and visualize chemical equipment parameter data. It features a Django REST backend, a modern React web frontend, and a PyQt5 desktop app—all using the same API for a seamless experience.

---

## Features

- **CSV Upload:** Easily upload your equipment parameter datasets (CSV format) from either the web or desktop app.
- **Data Analysis:** Get instant summary statistics and analytics powered by Pandas.
- **Chart Visualization:** View your data with interactive charts (web: Chart.js, desktop: matplotlib).
- **History Management:** Always see your 5 most recent uploads, with automatic cleanup of older files.
- **PDF Reports:** Download a professional PDF report for any dataset with one click.
- **Authentication:** Secure login/logout using Django's user system.
- **Consistent UI:** Both web and desktop apps offer a similar, user-friendly workflow.

---

## Project Structure

```
backend/           # Django REST API backend
frontend/          # React web frontend
desktop_app.py     # PyQt5 desktop frontend
pyqt_test.py       # (optional) PyQt5 test script
sample_equipment_data.csv  # Example CSV for testing
```

---

## Getting Started

### 1. Backend (Django)

```zsh
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Set up your login credentials
python manage.py runserver
```
- The API will be running at `http://127.0.0.1:8000/`

### 2. Frontend (React)

```zsh
cd frontend
npm install
npm start
```
- The web app will be available at `http://localhost:3000/`

### 3. Desktop App (PyQt5)

```zsh
pip install PyQt5 matplotlib requests
python desktop_app.py
```

---

## How to Use

1. **Login:** Enter your Django username and password.
2. **Upload CSV:** Add a new dataset to see its summary, charts, and history.
3. **View Summary:** Instantly see key statistics and type breakdowns.
4. **Visualize Data:** Explore your data with interactive charts.
5. **History:** Access and download PDF reports for your last 5 uploads. When you upload a 6th file, the oldest is automatically removed.
6. **Logout:** Log out securely when you're done.

---

## API Endpoints

- `/api/upload/` — Upload a CSV file
- `/api/summary/<id>/` — Get summary for a dataset
- `/api/history/` — List your 5 most recent datasets
- `/api/report/<id>/` — Download a PDF report
- `/api/login/` — Authenticate and get access

---

## Requirements

- Python 3.8 or newer
- Django, Django REST Framework, Pandas, ReportLab, django-cors-headers
- Node.js 16 or newer
- PyQt5, matplotlib, requests

---

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute it as you wish, but it comes with no warranty.

---

## Credits

Created by Samarth Singh