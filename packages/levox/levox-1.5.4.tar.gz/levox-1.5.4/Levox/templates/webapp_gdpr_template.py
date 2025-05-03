"""
GDPR Compliant Web Application Template

This template provides a Flask-based web application structure with built-in GDPR compliance
features including consent management, data minimization, and proper user data handling.
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gdpr_compliant_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize database
Base = declarative_base()
engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
db_session = Session()

# Define models with privacy by design principles
class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(64), unique=True, nullable=False)
    email = sa.Column(sa.String(120), unique=True, nullable=False)
    password_hash = sa.Column(sa.String(256), nullable=False)
    account_created = sa.Column(sa.DateTime, default=datetime.utcnow)
    last_login = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    # GDPR related fields
    consents = relationship("UserConsent", back_populates="user", cascade="all, delete-orphan")
    data_access_requests = relationship("DataAccessRequest", back_populates="user", cascade="all, delete-orphan")
    
    # Data minimization - only store what's necessary
    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary with minimal user data"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'account_created': self.account_created.isoformat(),
            'last_login': self.last_login.isoformat()
        }
    
    def set_password(self, password: str) -> None:
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_valid_consent(self, consent_type: str) -> bool:
        """Check if user has given valid consent for specified type"""
        for consent in self.consents:
            if consent.consent_type == consent_type and consent.is_valid():
                return True
        return False

class UserConsent(Base):
    __tablename__ = 'user_consents'
    
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    consent_type = sa.Column(sa.String(50), nullable=False)  # e.g., 'marketing', 'analytics', 'cookies'
    granted_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    revoked_at = sa.Column(sa.DateTime, nullable=True)
    ip_address = sa.Column(sa.String(50), nullable=True)
    user_agent = sa.Column(sa.String(512), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="consents")
    
    def is_valid(self) -> bool:
        """Check if consent is still valid (not revoked)"""
        return self.revoked_at is None
    
    def revoke(self) -> None:
        """Revoke this consent"""
        self.revoked_at = datetime.utcnow()

class DataAccessRequest(Base):
    __tablename__ = 'data_access_requests'
    
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    request_type = sa.Column(sa.String(50), nullable=False)  # 'export', 'deletion', 'correction'
    requested_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    completed_at = sa.Column(sa.DateTime, nullable=True)
    status = sa.Column(sa.String(20), default='pending')  # 'pending', 'processing', 'completed'
    
    # Relationships
    user = relationship("User", back_populates="data_access_requests")

# Create all tables
Base.metadata.create_all(engine)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))

# GDPR Compliance Helper Functions
def record_user_consent(user_id: int, consent_type: str) -> UserConsent:
    """Record user consent with proper tracking"""
    consent = UserConsent(
        user_id=user_id,
        consent_type=consent_type,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db_session.add(consent)
    db_session.commit()
    return consent

def revoke_user_consent(user_id: int, consent_type: str) -> bool:
    """Revoke a specific user consent"""
    consents = db_session.query(UserConsent).filter_by(
        user_id=user_id, 
        consent_type=consent_type, 
        revoked_at=None
    ).all()
    
    for consent in consents:
        consent.revoke()
    
    db_session.commit()
    return len(consents) > 0

def create_data_access_request(user_id: int, request_type: str) -> DataAccessRequest:
    """Create a new data access, correction or deletion request"""
    request = DataAccessRequest(
        user_id=user_id,
        request_type=request_type
    )
    db_session.add(request)
    db_session.commit()
    return request

def process_data_deletion(user_id: int) -> bool:
    """Process user data deletion request (Article 17 - Right to erasure)"""
    try:
        user = db_session.query(User).get(user_id)
        if not user:
            return False
            
        # Log the deletion for compliance records
        print(f"Processing deletion for user {user.username} (ID: {user.id})")
        
        # Delete the user record which will cascade to related data
        db_session.delete(user)
        db_session.commit()
        return True
    except Exception as e:
        db_session.rollback()
        print(f"Error processing deletion: {e}")
        return False

def export_user_data(user_id: int) -> Dict[str, Any]:
    """Export all user data (Article 20 - Right to data portability)"""
    user = db_session.query(User).get(user_id)
    if not user:
        return {}
        
    # Collect all user data in a portable format
    data = user.to_dict()
    
    # Add consent history
    data['consents'] = [
        {
            'type': consent.consent_type,
            'granted_at': consent.granted_at.isoformat(),
            'revoked_at': consent.revoked_at.isoformat() if consent.revoked_at else None,
        }
        for consent in user.consents
    ]
    
    # Add access request history
    data['data_requests'] = [
        {
            'type': req.request_type,
            'requested_at': req.requested_at.isoformat(),
            'completed_at': req.completed_at.isoformat() if req.completed_at else None,
            'status': req.status
        }
        for req in user.data_access_requests
    ]
    
    return data

# Routes - with proper consent handling and data minimization
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if consent was given
        marketing_consent = 'marketing_consent' in request.form
        analytics_consent = 'analytics_consent' in request.form
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db_session.add(user)
        db_session.commit()
        
        # Record user consents if provided
        if marketing_consent:
            record_user_consent(user.id, 'marketing')
            
        if analytics_consent:
            record_user_consent(user.id, 'analytics')
        
        # Always record essential consent
        record_user_consent(user.id, 'essential')
        
        # Log the user in
        login_user(user)
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db_session.query(User).filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Update last login time - GDPR audit
            user.last_login = datetime.utcnow()
            db_session.commit()
            
            login_user(user)
            return redirect(url_for('index'))
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # Data minimization - only pass necessary data to template
    return render_template('profile.html')

@app.route('/consents', methods=['GET', 'POST'])
@login_required
def manage_consents():
    if request.method == 'POST':
        # Update consents
        consent_types = ['marketing', 'analytics', 'data_processing']
        
        for consent_type in consent_types:
            # Check if consent checkbox is present
            if f'{consent_type}_consent' in request.form:
                # User wants to give consent
                if not current_user.has_valid_consent(consent_type):
                    record_user_consent(current_user.id, consent_type)
            else:
                # User wants to revoke consent
                if current_user.has_valid_consent(consent_type):
                    revoke_user_consent(current_user.id, consent_type)
                    
        return redirect(url_for('profile'))
        
    # Get current consents for display
    consents = {
        consent.consent_type: consent.is_valid() 
        for consent in current_user.consents
    }
    
    return render_template('consents.html', consents=consents)

@app.route('/export-data')
@login_required
def export_data():
    # Create a data access request record
    create_data_access_request(current_user.id, 'export')
    
    # Generate the export immediately
    user_data = export_user_data(current_user.id)
    
    # Return JSON response
    return jsonify(user_data)

@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        # Create data deletion request
        create_data_access_request(current_user.id, 'deletion')
        
        # Process deletion
        user_id = current_user.id
        logout_user()  # Log the user out first
        
        if process_data_deletion(user_id):
            return render_template('account_deleted.html')
        else:
            # If deletion failed, redirect to an error page
            return render_template('error.html', message="Account deletion failed")
    
    return render_template('delete_account.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/cookie-settings', methods=['GET', 'POST'])
def cookie_settings():
    if request.method == 'POST':
        if current_user.is_authenticated:
            # Update cookie consents for logged in users
            for consent_type in ['essential', 'functionality', 'analytics', 'advertising']:
                if f'{consent_type}_cookies' in request.form:
                    if not current_user.has_valid_consent(f'cookies_{consent_type}'):
                        record_user_consent(current_user.id, f'cookies_{consent_type}')
                else:
                    if current_user.has_valid_consent(f'cookies_{consent_type}'):
                        revoke_user_consent(current_user.id, f'cookies_{consent_type}')
        else:
            # For anonymous users, store in session
            session['cookie_consents'] = {
                'essential': 'essential_cookies' in request.form,
                'functionality': 'functionality_cookies' in request.form,
                'analytics': 'analytics_cookies' in request.form,
                'advertising': 'advertising_cookies' in request.form
            }
            
        return redirect(url_for('index'))
    
    # Determine current consent settings
    if current_user.is_authenticated:
        consents = {
            'essential': current_user.has_valid_consent('cookies_essential'),
            'functionality': current_user.has_valid_consent('cookies_functionality'),
            'analytics': current_user.has_valid_consent('cookies_analytics'),
            'advertising': current_user.has_valid_consent('cookies_advertising')
        }
    else:
        consents = session.get('cookie_consents', {
            'essential': True,  # Essential cookies are always enabled
            'functionality': False,
            'analytics': False,
            'advertising': False
        })
    
    return render_template('cookie_settings.html', consents=consents)

@app.before_request
def check_consent_banner():
    """Set a flag to show consent banner if needed"""
    if 'cookie_consent_shown' not in session:
        session['show_consent_banner'] = True
        session['cookie_consent_shown'] = True

@app.context_processor
def inject_consent_data():
    """Inject consent data into all templates"""
    if current_user.is_authenticated:
        analytics_consent = current_user.has_valid_consent('analytics')
        marketing_consent = current_user.has_valid_consent('marketing')
    else:
        consents = session.get('cookie_consents', {})
        analytics_consent = consents.get('analytics', False)
        marketing_consent = consents.get('advertising', False)
    
    show_banner = session.get('show_consent_banner', False)
    
    return {
        'analytics_enabled': analytics_consent,
        'marketing_enabled': marketing_consent,
        'show_consent_banner': show_banner
    }

if __name__ == '__main__':
    app.run(debug=False) 