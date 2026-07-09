# Stroke O Clock — AAU Basketball Website

Full-stack site for Stroke O Clock AAU Basketball: public pages, a player
registration form, and a coach/admin dashboard for managing applications.


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

