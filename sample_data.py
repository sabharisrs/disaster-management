"""Populate the database with beginner-friendly sample test data."""

from app import app
from models import Request, User, VolunteerAction, db


def create_user(name, email, phone, role, password):
    """Create a user only if the email is not already present."""

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return existing_user

    user = User(name=name, email=email, phone=phone, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


with app.app_context():
    victim = create_user(
        name="Anita Relief",
        email="victim@example.com",
        phone="9876543210",
        role="Victim",
        password="Victim@123",
    )

    volunteer = create_user(
        name="Rahul Volunteer",
        email="volunteer@example.com",
        phone="9123456780",
        role="Volunteer",
        password="Volunteer@123",
    )

    existing_request = Request.query.filter_by(title="Need food supplies").first()
    if not existing_request:
        sample_request = Request(
            title="Need food supplies",
            description="We need drinking water, dry food, blankets, and first aid support for five people.",
            disaster_type="Flood",
            urgency="High",
            latitude=13.0827,
            longitude=80.2707,
            contact="9876543210",
            status="Accepted",
            created_by=victim.id,
        )
        db.session.add(sample_request)
        db.session.commit()

        action = VolunteerAction(
            request_id=sample_request.id,
            volunteer_id=volunteer.id,
            status="Accepted",
        )
        db.session.add(action)
        db.session.commit()

    print("Sample data created successfully.")
