from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Stores registered users including victims, volunteers, and admins."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="Victim")

    requests = db.relationship(
        "Request",
        backref="creator",
        lazy=True,
        foreign_keys="Request.created_by",
        cascade="all, delete-orphan",
    )
    volunteer_actions = db.relationship(
        "VolunteerAction",
        backref="volunteer",
        lazy=True,
        foreign_keys="VolunteerAction.volunteer_id",
        cascade="all, delete-orphan",
    )

    def set_password(self, raw_password):
        """Hash and store the user's password."""

        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Validate a plain text password against the stored hash."""

        return check_password_hash(self.password, raw_password)

    def is_admin(self):
        """Return True when the user has administrator privileges."""

        return self.role.lower() == "admin"


class Request(db.Model):
    """Stores emergency requests submitted by victims."""

    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    disaster_type = db.Column(db.String(30), nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    volunteer_actions = db.relationship(
        "VolunteerAction",
        backref="request",
        lazy=True,
        cascade="all, delete-orphan",
    )


class VolunteerAction(db.Model):
    """Tracks which volunteer accepted or completed a request."""

    __tablename__ = "volunteer_actions"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Accepted")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
