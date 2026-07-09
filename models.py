"""
Database models for Stroke O Clock AAU Basketball.

Two tables:
  - Player: registration submissions from the Join page
  - AdminUser: coach/admin accounts that can log into the dashboard

Uses SQLAlchemy so the app can move from SQLite (dev) to
Postgres/MySQL (production) later without rewriting queries.
"""

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)

    # Player information
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    school = db.Column(db.String(120), nullable=False)
    height = db.Column(db.String(20))
    weight = db.Column(db.String(20))
    position = db.Column(db.String(40))
    jersey_size = db.Column(db.String(10))
    experience = db.Column(db.Text)

    # Parent / guardian information
    parent_name = db.Column(db.String(120), nullable=False)
    parent_email = db.Column(db.String(120), nullable=False)
    parent_phone = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(200))

    # Emergency information (sensitive — never rendered outside admin auth)
    emergency_contact = db.Column(db.String(120), nullable=False)
    emergency_phone = db.Column(db.String(30), nullable=False)
    medical_conditions = db.Column(db.Text)
    allergies = db.Column(db.Text)

    # Additional
    notes = db.Column(db.Text)
    agreed_to_terms = db.Column(db.Boolean, default=False, nullable=False)

    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    application_status = db.Column(db.String(20), default="Pending", nullable=False)
    # Allowed values: Pending, Accepted, Rejected, Waitlisted

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        years = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "age": self.age,
            "grade": self.grade,
            "school": self.school,
            "height": self.height,
            "weight": self.weight,
            "position": self.position,
            "jersey_size": self.jersey_size,
            "experience": self.experience,
            "parent_name": self.parent_name,
            "parent_email": self.parent_email,
            "parent_phone": self.parent_phone,
            "address": self.address,
            "emergency_contact": self.emergency_contact,
            "emergency_phone": self.emergency_phone,
            "medical_conditions": self.medical_conditions,
            "allergies": self.allergies,
            "notes": self.notes,
            "date_submitted": self.date_submitted.isoformat() if self.date_submitted else None,
            "application_status": self.application_status,
        }


class AdminUser(db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class ContactMessage(db.Model):
    """Messages submitted through the Contact page form."""
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
