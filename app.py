from datetime import date, datetime
from html import escape
from pathlib import Path
import base64

import streamlit as st

import auth
import database as db
import storage

# ==========================================
# CERTIFICATE VAULT — RITESH KUMAR SINGH
# Founder & CEO | Data Science | AI
# ==========================================

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

CATEGORIES = [
    "AI & Machine Learning",
    "Data Science & Analytics",
    "Programming & Software Development",
    "Hackathon",
    "Quiz Competition",
    "Coding Competition",
    "Workshop",
    "Webinar & Seminar",
    "Bootcamp & Training",
    "Internship",
    "Job Simulation",
    "Course Completion",
    "Academic Achievement",
    "Award & Recognition",
    "Volunteering & Leadership",
    "Other"
]


def find_photo():
    """Return the profile photo path if one exists in assets/."""
    for name in (
        "ritesh_profile.jpeg",
        "ritesh_profile.jpg",
        "ritesh_profile.png",
        "ritesh_profile.webp",
    ):
        candidate = ASSETS / name
        if candidate.exists():
            return candidate
    return None


PHOTO_PATH = find_photo()

st.set_page_config(
    page_title="Certificate Vault | Ritesh Kumar Singh",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state
st.session_state.setdefault("page", "Home")
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("flash", None)

# ==========================================
# STYLES
# ==========================================

st.markdown(
    f"<style>{(ROOT / 'styles.css').read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)


# ==========================================
# HELPERS
# ==========================================

def html(markup):
    """
    Render raw HTML safely through st.markdown.

    Markdown treats lines indented by 4+ spaces (or HTML followed by blank
    lines) as a code block, which is what printed "</section>" on the Home
    page. Stripping every line to a single compact string avoids that.
    """
    compact = "".join(line.strip() for line in markup.splitlines())
    st.markdown(compact, unsafe_allow_html=True)


def navigate(page):
    st.session_state.page = page
    st.rerun()


def flash(message, kind="success"):
    st.session_state.flash = (kind, message)


def show_flash():
    item = st.session_state.get("flash")
    if item:
        kind, message = item
        getattr(st, kind, st.info)(message)
        st.session_state.flash = None


def profile_photo_html():
    if PHOTO_PATH is None:
        return (
            '<div class="hero-photo" style="height:200px;display:flex;'
            'align-items:center;justify-content:center;font-size:70px">'
            "👨‍💻</div>"
        )

    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }[PHOTO_PATH.suffix.lower()]
    data = base64.b64encode(PHOTO_PATH.read_bytes()).decode("utf-8")
    return (
        '<div class="hero-photo">'
        f'<img src="data:{mime};base64,{data}" '
        'alt="Ritesh Kumar Singh profile photo">'
        "</div>"
    )


def valid_url(url):
    url = (url or "").strip()
    return url == "" or url.lower().startswith(("http://", "https://"))


def load_file(cert):
    """Return (bytes, filename, mime) for a certificate, or None."""
    blob = db.get_certificate_blob(cert["id"])
    if blob:
        return blob
    legacy = storage.get_certificate_file(cert.get("file_path", ""))  # older records
    if legacy is not None:
        mime = storage.MIME_TYPES.get(legacy.suffix.lower(), "application/octet-stream")
        return legacy.read_bytes(), legacy.name, mime
    return None


@st.cache_data(show_spinner=False, max_entries=64)
def pdf_to_images(pdf_bytes, max_pages=3):
    """Render the first PDF pages to PNG bytes so they display as real images."""
    try:
        import pymupdf
    except ImportError:
        return []
    pages = []
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        for index in range(min(len(doc), max_pages)):
            pix = doc[index].get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6))
            pages.append(pix.tobytes("png"))
    return pages


def render_file(cert, key, preview=True):
    """Show the real certificate: image preview, rendered PDF pages, and download."""
    if not (cert.get("has_blob") or cert.get("file_path")):
        st.caption("📎 No certificate file attached.")
        return
    loaded = load_file(cert)
    if loaded is None:
        st.warning(
            "Certificate file is missing from storage. "
            "Open Admin Studio → Manage → Replace file to upload it again."
        )
        return

    data, name, mime = loaded
    if preview:
        if mime == "application/pdf":
            pages = pdf_to_images(data)
            if pages:
                for number, page_png in enumerate(pages, start=1):
                    st.image(page_png, width="stretch")
            else:
                st.info("PDF preview unavailable — use the download button.")
        else:
            st.image(data, width="stretch")
    st.download_button(
        "⬇️ Download certificate",
        data=data,
        file_name=name,
        mime=mime or "application/octet-stream",
        key=f"dl_{key}",
    )


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.markdown("## 🏆 Certificate Vault")
    st.caption("PERSONAL ACHIEVEMENT PORTFOLIO")

    st.divider()

    st.markdown("### Ritesh Kumar Singh")
    st.caption("Founder & CEO")
    st.caption("Data Science · AI · Technology")

    st.divider()

    navigation = [
        ("🏠  Home", "Home"),
        ("🏆  Certificates", "Certificates"),
        ("👤  About Owner", "About"),
        ("⚙️  Admin Studio", "Admin"),
    ]

    for label, page_name in navigation:
        if st.button(
            label,
            key=f"nav_{page_name}",
            width="stretch",
            type="primary" if st.session_state.page == page_name else "secondary",
        ):
            navigate(page_name)

    if auth.is_authenticated():
        st.divider()
        st.success("Admin signed in")
        if st.button("🚪  Sign out", key="nav_logout", width="stretch"):
            auth.logout()
            flash("You have been signed out.", "info")
            navigate("Home")

    st.divider()
    st.caption("Built with Python & Streamlit")
    st.caption("© Ritesh Kumar Singh")


# ==========================================
# HOME PAGE
# ==========================================

page = st.session_state.page

if page == "Home":
    show_flash()
    stats = db.get_dashboard_stats()

    html(
        f"""
        <section class="hero">
            <div class="hero-copy">
                <div class="eyebrow">MY LEARNING JOURNEY · MY ACHIEVEMENTS</div>
                <h1>Knowledge Earned.<br>Potential Unlocked.</h1>
                <p>Welcome to my personal Certificate Vault — a central portfolio
                for my certifications, technical skills, learning milestones,
                and professional growth.</p>
                <div class="owner-pill">✦ Ritesh Kumar Singh &nbsp; | &nbsp; Founder &amp; CEO</div>
            </div>
            {profile_photo_html()}
        </section>
        """
    )

    html(
        '<div class="section-title">Portfolio at a Glance</div>'
        '<div class="section-subtitle">'
        "A professional home for my learning achievements."
        "</div>"
    )

    c1, c2, c3 = st.columns(3)
    metrics = [
        (c1, "PUBLISHED CERTIFICATES", str(stats["published"])),
        (c2, "SKILL CATEGORIES", str(stats["categories"])),
        (c3, "PORTFOLIO FOCUS", "AI + DATA"),
    ]
    for col, label, value in metrics:
        with col:
            html(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """
            )

    html(
        '<div class="section-title">Explore Your Portfolio</div>'
        '<div class="section-subtitle">Choose a section to continue.</div>'
    )

    a, b, c = st.columns(3)
    features = [
        (a, "🏆", "Certificate Library",
         "Browse published certificates, skills, and credentials."),
        (b, "🧭", "Learning Journey",
         "Present your progress and technical interests professionally."),
        (c, "🔐", "Owner Control Center",
         "Manage certificate records through the private admin area."),
    ]
    for col, icon, title, description in features:
        with col:
            html(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """
            )

    st.write("")
    x, y = st.columns(2)
    with x:
        if st.button("Explore Certificates  →", type="primary", width="stretch"):
            navigate("Certificates")
    with y:
        if st.button("Meet the Owner  →", width="stretch"):
            navigate("About")


# ==========================================
# CERTIFICATE LIBRARY (PUBLIC)
# ==========================================

elif page == "Certificates":
    st.title("🏆 Certificate Library")
    st.caption("Search and explore certificates published by the owner.")

    f1, f2 = st.columns([2, 1])
    with f1:
        search = st.text_input(
            "🔎 Search certificates",
            placeholder="Search by title, issuer, or skill...",
        )
    with f2:
        category = st.selectbox("Filter by category", ["All Categories"] + CATEGORIES)

    certificates = db.get_certificates(
        published_only=True, category=category, search=search
    )

    if not certificates:
        st.info(
            "No published certificates found. "
            "Add and publish certificates from the Admin Studio."
        )
    else:
        st.caption(f"Showing {len(certificates)} certificate(s)")
        for cert in certificates:
            with st.container(border=True):
                left, right = st.columns([2, 3], gap="large")
                with left:
                    st.subheader(cert["title"])
                    st.markdown(
                        f"**Issuer:** {cert['issuer']}  \n"
                        f"**Category:** {cert['category']}"
                        + (f"  \n**Issued:** {cert['issue_date']}" if cert["issue_date"] else "")
                        + (f"  \n**Credential ID:** `{cert['credential_id']}`" if cert["credential_id"] else "")
                    )
                    if cert["description"]:
                        st.write(cert["description"])
                    if cert["skills"]:
                        badges = "".join(
                            f'<span class="badge">{escape(s.strip())}</span>'
                            for s in cert["skills"].split(",")
                            if s.strip()
                        )
                        html(badges)
                    if cert["verification_url"] and valid_url(cert["verification_url"]):
                        st.link_button("🔗 Verify credential", cert["verification_url"])
                with right:
                    render_file(cert, f"pub_{cert['id']}")


# ==========================================
# ABOUT OWNER PAGE
# ==========================================

elif page == "About":
    st.title("👤 About the Owner")

    left, right = st.columns([1, 2], gap="large")

    with left:
        if PHOTO_PATH is not None:
            st.image(str(PHOTO_PATH), caption="Ritesh Kumar Singh", width="stretch")
        else:
            st.info("Add your photo at assets/ritesh_profile.jpeg")

    with right:
        html('<div class="eyebrow">OWNER · FOUNDER · CEO</div>')
        st.header("Ritesh Kumar Singh")
        st.write(
            "Data Science Student | Python | Machine Learning | "
            "Artificial Intelligence"
        )

        st.markdown("### My Mission")
        st.write(
            "To continuously learn, build practical projects, "
            "develop industry-relevant skills, and document my "
            "professional growth."
        )

        st.markdown("### Areas of Interest")
        st.markdown(
            "- Data Science and Data Analytics\n"
            "- Python Programming and SQL\n"
            "- Machine Learning and Artificial Intelligence\n"
            "- Building practical technology projects"
        )

        html('<div class="owner-pill">✦ Founder &amp; CEO — Certificate Vault</div>')


# ==========================================
# ADMIN STUDIO (LOGIN + MANAGEMENT)
# ==========================================

elif page in ("Admin", "Login"):
    st.title("⚙️ Admin Studio")
    st.caption("Private workspace for the portfolio owner.")

    # ---------- Login gate ----------
    if not auth.is_authenticated():
        if not auth.credentials_configured():
            st.error(
                "Admin credentials are not configured. Create "
                "`.streamlit/secrets.toml` (locally) or add the same text under "
                "**Settings → Secrets** (Streamlit Cloud):"
            )
            st.code(
                '[admin]\nemail = "your-email@example.com"\n'
                'password = "choose-a-strong-password"',
                language="toml",
            )
            st.stop()

        show_flash()
        st.subheader("🔐 Owner Sign In")
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            with st.form("login_form"):
                email = st.text_input("Email", autocomplete="username")
                password = st.text_input(
                    "Password", type="password", autocomplete="current-password"
                )
                submitted = st.form_submit_button(
                    "Sign In", type="primary", width="stretch"
                )
            if submitted:
                ok, message = auth.login(email, password)
                if ok:
                    flash(message, "success")
                    navigate("Admin")
                else:
                    st.error(message)
        st.stop()

    # ---------- Authenticated area ----------
    show_flash()
    stats = db.get_dashboard_stats()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", stats["total"])
    m2.metric("Published", stats["published"])
    m3.metric("Drafts", stats["drafts"])
    m4.metric("Categories", stats["categories"])

    tab_add, tab_manage = st.tabs(["➕ Add Certificate", "🗂️ Manage Certificates"])

    # ----- Add -----
    with tab_add:
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            title = c1.text_input("Title *")
            issuer = c2.text_input("Issuer *")
            category = c1.selectbox("Category", CATEGORIES, index=len(CATEGORIES) - 1)
            issue_date = c2.date_input("Issue date", value=date.today())
            credential_id = c1.text_input("Credential ID")
            verification_url = c2.text_input("Verification URL (https://...)")
            skills = st.text_input("Skills (comma separated)")
            description = st.text_area("Description")
            upload = st.file_uploader(
                "Certificate file (PDF, PNG, JPG, JPEG, WEBP — max 10 MB)",
                type=["pdf", "png", "jpg", "jpeg", "webp"],
            )
            publish = st.checkbox("Publish immediately", value=True)
            add_clicked = st.form_submit_button("Save Certificate", type="primary")

        if add_clicked:
            if not title.strip() or not issuer.strip():
                st.error("Title and issuer are required.")
            elif not valid_url(verification_url):
                st.error("Verification URL must start with http:// or https://")
            else:
                try:
                    file_data, file_name, file_mime = (None, "", "")
                    if upload is not None:
                        file_data, file_name, file_mime = storage.prepare_upload(upload)
                    new_id = db.add_certificate(
                        title=title,
                        issuer=issuer,
                        category=category,
                        issue_date=issue_date.isoformat() if issue_date else "",
                        credential_id=credential_id.strip(),
                        verification_url=verification_url.strip(),
                        description=description.strip(),
                        skills=skills.strip(),
                        published=publish,
                        file_data=file_data,
                        file_name=file_name,
                        file_mime=file_mime,
                    )
                    flash(f"Certificate #{new_id} saved.", "success")
                    st.rerun()
                except storage.StorageError as exc:
                    st.error(str(exc))
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Could not save certificate: {exc}")

    # ----- Manage -----
    with tab_manage:
        certificates = db.get_certificates()
        if not certificates:
            st.info("No certificates yet. Add your first one in the previous tab.")

        for cert in certificates:
            cid = cert["id"]
            status = "✅ Published" if cert["published"] else "📝 Draft"
            with st.expander(f"{status}  ·  {cert['title']}  —  {cert['issuer']}"):
                with st.form(f"edit_{cid}"):
                    c1, c2 = st.columns(2)
                    e_title = c1.text_input("Title *", cert["title"])
                    e_issuer = c2.text_input("Issuer *", cert["issuer"])
                    cat_options = CATEGORIES if cert["category"] in CATEGORIES else CATEGORIES + [cert["category"]]
                    e_category = c1.selectbox(
                        "Category", cat_options, index=cat_options.index(cert["category"])
                    )
                    try:
                        current_date = datetime.strptime(cert["issue_date"], "%Y-%m-%d").date()
                    except (ValueError, TypeError):
                        current_date = date.today()
                    e_date = c2.date_input("Issue date", value=current_date)
                    e_cred = c1.text_input("Credential ID", cert["credential_id"])
                    e_url = c2.text_input("Verification URL", cert["verification_url"])
                    e_skills = st.text_input("Skills (comma separated)", cert["skills"])
                    e_desc = st.text_area("Description", cert["description"])
                    e_file = st.file_uploader(
                        "Replace certificate file (optional)",
                        type=["pdf", "png", "jpg", "jpeg", "webp"],
                        key=f"file_{cid}",
                    )
                    e_pub = st.checkbox("Published", value=bool(cert["published"]))
                    save_clicked = st.form_submit_button("Save Changes", type="primary")

                if cert.get("has_blob") or cert.get("file_path"):
                    loaded = load_file(cert)
                    if loaded is None:
                        st.warning("Attached file is missing — upload it again with 'Replace file'.")
                    else:
                        st.caption(f"Current file: {loaded[1]}")
                        if loaded[2] != "application/pdf":
                            st.image(loaded[0], width=260)
                else:
                    st.caption("No file attached.")

                if save_clicked:
                    if not e_title.strip() or not e_issuer.strip():
                        st.error("Title and issuer are required.")
                    elif not valid_url(e_url):
                        st.error("Verification URL must start with http:// or https://")
                    else:
                        try:
                            fields = dict(
                                title=e_title,
                                issuer=e_issuer,
                                category=e_category,
                                issue_date=e_date.isoformat(),
                                credential_id=e_cred.strip(),
                                verification_url=e_url.strip(),
                                description=e_desc.strip(),
                                skills=e_skills.strip(),
                                published=e_pub,
                            )
                            if e_file is not None:
                                data, fname, fmime = storage.prepare_upload(e_file)
                                fields.update(file_data=data, file_name=fname, file_mime=fmime)
                            db.update_certificate(cid, **fields)
                            flash("Certificate updated.", "success")
                            st.rerun()
                        except storage.StorageError as exc:
                            st.error(str(exc))
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"Could not update certificate: {exc}")

                d1, d2, d3 = st.columns([1, 1, 2])
                toggle_label = "Unpublish" if cert["published"] else "Publish"
                if d1.button(toggle_label, key=f"toggle_{cid}", width="stretch"):
                    db.set_published(cid, not cert["published"])
                    flash("Certificate unpublished." if cert["published"] else "Certificate published.", "success")
                    st.rerun()

                confirm = d3.checkbox("Confirm delete", key=f"confirm_{cid}")
                if d2.button("🗑️ Delete", key=f"delete_{cid}", width="stretch"):
                    if confirm:
                        db.delete_certificate(cid)
                        if cert["file_path"]:
                            storage.delete_certificate_file(cert["file_path"])
                        flash("Certificate deleted.", "success")
                        st.rerun()
                    else:
                        st.warning("Tick 'Confirm delete' first.")


# ==========================================
# FOOTER
# ==========================================

html(
    """
    <div class="footer">
        © 2026 Ritesh Kumar Singh · Founder &amp; CEO<br>
        Certificate Vault · Built with Python &amp; Streamlit<br>
        Learn. Build. Verify. Grow.
    </div>
    """
)
