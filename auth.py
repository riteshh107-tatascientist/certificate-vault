"""Owner authentication for Certificate Vault."""
import hashlib
import hmac
import os
import time

import streamlit as st

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 60


def _read_credentials():
    """Read admin credentials from Streamlit secrets or environment variables."""
    email = password = password_hash = ""
    try:
        section = st.secrets.get("admin", {})
        email = str(section.get("email", ""))
        password = str(section.get("password", ""))
        password_hash = str(section.get("password_sha256", ""))
    except Exception:
        pass  # no secrets file present

    email = email or os.environ.get("ADMIN_EMAIL", "")
    password = password or os.environ.get("ADMIN_PASSWORD", "")
    password_hash = password_hash or os.environ.get("ADMIN_PASSWORD_SHA256", "")
    return email.strip(), password, password_hash.strip().lower()


def credentials_configured():
    email, password, password_hash = _read_credentials()
    return bool(email and (password or password_hash))


def _check(email_in, password_in):
    email, password, password_hash = _read_credentials()
    if not email:
        return False

    email_ok = hmac.compare_digest(
        email_in.strip().lower().encode(), email.lower().encode()
    )
    if password_hash:
        supplied = hashlib.sha256(password_in.encode()).hexdigest()
        pass_ok = hmac.compare_digest(supplied.encode(), password_hash.encode())
    else:
        pass_ok = bool(password) and hmac.compare_digest(
            password_in.encode(), password.encode()
        )
    return email_ok and pass_ok


def is_authenticated():
    return bool(st.session_state.get("authenticated", False))


def login(email_in, password_in):
    """Return (success, message)."""
    now = time.time()
    locked_until = st.session_state.get("locked_until", 0)
    if now < locked_until:
        wait = int(locked_until - now) + 1
        return False, f"Too many failed attempts. Try again in {wait} seconds."

    if _check(email_in, password_in):
        st.session_state.authenticated = True
        st.session_state.failed_attempts = 0
        return True, "Signed in successfully."

    attempts = st.session_state.get("failed_attempts", 0) + 1
    st.session_state.failed_attempts = attempts
    if attempts >= MAX_ATTEMPTS:
        st.session_state.locked_until = now + LOCKOUT_SECONDS
        st.session_state.failed_attempts = 0
        return False, "Too many failed attempts. Locked for 60 seconds."
    return False, f"Incorrect email or password. ({MAX_ATTEMPTS - attempts} attempts left)"


def logout():
    st.session_state.authenticated = False
