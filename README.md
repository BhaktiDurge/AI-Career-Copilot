# AI Career Copilot

AI Career Copilot is a Flask-based web application that helps users with career guidance using AI.

## Features

- User Authentication (Signup/Login)
- OTP Email Verification
- Password Reset via Email
- AI-Powered Career Guidance
- Career History Tracking
- Secure Database Integration

## Tech Stack

- Python
- Flask
- SQLAlchemy
- TiDB Cloud
- HTML
- CSS
- Groq API

## Installation

1. Clone the repository

```bash
git clone <repository-url>
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add:

```env
DATABASE_URL=your_database_url
EMAIL_USER=your_email
EMAIL_PASSWORD=your_app_password
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
```

4. Run the application

```bash
python app.py
```

## Author

Bhakti Durge 