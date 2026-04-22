# Disaster Help Coordination Platform

This is a beginner-friendly full-stack Flask website for managing disaster help requests and volunteer coordination.

## Features

- User registration and login with password hashing
- Victim dashboard to create, edit, and delete emergency requests
- Volunteer dashboard to accept and complete requests
- Admin dashboard to manage users, requests, and statistics
- OpenStreetMap integration with clickable location picker and request markers
- Responsive Bootstrap 5 interface

## Project Structure

```text
disaster_help_platform/
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── database.db
├── README.md
├── templates/
│   ├── about.html
│   ├── admin_dashboard.html
│   ├── base.html
│   ├── contact.html
│   ├── create_request.html
│   ├── dashboard.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── view_requests.html
│   └── volunteer_dashboard.html
└── static/
    ├── css/style.css
    └── js/script.js
```

## How to Run

1. Open a terminal in the `disaster_help_platform` folder.
2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

```bash
venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the Flask app:

```bash
python app.py
```

6. Open your browser and visit:

```text
http://127.0.0.1:5000
```

7. Optional: load sample test data:

```bash
python sample_data.py
```

## Default Admin Login

- Email: `admin@disasterhelp.com`
- Password: `Admin@123`

## Sample Test Data

Run `python sample_data.py` to add these ready-made records:

- Victim: `victim@example.com` / `Victim@123`
- Volunteer: `volunteer@example.com` / `Volunteer@123`
- Request: `Need food supplies` at `13.0827, 80.2707`
