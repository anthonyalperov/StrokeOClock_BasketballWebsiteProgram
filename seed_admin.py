"""
Run once to create the first coach/admin account:

    python seed_admin.py

Prompts for a username, display name, and password so no
credentials are hard-coded in source control.
"""
import getpass
from app import app
from models import db, AdminUser

with app.app_context():
    db.create_all()

    print("Create the first Stroke O Clock admin account.\n")
    username = input("Username: ").strip()

    if AdminUser.query.filter_by(username=username).first():
        print(f"An admin with username '{username}' already exists. Exiting.")
        raise SystemExit(1)

    display_name = input("Display name (e.g. 'Coach Harris'): ").strip()
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Passwords did not match. Exiting.")
        raise SystemExit(1)
    if len(password) < 8:
        print("Password must be at least 8 characters. Exiting.")
        raise SystemExit(1)

    admin = AdminUser(username=username, display_name=display_name)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    print(f"\nAdmin account '{username}' created. You can now log in at /admin/login.")
