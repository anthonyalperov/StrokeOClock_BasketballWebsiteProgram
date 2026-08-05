# Stroke O Clock — AAU Basketball Website

Full-stack site for Stroke O Clock AAU Basketball: public pages, a player registration form, and a coach/admin dashboard for managing applications.

## Tech stack

- **Backend:** Flask + SQLAlchemy (`app.py`, `models.py`)
- **Database:** SQLite locally (`instance/stroke_o_clock.db`, created automatically) — **Postgres in production on Render** (see backup/restore section below)
- **Frontend:** Server-rendered Jinja templates, hand-written CSS (no framework), vanilla JS
- **Auth:** Session-based login, passwords hashed with Werkzeug (`generate_password_hash`)

## Setup

```
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
  backup-db.sh              # dumps production Postgres DB
  export-backup.sh          # gets the dump out of Render Shell
  restore-db.sh              # restores a dump into a database
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

## Database Backup & Restore (Production)

Render's free Postgres tier expires (typically after 30 days) and deletes all data
permanently. These scripts back up the database before that happens and restore it
into the next one.

### Files

- `backup-db.sh` — dumps the current database to `backup.dump`
- `export-backup.sh` — uploads `backup.dump` to a temporary public URL so you can
  download it from outside Render's Shell
- `restore-db.sh` — restores `backup.dump` into a database

### When to back up

Do this **before** the current database's expiration date (check Render dashboard →
your database → Info tab for the expiration date). Don't wait until the last day.

### How to back up

1. Open Render dashboard → your web service → **Shell** tab
2. Check tools are installed:
   ```
   which pg_dump
   ```
   If missing (Debian/Ubuntu base image):
   ```
   apt-get update && apt-get install -y postgresql-client
   ```
3. Run the backup:
   ```
   ./backup-db.sh
   ```
4. Get the file out of the Shell:
   ```
   ./export-backup.sh
   ```
5. Copy the printed URL, open it in a browser, and download `backup.dump` to your
   computer. The link is public — download it promptly, don't share it, and let it
   expire.

### How to restore into a new database

1. Create the new Postgres database in the Render dashboard
2. Copy its **Internal Connection String** and update the `DATABASE_URL` environment
   variable on your web service to point to it
3. Redeploy the web service so it picks up the new `DATABASE_URL`
4. Open the Shell tab again
5. Upload `backup.dump` into the Shell session (drag-and-drop into the terminal panel)
6. Run:
   ```
   ./restore-db.sh
   ```
7. Confirm the site is reading data correctly (check the admin dashboard or a public
   page that pulls from the database)

### Notes

- `backup.dump` is gitignored — never commit it. It can contain admin credentials
  and contact form submissions.
- The `export-backup.sh` link is temporary and unauthenticated. Anyone with the link
  can download it until it expires, so treat it like a password: don't post it
  anywhere, don't leave the tab open longer than needed.
- Longer-term fix: Render's free Postgres expiration is the root cause of this
  entire workflow. Migrating to a host with a permanent free tier (Neon, Supabase)
  would remove the need to do this on a recurring basis.