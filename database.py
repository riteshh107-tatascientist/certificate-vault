
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


def initialize_database():
    """Create the database and required tables."""
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
                # Check existing database columns
        existing = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(certificates)"
            )
        }

        # Add missing columns to older databases
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

        # Migrate older databases: store the certificate file inside the DB.
        existing = {row[1] for row in connection.execute("PRAGMA table_info(certificates)")}
        for column, ddl in (
            ("file_data", "BLOB"),
            ("file_name", "TEXT DEFAULT ''"),
            ("file_mime", "TEXT DEFAULT ''"),
        ):
            if column not in existing:
                connection.execute(f"ALTER TABLE certificates ADD COLUMN {column} {ddl}")

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_certificates_published
            ON certificates(published)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_certificates_category
            ON certificates(category)
        """)


@contextmanager
def get_connection():
    """Provide a database connection and manage transactions."""
    connection = sqlite3.connect(
        str(DB_PATH),
        timeout=30,
    )
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


LIST_COLUMNS = (
    "id, title, issuer, category, issue_date, credential_id, verification_url, "
    "description, skills, file_path, published, created_at, updated_at, "
    "file_name, file_mime, (file_data IS NOT NULL AND LENGTH(file_data) > 0) AS has_blob"
)


def get_certificate_blob(certificate_id):
    """Return (bytes, filename, mime) stored in the database, or None."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT file_data, file_name, file_mime FROM certificates WHERE id = ?",
            (certificate_id,),
        ).fetchone()
    if row and row["file_data"]:
        return bytes(row["file_data"]), row["file_name"] or "certificate", row["file_mime"] or ""
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
    """Insert a certificate and return its new ID."""
    title = title.strip()
    issuer = issuer.strip()

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
                int(published),
                file_data,
                file_name,
                file_mime,
            ),
        )

        return cursor.lastrowid


def get_certificate(certificate_id):
    """Return one certificate or None."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM certificates WHERE id = ?",
            (certificate_id,),
        ).fetchone()

        return dict(row) if row else None


def get_certificates(
    published_only=False,
    category=None,
    search=None,
):
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
        search_term = f"%{search.strip()}%"
        parameters.extend([search_term] * 4)

    query += " ORDER BY created_at DESC, id DESC"

    with get_connection() as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        return [dict(row) for row in rows]


def update_certificate(certificate_id, **fields):
    """Update supported fields for an existing certificate."""
    allowed_fields = {
        "title",
        "issuer",
        "category",
        "issue_date",
        "credential_id",
        "verification_url",
        "description",
        "skills",
        "file_path",
        "published",
        "file_data",
        "file_name",
        "file_mime",
    }

    updates = {
        key: value
        for key, value in fields.items()
        if key in allowed_fields
    }

    if not updates:
        raise ValueError("No valid fields supplied for update.")

    if "title" in updates:
        updates["title"] = str(updates["title"]).strip()
        if not updates["title"]:
            raise ValueError("Certificate title cannot be empty.")

    if "issuer" in updates:
        updates["issuer"] = str(updates["issuer"]).strip()
        if not updates["issuer"]:
            raise ValueError("Certificate issuer cannot be empty.")

    if "published" in updates:
        updates["published"] = int(bool(updates["published"]))

    assignments = ", ".join(
        f"{field} = ?" for field in updates
    )

    values = list(updates.values())
    values.append(certificate_id)

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
    """Return counts for the dashboard."""
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


# Create database tables when this module is imported.
initialize_database()
