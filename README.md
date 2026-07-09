# Stroke O Clock — AAU Basketball Website

Full-stack site for Stroke O Clock AAU Basketball: public pages, a player
registration form, and a coach/admin dashboard for managing applications.

Covers **Phase 1–3** of the original project plan (public site, registration
+ database, admin login + dashboard). Phase 4–5 items (gallery uploads,
player/parent accounts, payments, merch store) are intentionally left as
next steps — see "What's next" below.

## Tech stack
- **Backend:** Flask + SQLAlchemy (`app.py`, `models.py`)
- **Database:** SQLite (`instance/stroke_o_clock.db`, created automatically)
- **Frontend:** Server-rendered Jinja templates, hand-written CSS (no framework), vanilla JS
- **Auth:** Session-based login, passwords hashed with Werkzeug (`generate_password_hash`)

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python seed_admin.py            # creates your first coach/admin login
python app.py                   # runs at http://127.0.0.1:5000
```

A `.env` file is already included with a randomly generated `SECRET_KEY` for
local development — Flask loads it automatically via `python-dotenv`. You
don't need to do anything for local use.

If you ever deploy this publicly, generate a **new** key (don't reuse the
one in this zip) and set it as an environment variable on your host instead
of committing a `.env` file:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
`.env` is already gitignored, so it won't get pushed to GitHub. `.env.example`
shows what variables the app expects, for anyone cloning the repo.

Visit the site at `/`, and the admin dashboard at `/admin/login` using the
credentials you set with `seed_admin.py`.

## Project structure

```
stroke-o-clock/
  app.py                  # routes, validation, admin auth
  models.py                # Player, AdminUser, ContactMessage tables
  seed_admin.py             # interactive script to create the first admin login
  requirements.txt
  static/
    css/style.css          # full design system (tokens, components)
    js/main.js              # nav toggle, confirm dialogs, light form UX
  templates/
    base.html               # public site layout (nav + footer)
    home.html, about.html, what-we-do.html, help-us.html,
    gallery.html, contact.html, join.html, join-confirmation.html
    admin/
      _admin_base.html      # admin layout
      login.html, dashboard.html, player_detail.html, edit_player.html
  instance/                 # SQLite db lives here at runtime (gitignored)
```

## What's implemented

- **All public pages** from the site map (Home, About, What We Do, Help Us,
  Gallery, Contact), built from the actual program content in the project plan.
- **Registration form** (`/join`) with full server-side validation (required
  fields, email/phone format, date-of-birth sanity check) — validation runs
  even if JavaScript is disabled.
- **SQLite database** storing every submission, matching the Players table
  spec in the plan, plus an `application_status` field (Pending / Accepted /
  Rejected / Waitlisted).
- **Admin dashboard** (`/admin`) — password-protected, filter by status,
  view full player detail (including emergency/medical info, clearly marked
  as sensitive), update status, edit, or delete a registration.
- **Contact form** stores messages to the database and surfaces the latest
  five on the admin dashboard.

## Security notes (please read before deploying)

- A working `SECRET_KEY` is included in `.env` for local dev only. **Generate
  a fresh one and set it as a real environment variable before deploying
  anywhere public** — never reuse a key that's ever been in a zip file or
  git history.
- Admin passwords are hashed, never stored in plain text.
- Medical/allergy/emergency fields are only ever rendered on
  admin-authenticated pages, never on any public page.
- Before production: serve over HTTPS only, and consider encrypting the
  medical/allergy columns at rest if you move off SQLite.

## What's next (Phase 4–5, not built yet)

- Real photo/video uploads for the Gallery page (currently placeholder tiles)
- Announcements/events editable from the admin dashboard instead of hardcoded in `app.py`
- Player/parent accounts, attendance tracking, training resources
- Merchandise store and online payments/donations
- Migrating from SQLite to Postgres for production (SQLAlchemy makes this a
  one-line config change since no raw SQL is used anywhere)
