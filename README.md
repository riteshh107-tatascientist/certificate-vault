# Certificate Vault — Ritesh Kumar Singh

A Streamlit certificate portfolio with an owner-only admin area and a public read-only gallery.

## Features
- Branded homepage: Ritesh Kumar Singh — Founder & CEO
- Public certificate gallery with search and category filter
- Admin login, add, edit, replace, publish/unpublish, and delete
- SQLite metadata database and local file storage
- Upload validation for PDF, PNG, JPG/JPEG (15 MB max)
- Credential verification links, when provided

## Requirements
- Python 3.10+
- Streamlit

## Run locally
1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml`.
   Rename it to `secrets.toml` and set your own email/password.
4. Start the app:
   ```bash
   streamlit run app.py
   ```

## Files
- `app.py` — user interface, public gallery and admin pages
- `database.py` — SQLite metadata CRUD
- `storage.py` — local certificate file handling

## Important deployment/security notes
This is a local-first starter application. SQLite and `certificate_files/` are stored on the machine's filesystem. Streamlit Community Cloud's local filesystem is not a reliable persistent storage solution, so do not deploy this version as a permanent cloud vault without replacing local persistence with managed storage (for example, Supabase Storage + PostgreSQL).

The basic email/password check in this starter app is not a substitute for a production authentication provider. The current code controls which UI is shown but does not provide robust multi-user identity or server-side database authorization. For a public production deployment, use Supabase Auth and Row Level Security policies so only the authenticated owner can write, while anonymous visitors can read published metadata/files only. Keep private files in a private bucket and use authenticated/signed access.

Never commit `.streamlit/secrets.toml`, real credentials, certificate files, or the local database to a public repository. Do not upload certificates containing sensitive personal information to a public portfolio.
