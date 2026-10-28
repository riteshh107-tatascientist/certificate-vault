
from pathlib import Path
import sqlite3
from contextlib import contextmanager

# ==========================================
# CERTIFICATE VAULT — DATABASE ENGINE
# Owner: Ritesh Kumar Singh
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "certificates.db"


@contextmanager
def get_connection():
    """Open a database connection and manage transactions."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DB_PATH), timeout=30)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    """Create tables and safely migrate older databases."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                issuer TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Other',
                issue_date TEXT DEFAULT '',
                credential_id TEXT DEFAULT '',
                verification_url TEXT DEFAULT '',
                description TEXT DEFAULT '',
                skills TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                published INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add missing columns to existing databases.
        existing = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(certificates)"
            )
        }

        migrations = {
            "file_data": "BLOB",
            "file_name": "TEXT DEFAULT ''",
            "file_mime": "TEXT DEFAULT ''",
        }

        for column, definition in migrations.items():
            if column not in existing:
                connection.execute(
                    f"ALTER TABLE certificates "
                    f"ADD COLUMN {column} {definition}"
                )
                existing.add(column)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_certificates_published
            ON certificates(published)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_certificates_category
            ON certificates(category)
        """)


LIST_COLUMNS = (
    "id, title, issuer, category, issue_date, credential_id, "
    "verification_url, description, skills, file_path, published, "
    "created_at, updated_at, file_name, file_mime, "
    "(file_data IS NOT NULL AND LENGTH(file_data) > 0) AS has_blob"
)


def get_certificate_blob(certificate_id):
    """Return certificate bytes, filename and MIME type, or None."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT file_data, file_name, file_mime
            FROM certificates
            WHERE id = ?
            """,
            (certificate_id,),
        ).fetchone()

    if row and row["file_data"]:
        return (
            bytes(row["file_data"]),
            row["file_name"] or "certificate",
            row["file_mime"] or "",
        )

    return None


def add_certificate(
    title,
    issuer,
    category="Other",
    issue_date="",
    credential_id="",
    verification_url="",
    description="",
    skills="",
    file_path="",
    published=False,
    file_data=None,
    file_name="",
    file_mime="",
):
    """Insert a certificate and return its ID."""
    title = str(title or "").strip()
    issuer = str(issuer or "").strip()

    if not title:
        raise ValueError("Certificate title is required.")

    if not issuer:
        raise ValueError("Certificate issuer is required.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO certificates (
                title, issuer, category, issue_date,
                credential_id, verification_url,
                description, skills, file_path, published,
                file_data, file_name, file_mime
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                issuer,
                category,
                issue_date,
                credential_id,
                verification_url,
                description,
                skills,
                file_path,
                int(bool(published)),
                file_data,
                file_name,
                file_mime,
            ),
        )

        return cursor.lastrowid


def get_certificate(certificate_id):
    """Return one certificate as a dictionary, or None."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM certificates WHERE id = ?",
            (certificate_id,),
        ).fetchone()

    return dict(row) if row else None


def get_certificates(published_only=False, category=None, search=None):
    """Return certificates with optional filters."""
    query = f"SELECT {LIST_COLUMNS} FROM certificates WHERE 1=1"
    parameters = []

    if published_only:
        query += " AND published = 1"

    if category and category != "All Categories":
        query += " AND category = ?"
        parameters.append(category)

    if search and search.strip():
        query += """
            AND (
                title LIKE ?
                OR issuer LIKE ?
                OR skills LIKE ?
                OR description LIKE ?
            )
        """
        term = f"%{search.strip()}%"
        parameters.extend([term] * 4)

    query += " ORDER BY created_at DESC, id DESC"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    return [dict(row) for row in rows]


def update_certificate(certificate_id, **fields):
    """Update supported fields for a certificate."""
    allowed_fields = {
        "title", "issuer", "category", "issue_date",
        "credential_id", "verification_url", "description",
        "skills", "file_path", "published", "file_data",
        "file_name", "file_mime",
    }

    updates = {
        key: value
        for key, value in fields.items()
        if key in allowed_fields
    }

    if not updates:
        raise ValueError("No valid fields supplied for update.")

    for field in ("title", "issuer"):
        if field in updates:
            updates[field] = str(updates[field] or "").strip()
            if not updates[field]:
                raise ValueError(
                    f"{field.capitalize()} cannot be empty."
                )

    if "published" in updates:
        updates["published"] = int(bool(updates["published"]))

    assignments = ", ".join(
        f"{field} = ?" for field in updates
    )
    values = list(updates.values()) + [certificate_id]

    with get_connection() as connection:
        cursor = connection.execute(
            f"""
            UPDATE certificates
            SET {assignments}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            values,
        )

    return cursor.rowcount > 0


def delete_certificate(certificate_id):
    """Delete a certificate record by ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM certificates WHERE id = ?",
            (certificate_id,),
        )

    return cursor.rowcount > 0


def set_published(certificate_id, published):
    """Publish or unpublish a certificate."""
    return update_certificate(
        certificate_id,
        published=published,
    )


def get_dashboard_stats():
    """Return dashboard counts."""
    with get_connection() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM certificates"
        ).fetchone()[0]

        published = connection.execute(
            "SELECT COUNT(*) FROM certificates WHERE published = 1"
        ).fetchone()[0]

        categories = connection.execute(
            """
            SELECT COUNT(DISTINCT category)
            FROM certificates
            WHERE published = 1
            """
        ).fetchone()[0]

    return {
        "total": total,
        "published": published,
        "categories": categories,
        "drafts": total - published,
    }


# Initialize and migrate the database when this module loads.
initialize_database()
