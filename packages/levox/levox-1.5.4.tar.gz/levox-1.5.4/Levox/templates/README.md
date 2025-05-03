# GDPR Compliant Web Application Template

This repository contains a Flask-based web application template that implements GDPR compliance features from the ground up, making it easier for developers to build GDPR-compliant web applications.

## Features

- **User Consent Management**: Comprehensive system for recording, tracking, and revoking user consent
- **Data Minimization**: Only collect and store necessary user information
- **Right to Access**: Users can export their data in a portable format (JSON)
- **Right to Erasure**: Full account deletion functionality with proper cascading deletions
- **Cookie Management**: Fine-grained cookie consent controls for both logged-in and anonymous users
- **Consent Tracking**: Records IP address, user agent, timestamps for all consent actions
- **GDPR Audit Trail**: Logs all data access and deletion requests

## Setup Instructions

1. Clone this repository

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create the requirements.txt file:
```
Flask==2.2.3
Flask-WTF==1.0.1
Flask-Login==0.6.2
SQLAlchemy==1.4.46
WTForms==3.0.1
Werkzeug==2.2.3
```

4. Create template directories:
```bash
mkdir -p templates static/css
```

5. Create basic templates (at minimum, create these empty files for now):
```
templates/
  - index.html
  - login.html
  - register.html
  - profile.html
  - consents.html
  - cookie_settings.html
  - privacy_policy.html
  - delete_account.html
  - account_deleted.html
  - error.html
```

6. Set environment variables (optional, defaults are provided in the code):
```bash
# Development
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=sqlite:///gdpr_compliant_app.db

# Production - use more secure options
export SECRET_KEY=your-very-secure-secret-key
export DATABASE_URL=postgresql://username:password@localhost/dbname
```

7. Run the application:
```bash
python webapp_gdpr_template.py
```

## GDPR Compliance Features

### Consent Management

The application implements a comprehensive consent system that:
- Records explicit consent with timestamps, IP address, and user agent
- Allows users to revoke consent at any time
- Prevents processing of data without appropriate consent
- Provides fine-grained controls for different types of data processing

### Data Access & Portability

Users can export their data in a structured, machine-readable format (JSON) including:
- Account information
- Consent history
- Data access request history

### Right to Erasure

The application implements a complete account deletion process that:
- Removes all user data from the database (using SQL cascade)
- Logs the deletion for compliance purposes
- Provides confirmation to the user

### Cookie Management

The template includes a complete cookie consent system that:
- Allows users to control which cookies are set
- Persists settings for both logged-in and anonymous users
- Displays a consent banner to first-time visitors
- Provides detailed privacy information

## Extending the Template

This template provides the basic structure for a GDPR-compliant web application. To extend it:

1. Create the HTML templates in the templates directory
2. Add your application-specific functionality
3. Ensure new data processing activities are tied to appropriate consent mechanisms
4. Update the privacy policy with details about any new data processing activities

## Legal Disclaimer

This template is provided as a technical implementation reference only. It does not constitute legal advice. Always consult with a qualified legal professional to ensure your specific implementation meets GDPR requirements for your use case and jurisdiction. 