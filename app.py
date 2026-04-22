from functools import wraps

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from config import Config
from models import Request, User, VolunteerAction, db


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    """Load the currently logged-in user."""

    return User.query.get(int(user_id))


def role_required(*roles):
    """Restrict access to one or more user roles."""

    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()

            allowed_roles = [role.lower() for role in roles]
            if current_user.role.lower() not in allowed_roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("dashboard"))

            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator


def seed_admin():
    """Create a default admin account when it does not exist."""

    admin_email = "admin@disasterhelp.com"
    existing_admin = User.query.filter_by(email=admin_email).first()

    if not existing_admin:
        admin_user = User(
            name="Platform Admin",
            email=admin_email,
            phone="9999999999",
            role="Admin",
        )
        admin_user.set_password("Admin@123")
        db.session.add(admin_user)
        db.session.commit()


def validate_request_form(form_data):
    """Validate request form fields and return a list of error messages."""

    errors = []
    title = form_data.get("title", "").strip()
    description = form_data.get("description", "").strip()
    disaster_type = form_data.get("disaster_type", "").strip()
    urgency = form_data.get("urgency", "").strip()
    latitude = form_data.get("latitude", "").strip()
    longitude = form_data.get("longitude", "").strip()
    contact = form_data.get("contact", "").strip()

    if len(title) < 5:
        errors.append("Title must be at least 5 characters long.")
    if len(description) < 15:
        errors.append("Description must be at least 15 characters long.")
    if disaster_type not in ["Flood", "Fire", "Earthquake", "Storm"]:
        errors.append("Please choose a valid disaster type.")
    if urgency not in ["Low", "Medium", "High"]:
        errors.append("Please choose a valid urgency level.")
    if not contact or len(contact) < 7:
        errors.append("Please enter a valid contact number.")

    try:
        lat_value = float(latitude)
        lng_value = float(longitude)
        if not -90 <= lat_value <= 90:
            errors.append("Latitude must be between -90 and 90.")
        if not -180 <= lng_value <= 180:
            errors.append("Longitude must be between -180 and 180.")
    except ValueError:
        errors.append("Latitude and longitude must be valid numbers.")

    return errors


@app.route("/")
def home():
    """Render the landing page with recent public requests."""

    latest_requests = Request.query.order_by(Request.created_at.desc()).limit(6).all()
    return render_template("home.html", latest_requests=latest_requests)


@app.route("/about")
def about():
    """Render the about page."""

    return render_template("about.html")


@app.route("/contact")
def contact():
    """Render the contact page."""

    return render_template("contact.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new victim or volunteer account."""

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        phone = request.form.get("phone", "").strip()
        role = request.form.get("role", "").strip()

        errors = []

        if len(name) < 3:
            errors.append("Full name must be at least 3 characters long.")
        if "@" not in email or "." not in email:
            errors.append("Please enter a valid email address.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if len(phone) < 7:
            errors.append("Please enter a valid phone number.")
        if role not in ["Victim", "Volunteer"]:
            errors.append("Please select a valid role.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html")

        user = User(name=name, email=email, phone=phone, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user and redirect to the dashboard."""

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log out the current user."""

    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Send users to the correct dashboard based on their role."""

    if current_user.is_admin():
        return redirect(url_for("admin_dashboard"))

    if current_user.role == "Volunteer":
        requests_data = Request.query.order_by(Request.created_at.desc()).all()
        volunteer_actions = {
            action.request_id: action
            for action in VolunteerAction.query.filter_by(volunteer_id=current_user.id).all()
        }
        return render_template(
            "volunteer_dashboard.html",
            requests_data=requests_data,
            volunteer_actions=volunteer_actions,
        )

    user_requests = (
        Request.query.filter_by(created_by=current_user.id)
        .order_by(Request.created_at.desc())
        .all()
    )
    return render_template("dashboard.html", user_requests=user_requests)


@app.route("/requests")
@login_required
def view_requests():
    """Display all emergency requests."""

    requests_data = Request.query.order_by(Request.created_at.desc()).all()
    volunteer_actions = {}
    if current_user.role == "Volunteer":
        volunteer_actions = {
            action.request_id: action
            for action in VolunteerAction.query.filter_by(volunteer_id=current_user.id).all()
        }
    return render_template(
        "view_requests.html",
        requests_data=requests_data,
        volunteer_actions=volunteer_actions,
    )


@app.route("/request/create", methods=["GET", "POST"])
@login_required
@role_required("Victim")
def create_request():
    """Allow victims to create a new emergency request."""

    if request.method == "POST":
        errors = validate_request_form(request.form)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("create_request.html", form_mode="create", help_request=None)

        help_request = Request(
            title=request.form["title"].strip(),
            description=request.form["description"].strip(),
            disaster_type=request.form["disaster_type"].strip(),
            urgency=request.form["urgency"].strip(),
            latitude=float(request.form["latitude"]),
            longitude=float(request.form["longitude"]),
            contact=request.form["contact"].strip(),
            created_by=current_user.id,
        )
        db.session.add(help_request)
        db.session.commit()

        flash("Emergency request created successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_request.html", form_mode="create", help_request=None)


@app.route("/request/<int:request_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Victim")
def edit_request(request_id):
    """Allow victims to edit their own requests."""

    help_request = Request.query.get_or_404(request_id)

    if help_request.created_by != current_user.id:
        flash("You can only edit your own requests.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        errors = validate_request_form(request.form)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "create_request.html",
                form_mode="edit",
                help_request=help_request,
            )

        help_request.title = request.form["title"].strip()
        help_request.description = request.form["description"].strip()
        help_request.disaster_type = request.form["disaster_type"].strip()
        help_request.urgency = request.form["urgency"].strip()
        help_request.latitude = float(request.form["latitude"])
        help_request.longitude = float(request.form["longitude"])
        help_request.contact = request.form["contact"].strip()
        db.session.commit()

        flash("Emergency request updated successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "create_request.html",
        form_mode="edit",
        help_request=help_request,
    )


@app.route("/request/<int:request_id>/delete", methods=["POST"])
@login_required
def delete_request(request_id):
    """Delete a request owned by the victim or by the admin."""

    help_request = Request.query.get_or_404(request_id)

    if not current_user.is_admin() and help_request.created_by != current_user.id:
        flash("You do not have permission to delete this request.", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(help_request)
    db.session.commit()
    flash("Request deleted successfully.", "info")

    if current_user.is_admin():
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("dashboard"))


@app.route("/request/<int:request_id>/accept", methods=["POST"])
@login_required
@role_required("Volunteer")
def accept_request(request_id):
    """Allow a volunteer to accept a pending request."""

    help_request = Request.query.get_or_404(request_id)

    if help_request.status == "Completed":
        flash("This request has already been completed.", "warning")
        return redirect(url_for("view_requests"))

    existing_action = VolunteerAction.query.filter_by(
        request_id=request_id, volunteer_id=current_user.id
    ).first()

    if existing_action:
        flash("You have already accepted this request.", "info")
        return redirect(url_for("view_requests"))

    help_request.status = "Accepted"
    action = VolunteerAction(
        request_id=request_id,
        volunteer_id=current_user.id,
        status="Accepted",
    )
    db.session.add(action)
    db.session.commit()

    flash("Request accepted successfully.", "success")
    return redirect(url_for("view_requests"))


@app.route("/request/<int:request_id>/complete", methods=["POST"])
@login_required
@role_required("Volunteer")
def complete_request(request_id):
    """Allow the accepting volunteer to mark a request as completed."""

    help_request = Request.query.get_or_404(request_id)
    volunteer_action = VolunteerAction.query.filter_by(
        request_id=request_id, volunteer_id=current_user.id
    ).first()

    if not volunteer_action:
        flash("You must accept the request before completing it.", "danger")
        return redirect(url_for("view_requests"))

    help_request.status = "Completed"
    volunteer_action.status = "Completed"
    db.session.commit()

    flash("Request marked as completed.", "success")
    return redirect(url_for("view_requests"))


@app.route("/admin")
@login_required
@role_required("Admin")
def admin_dashboard():
    """Show user, request, and statistics data for administrators."""

    users = User.query.order_by(User.id.desc()).all()
    requests_data = Request.query.order_by(Request.created_at.desc()).all()
    statistics = {
        "total_users": User.query.count(),
        "total_requests": Request.query.count(),
        "completed_requests": Request.query.filter_by(status="Completed").count(),
    }
    return render_template(
        "admin_dashboard.html",
        users=users,
        requests_data=requests_data,
        statistics=statistics,
    )


@app.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def delete_user(user_id):
    """Allow admins to delete non-admin users."""

    user = User.query.get_or_404(user_id)

    if user.is_admin():
        flash("Admin accounts cannot be deleted from the dashboard.", "warning")
        return redirect(url_for("admin_dashboard"))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/map-data")
@login_required
def map_data():
    """Provide request marker data to JavaScript map components."""

    requests_data = Request.query.order_by(Request.created_at.desc()).all()
    return {
        "requests": [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "disaster_type": item.disaster_type,
                "urgency": item.urgency,
                "status": item.status,
                "latitude": item.latitude,
                "longitude": item.longitude,
            }
            for item in requests_data
        ]
    }


@app.context_processor
def inject_helpers():
    """Expose shared helper functions to all templates."""

    def badge_class(status):
        status_map = {
            "Pending": "warning",
            "Accepted": "primary",
            "Completed": "success",
        }
        return status_map.get(status, "secondary")

    return {"badge_class": badge_class}


with app.app_context():
    db.create_all()
    seed_admin()


if __name__ == "__main__":
    app.run(debug=True)
