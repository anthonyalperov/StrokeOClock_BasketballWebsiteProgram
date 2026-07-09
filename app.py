"""
Stroke O Clock AAU Basketball — Flask application.

Run locally:
    pip install -r requirements.txt
    python seed_admin.py        # creates the first admin login
    python app.py                # http://127.0.0.1:5000

Phases implemented (see PROJECT PLAN):
    Phase 1 — Public pages (Home, About, What We Do, Help Us, Gallery, Contact)
    Phase 2 — Player registration form + validation + SQLite storage
    Phase 3 — Coach/Admin login + dashboard (accept/reject/waitlist, edit, delete)
"""

import os
import re
from datetime import datetime, date
from functools import wraps

from dotenv import load_dotenv
load_dotenv()  # reads variables from a local .env file, if present

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)

from models import db, Player, AdminUser, ContactMessage

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "instance", "stroke_o_clock.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------------------------------------------------------------------
# Static site content (kept in Python for now; move to DB/CMS in Phase 4)
# ---------------------------------------------------------------------------

# "What We Do" is built around the word STROKE — each letter is a pillar
# of the program.
STROKE_AREAS = [
    {
        "letter": "S",
        "title": "Support",
        "body": "A player's development doesn't happen alone. We build a community around every athlete — coaches, teammates, and families all pulling in the same direction.",
        "tags": ["Community", "Family Involvement", "Encouragement", "Accountability"],
    },
    {
        "letter": "T",
        "title": "Teamwork",
        "body": "Passing, communication, and trust on the court start with how players learn to work together in practice.",
        "tags": ["Passing", "Communication", "Team Workouts", "Trust"],
    },
    {
        "letter": "R",
        "title": "Respect",
        "body": "For teammates, coaches, opponents, and the game itself. Respect is the standard everything else is built on.",
        "tags": ["For Teammates", "For Coaches", "For Opponents", "For the Game"],
    },
    {
        "letter": "O",
        "title": "Opportunity",
        "body": "We want every player to have a real shot at growth — more reps, more competition, and more chances to be seen.",
        "tags": ["Playing Time", "Growth", "Exposure", "Competition"],
    },
    {
        "letter": "K",
        "title": "Knowledge",
        "body": "Basketball IQ separates good players from great ones. We teach the game, not just the moves.",
        "tags": ["Basketball IQ", "Film Study", "Game Situations", "Defensive Rotations"],
    },
    {
        "letter": "E",
        "title": "Effort",
        "body": "Work ethic, conditioning, and mental toughness — the habits that show up when no one's watching.",
        "tags": ["Work Ethic", "Conditioning", "Hustle", "Mental Toughness"],
    },
]

SUPPORT_OPTIONS = [
    {"title": "Become a Sponsor", "body": "Put your business in front of local families while funding player development."},
    {"title": "Donate", "body": "One-time or recurring gifts go directly toward gym time, equipment, and tournament fees."},
    {"title": "Volunteer", "body": "Help run tryouts, tournaments, and team events throughout the season."},
    {"title": "Buy Merchandise", "body": "Team gear is coming to the site soon — proceeds support the program directly."},
    {"title": "Help Cover Tournament Costs", "body": "Tournament entry fees add up fast across a season. Every contribution helps a player compete."},
    {"title": "Help Cover Travel Expenses", "body": "Away tournaments mean hotels, gas, and meals. Travel support keeps the whole roster on the road together."},
    {"title": "Donate Equipment", "body": "Basketballs, cones, resistance bands, and practice gear are always needed."},
    {"title": "Support Gym Rentals", "body": "Reliable practice time depends on consistent gym access — help us lock it in season to season."},
]

POSITIONS = ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center", "Flexible / Not Sure"]
JERSEY_SIZES = ["YS", "YM", "YL", "AS", "AM", "AL", "AXL"]
GRADES = ["3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9()\-\s+.]{7,20}$")


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please log in to access the admin dashboard.", "error")
            return redirect(url_for("admin_login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


def parse_date(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Public pages — Phase 1
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/what-we-do")
def what_we_do():
    return render_template("what-we-do.html", areas=STROKE_AREAS)


@app.route("/help-us")
def help_us():
    return render_template("help-us.html", options=SUPPORT_OPTIONS)


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ---------------------------------------------------------------------------
# Join / registration — Phase 2
# ---------------------------------------------------------------------------

@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "GET":
        return render_template(
            "join.html", form={}, positions=POSITIONS,
            jersey_sizes=JERSEY_SIZES, grades=GRADES,
        )

    form = request.form
    errors = []

    first_name = form.get("first_name", "").strip()
    last_name = form.get("last_name", "").strip()
    dob_raw = form.get("date_of_birth", "").strip()
    grade = form.get("grade", "").strip()
    school = form.get("school", "").strip()
    parent_name = form.get("parent_name", "").strip()
    parent_email = form.get("parent_email", "").strip()
    parent_phone = form.get("parent_phone", "").strip()
    emergency_contact = form.get("emergency_contact", "").strip()
    emergency_phone = form.get("emergency_phone", "").strip()
    agreed = form.get("agreement") == "on"

    dob = parse_date(dob_raw)

    # Required-field validation
    if not first_name:
        errors.append("First name is required.")
    if not last_name:
        errors.append("Last name is required.")
    if not dob_raw:
        errors.append("Date of birth is required.")
    elif not dob:
        errors.append("Date of birth must be a valid date.")
    elif dob > date.today():
        errors.append("Date of birth can't be in the future.")
    if not grade:
        errors.append("Grade is required.")
    if not school:
        errors.append("School is required.")
    if not parent_name:
        errors.append("Parent/guardian name is required.")
    if not parent_email or not EMAIL_RE.match(parent_email):
        errors.append("A valid parent/guardian email is required.")
    if not parent_phone or not PHONE_RE.match(parent_phone):
        errors.append("A valid parent/guardian phone number is required.")
    if not emergency_contact:
        errors.append("Emergency contact name is required.")
    if not emergency_phone or not PHONE_RE.match(emergency_phone):
        errors.append("A valid emergency phone number is required.")
    if not agreed:
        errors.append("You must agree to the terms to submit a registration.")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template(
            "join.html", form=form, positions=POSITIONS,
            jersey_sizes=JERSEY_SIZES, grades=GRADES,
        ), 400

    player = Player(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=dob,
        grade=grade,
        school=school,
        height=form.get("height", "").strip(),
        weight=form.get("weight", "").strip(),
        position=form.get("position", "").strip(),
        jersey_size=form.get("jersey_size", "").strip(),
        experience=form.get("experience", "").strip(),
        parent_name=parent_name,
        parent_email=parent_email,
        parent_phone=parent_phone,
        address=form.get("address", "").strip(),
        emergency_contact=emergency_contact,
        emergency_phone=emergency_phone,
        medical_conditions=form.get("medical_conditions", "").strip(),
        allergies=form.get("allergies", "").strip(),
        notes=form.get("notes", "").strip(),
        agreed_to_terms=True,
        application_status="Pending",
    )
    db.session.add(player)
    db.session.commit()

    return render_template("join-confirmation.html", player=player)


# ---------------------------------------------------------------------------
# Admin — Phase 3
# ---------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin/login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = AdminUser.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        flash("Invalid username or password.", "error")
        return render_template("admin/login.html"), 401

    session.clear()
    session["admin_id"] = user.id
    session["admin_name"] = user.display_name or user.username
    flash(f"Welcome back, {session['admin_name']}.", "success")
    next_url = request.args.get("next")
    return redirect(next_url or url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("You've been logged out.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    status_filter = request.args.get("status", "All")
    query = Player.query
    if status_filter in {"Pending", "Accepted", "Rejected", "Waitlisted"}:
        query = query.filter_by(application_status=status_filter)
    players = query.order_by(Player.date_submitted.desc()).all()

    counts = {
        "All": Player.query.count(),
        "Pending": Player.query.filter_by(application_status="Pending").count(),
        "Accepted": Player.query.filter_by(application_status="Accepted").count(),
        "Waitlisted": Player.query.filter_by(application_status="Waitlisted").count(),
        "Rejected": Player.query.filter_by(application_status="Rejected").count(),
    }
    messages = ContactMessage.query.order_by(ContactMessage.date_submitted.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        players=players, counts=counts, status_filter=status_filter,
        messages=messages,
    )


@app.route("/admin/player/<int:player_id>")
@admin_required
def admin_player_detail(player_id):
    player = Player.query.get_or_404(player_id)
    return render_template("admin/player_detail.html", player=player)


@app.route("/admin/player/<int:player_id>/status", methods=["POST"])
@admin_required
def admin_update_status(player_id):
    player = Player.query.get_or_404(player_id)
    new_status = request.form.get("status")
    if new_status not in {"Pending", "Accepted", "Rejected", "Waitlisted"}:
        abort(400)
    player.application_status = new_status
    db.session.commit()
    flash(f"{player.full_name}'s status updated to {new_status}.", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/player/<int:player_id>/delete", methods=["POST"])
@admin_required
def admin_delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    name = player.full_name
    db.session.delete(player)
    db.session.commit()
    flash(f"Deleted registration for {name}.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/player/<int:player_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_player(player_id):
    player = Player.query.get_or_404(player_id)

    if request.method == "GET":
        return render_template(
            "admin/edit_player.html", player=player,
            positions=POSITIONS, jersey_sizes=JERSEY_SIZES, grades=GRADES,
        )

    form = request.form
    player.first_name = form.get("first_name", player.first_name).strip()
    player.last_name = form.get("last_name", player.last_name).strip()
    dob = parse_date(form.get("date_of_birth", ""))
    if dob:
        player.date_of_birth = dob
    player.grade = form.get("grade", player.grade).strip()
    player.school = form.get("school", player.school).strip()
    player.height = form.get("height", "").strip()
    player.weight = form.get("weight", "").strip()
    player.position = form.get("position", "").strip()
    player.jersey_size = form.get("jersey_size", "").strip()
    player.experience = form.get("experience", "").strip()
    player.parent_name = form.get("parent_name", player.parent_name).strip()
    player.parent_email = form.get("parent_email", player.parent_email).strip()
    player.parent_phone = form.get("parent_phone", player.parent_phone).strip()
    player.address = form.get("address", "").strip()
    player.emergency_contact = form.get("emergency_contact", player.emergency_contact).strip()
    player.emergency_phone = form.get("emergency_phone", player.emergency_phone).strip()
    player.medical_conditions = form.get("medical_conditions", "").strip()
    player.allergies = form.get("allergies", "").strip()
    player.notes = form.get("notes", "").strip()

    db.session.commit()
    flash(f"Updated registration for {player.full_name}.", "success")
    return redirect(url_for("admin_player_detail", player_id=player.id))


# ---------------------------------------------------------------------------
# JSON API (used by dashboard for lightweight status updates, future mobile use)
# ---------------------------------------------------------------------------

@app.route("/api/players")
@admin_required
def api_players():
    return jsonify([p.to_dict() for p in Player.query.order_by(Player.date_submitted.desc()).all()])


if __name__ == "__main__":
    app.run(debug=True)
