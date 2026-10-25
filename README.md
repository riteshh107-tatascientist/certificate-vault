# Certificate Vault — Ritesh Kumar Singh

A Streamlit certificate portfolio with a public gallery and a password-protected admin area.

## Features
- Branded homepage with live counters (published certificates, categories)
- Public gallery with search and category filter
- Admin login (email + password, 5-attempt lockout)
- Add, edit, replace file, publish/unpublish, delete (with confirmation)
- SQLite database; certificate files are stored inside the database record
- PDF certificates are previewed as real page images (PyMuPDF) plus a download button
- Upload validation: PDF, PNG, JPG/JPEG, WEBP, 10 MB max, file-signature check

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate     Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Admin login
Credentials are read from `.streamlit/secrets.toml`:
```toml
[admin]
email = "your-email@example.com"
password = "choose-a-strong-password"
```
A temporary file is included (`admin@certvault.local` / `ChangeMe@2026`) — **change it**.
Optional: store a SHA-256 hash instead of the plain password with `password_sha256 = "..."`.

### Streamlit Community Cloud
App → Settings → **Secrets** → paste the `[admin]` block above. The local
`secrets.toml` is not uploaded (it is in `.gitignore`).

## Profile photo
Put your photo at `assets/ritesh_profile.jpeg` (`.jpg`, `.png`, `.webp` also work).

## Files
- `app.py` — pages: Home, Certificates, About, Admin
- `auth.py` — login, lockout, logout
- `database.py` — SQLite CRUD
- `storage.py` — validated file storage
- `styles.css` — theme

## Important deployment note
SQLite and `uploads/` live on the local filesystem. Streamlit Community Cloud storage
is **not persistent** — certificates added there can disappear when the app restarts.
For a permanent online vault, use managed storage (e.g. Supabase Storage + PostgreSQL),
or host on a server/VPS with a persistent disk. Never commit `secrets.toml`, the
database, or private certificates to a public repo.
