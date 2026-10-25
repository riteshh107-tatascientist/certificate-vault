
from pathlib import Path
import base64
import streamlit as st

# ==========================================
# CERTIFICATE VAULT — RITESH KUMAR SINGH
# Founder & CEO | Data Science | AI
# ==========================================

ROOT = Path(__file__).resolve().parent
PHOTO_PATH = ROOT / "assets" / "ritesh_profile.jpeg"

st.set_page_config(
    page_title="Certificate Vault | Ritesh Kumar Singh",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# ==========================================
# PREMIUM UI DESIGN
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');

:root {
    --bg: #07111f;
    --panel: #102139;
    --line: #29415e;
    --cyan: #67e8f9;
    --blue: #60a5fa;
    --muted: #a8bad0;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #142d50 0%, transparent 35%),
        radial-gradient(ellipse at 95% 15%, #0c3342 0%, transparent 30%),
        var(--bg);
    color: #f5f8ff;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b192b, #07111f);
    border-right: 1px solid var(--line);
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -0.035em;
}

.hero {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(200px, 0.5fr);
    gap: 30px;
    align-items: center;
    position: relative;
    overflow: hidden;
    padding: clamp(25px, 4vw, 52px);
    border-radius: 26px;
    border: 1px solid #294c68;
    background: linear-gradient(120deg, #122440, #102e40);
    box-shadow: 0 15px 55px #00000035;
    animation: fadeUp 0.7s ease;
}

.hero:before {
    content: "";
    position: absolute;
    width: 300px;
    height: 300px;
    right: 10%;
    top: -200px;
    border-radius: 50%;
    background: #22d3ee30;
    filter: blur(30px);
    animation: glow 5s ease-in-out infinite alternate;
}

.hero-copy, .hero-photo {
    position: relative;
    z-index: 1;
}

.eyebrow {
    color: var(--cyan);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.5px;
    text-transform: uppercase;
}

.hero h1 {
    font-size: clamp(34px, 4vw, 57px);
    line-height: 1.12;
    margin: 18px 0;
    color: #f7fbff;
}

.hero p {
    color: #c3d4e8;
    font-size: 16px;
    line-height: 1.8;
}

.owner-pill {
    display: inline-block;
    padding: 10px 15px;
    margin-top: 12px;
    border: 1px solid #3a7187;
    border-radius: 999px;
    color: #a5f3fc;
    background: #0891b218;
    font-size: 12px;
    font-weight: 700;
}

.hero-photo {
    justify-self: center;
    width: min(100%, 255px);
    padding: 6px;
    border-radius: 25px;
    background: linear-gradient(135deg, #67e8f9, #3b82f6, #a78bfa);
    background-size: 200% 200%;
    animation: borderFlow 5s ease infinite, floatPhoto 5s ease-in-out infinite;
    box-shadow: 0 0 30px #22d3ee30;
}

.hero-photo img {
    display: block;
    width: 100%;
    height: 290px;
    object-fit: cover;
    object-position: center 25%;
    border-radius: 20px;
}

.section-title {
    font-family: 'Manrope', sans-serif;
    font-size: 25px;
    font-weight: 800;
    margin-top: 32px;
    margin-bottom: 6px;
}

.section-subtitle {
    color: var(--muted);
    margin-bottom: 20px;
}

.metric-card, .feature-card {
    padding: 22px;
    border-radius: 17px;
    border: 1px solid var(--line);
    background: linear-gradient(145deg, #122740, #0b192b);
    transition: 0.25s ease;
    height: 100%;
}

.metric-card:hover, .feature-card:hover {
    transform: translateY(-4px);
    border-color: var(--cyan);
    box-shadow: 0 10px 28px #00000025, 0 0 18px #22d3ee10;
}

.metric-label {
    color: #afc2d9;
    font-size: 12px;
}

.metric-value {
    color: var(--cyan);
    font-size: 30px;
    font-weight: 800;
    margin-top: 12px;
}

.feature-icon {
    font-size: 25px;
    margin-bottom: 12px;
}

.feature-card h3 {
    font-size: 18px;
}

.feature-card p {
    color: var(--muted);
    line-height: 1.7;
    font-size: 13px;
}

.stButton > button {
    min-height: 44px;
    border-radius: 12px;
    font-weight: 700;
    border: 1px solid #365371;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    border-color: var(--cyan);
    box-shadow: 0 0 18px #22d3ee20;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #0891b2, #2563eb);
    border: none;
}

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border-radius: 11px;
}

.footer {
    border-top: 1px solid var(--line);
    margin-top: 45px;
    padding-top: 22px;
    text-align: center;
    color: #8ca2bc;
    font-size: 12px;
    line-height: 1.8;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes glow {
    from { transform: translateX(-15px); }
    to { transform: translateX(45px); }
}

@keyframes floatPhoto {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

@keyframes borderFlow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

@media (max-width: 750px) {
    .hero {
        grid-template-columns: 1fr;
    }

    .hero-photo {
        width: 210px;
    }

    .hero-photo img {
        height: 240px;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *:before, *:after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def navigate(page):
    st.session_state.page = page
    st.rerun()


def profile_photo_html():
    if not PHOTO_PATH.exists():
        return """
        <div class="hero-photo"
             style="height:200px;display:flex;align-items:center;
             justify-content:center;font-size:70px">
             👨‍💻
        </div>
        """

    image_data = base64.b64encode(
        PHOTO_PATH.read_bytes()
    ).decode("utf-8")

    return f"""
    <div class="hero-photo">
        <img src="data:image/jpeg;base64,{image_data}"
             alt="Ritesh Kumar Singh profile photo">
    </div>
    """


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
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.page == page_name
                else "secondary"
            ),
        ):
            navigate(page_name)

    st.divider()
    st.caption("Built with Python & Streamlit")
    st.caption("© Ritesh Kumar Singh")


# ==========================================
# HOME PAGE
# ==========================================

if st.session_state.page == "Home":

    st.markdown(
        f"""
        <section class="hero">
            <div class="hero-copy">
                <div class="eyebrow">
                    MY LEARNING JOURNEY · MY ACHIEVEMENTS
                </div>
                <h1>Knowledge Earned.<br>Potential Unlocked.</h1>
                <p>
                    Welcome to my personal Certificate Vault —
                    a central portfolio for my certifications,
                    technical skills, learning milestones,
                    and professional growth.
                </p>
                <div class="owner-pill">
                    ✦ Ritesh Kumar Singh &nbsp; | &nbsp; Founder & CEO
                </div>
            </div>
            {profile_photo_html()}
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Portfolio at a Glance</div>'
        '<div class="section-subtitle">'
        'A professional home for my learning achievements.'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    metrics = [
        (c1, "PUBLISHED CERTIFICATES", "0"),
        (c2, "SKILL CATEGORIES", "0"),
        (c3, "PORTFOLIO FOCUS", "AI + DATA"),
    ]

    for col, label, value in metrics:
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="section-title">Explore Your Portfolio</div>'
        '<div class="section-subtitle">'
        'Choose a section to continue.'
        '</div>',
        unsafe_allow_html=True,
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
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    x, y = st.columns(2)

    with x:
        if st.button(
            "Explore Certificates  →",
            type="primary",
            use_container_width=True,
        ):
            navigate("Certificates")

    with y:
        if st.button(
            "Meet the Owner  →",
            use_container_width=True,
        ):
            navigate("About")


# ==========================================
# CERTIFICATE PAGE — CONNECT DATABASE NEXT
# ==========================================

elif st.session_state.page == "Certificates":

    st.title("🏆 Certificate Library")
    st.caption(
        "Search and explore certificates published by the owner."
    )

    search = st.text_input(
        "🔎 Search certificates",
        placeholder="Search by title, issuer, or skill...",
    )

    category = st.selectbox(
        "Filter by category",
        [
            "All Categories",
            "Data Science",
            "Python",
            "Machine Learning",
            "Artificial Intelligence",
            "SQL",
            "Internship",
            "Other",
        ],
    )

    st.info(
        "Your certificate database will be connected in the next files. "
        "After setup, published certificates will appear here."
    )


# ==========================================
# ABOUT OWNER PAGE
# ==========================================

elif st.session_state.page == "About":

    st.title("👤 About the Owner")

    left, right = st.columns([1, 2], gap="large")

    with left:
        if PHOTO_PATH.exists():
            st.image(
                str(PHOTO_PATH),
                caption="Ritesh Kumar Singh",
                use_container_width=True,
            )
        else:
            st.info("Add your photo at assets/ritesh_profile.jpeg")

    with right:
        st.markdown(
            '<div class="eyebrow">OWNER · FOUNDER · CEO</div>',
            unsafe_allow_html=True,
        )

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

        st.markdown(
            '<div class="owner-pill">'
            '✦ Founder & CEO — Certificate Vault'
            '</div>',
            unsafe_allow_html=True,
        )


# ==========================================
# ADMIN PAGE — AUTHENTICATION COMES NEXT
# ==========================================

elif st.session_state.page == "Admin":

    st.title("⚙️ Admin Studio")
    st.caption("Private workspace for the portfolio owner.")

    if not st.session_state.authenticated:
        st.warning(
            "Admin login and protected certificate management "
            "will be connected in the upcoming files."
        )

        if st.button(
            "Go to Admin Login Setup  →",
            type="primary",
        ):
            navigate("Login")
    else:
        st.success("Admin session active.")


elif st.session_state.page == "Login":

    st.title("🔐 Owner Sign In")

    st.info(
        "Secure authentication will be implemented when we connect "
        "the configuration and database files."
    )

    if st.button("← Back to Home"):
        navigate("Home")


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="footer">
        © 2026 Ritesh Kumar Singh · Founder & CEO<br>
        Certificate Vault · Built with Python & Streamlit<br>
        Learn. Build. Verify. Grow.
    </div>
    """,
    unsafe_allow_html=True,
)
