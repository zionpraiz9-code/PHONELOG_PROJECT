#!/usr/bin/env python3
"""
Production-ready Flask app for flat-file address book.

Features:
- Flat-file storage: users.txt, contacts.txt (CSV-ish)
- Safe atomic writes and defensive parsing
- Seeding of initial users and 15+ contacts for owners: admin, praise, zion
- Routes: login, register, logout, dashboard, add/edit/delete, import/export
"""
from __future__ import annotations
import csv
import os
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file,
    Response,
)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.txt")
CONTACTS_FILE = os.path.join(BASE_DIR, "contacts.txt")

app = Flask(__name__)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "dev-secret-key-change-me"


def safe_read_lines(path: str) -> List[str]:
    """Safely read file lines, handling missing files gracefully."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return [l.rstrip("\n\r") for l in fh]
    except FileNotFoundError:
        return []


def init_data_files() -> None:
    """Initialize users.txt and contacts.txt with seed data on first run."""
    # ensure users file with seeded users
    users = {"admin": "adminpassword", "praise": "praisepass", "zion": "zionpass"}
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8", newline="") as fh:
            for u, p in users.items():
                fh.write(f"{u},{generate_password_hash(p)},user\n")
        # make admin role explicit
        lines = safe_read_lines(USERS_FILE)
        with open(USERS_FILE, "w", encoding="utf-8", newline="") as fh:
            for line in lines:
                parts = line.split(",")
                if parts[0] == "admin":
                    parts = [parts[0], parts[1], "admin"]
                fh.write(",".join(parts) + "\n")

    # ensure contacts file seeded with 15+ sample records
    if not os.path.exists(CONTACTS_FILE) or len(safe_read_lines(CONTACTS_FILE)) < 10:
        sample = [
            ("Aiden Park","+1-202-555-0101","aiden.park@example.com","Work","2024-06-01","admin"),
            ("Maya Johnson","+1-202-555-0112","maya.j@example.com","Family","2024-05-28","praise"),
            ("Liam Smith","+1-202-555-0133","liam.s@example.com","Friends","2024-05-22","zion"),
            ("Noah Brown","+1-202-555-0144","noah.b@example.com","Work","2024-06-02","admin"),
            ("Olivia Davis","+1-202-555-0155","olivia.d@example.com","Friends","2024-05-21","praise"),
            ("Emma Wilson","+1-202-555-0166","emma.w@example.com","Family","2024-05-18","zion"),
            ("Lucas Miller","+1-202-555-0177","lucas.m@example.com","Work","2024-05-03","admin"),
            ("Sophia Martinez","+1-202-555-0188","sophia.m@example.com","Friends","2024-04-30","praise"),
            ("Mason Anderson","+1-202-555-0199","mason.a@example.com","Work","2024-04-22","zion"),
            ("Isabella Thomas","+1-202-555-0202","isabella.t@example.com","Family","2024-04-01","admin"),
            ("James Taylor","+1-202-555-0213","james.t@example.com","Friends","2024-03-15","praise"),
            ("Amelia Moore","+1-202-555-0224","amelia.m@example.com","Others","2024-02-28","zion"),
            ("Benjamin Jackson","+1-202-555-0235","ben.j@example.com","Work","2024-02-14","admin"),
            ("Harper White","+1-202-555-0246","harper.w@example.com","Family","2024-01-08","praise"),
            ("Evelyn Harris","+1-202-555-0257","evelyn.h@example.com","Friends","2023-12-31","zion"),
        ]
        with open(CONTACTS_FILE, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            id_ = 1
            for name, phone, email, cat, date_added, owner in sample:
                writer.writerow([id_, name, phone, email, cat, date_added, owner])
                id_ += 1


def load_users() -> Dict[str, Dict[str, str]]:
    """Load all users from users.txt."""
    users: Dict[str, Dict[str, str]] = {}
    for line in safe_read_lines(USERS_FILE):
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        username = parts[0]
        pw = parts[1]
        role = parts[2] if len(parts) > 2 else "user"
        users[username] = {"password": pw, "role": role}
    return users


def append_user(username: str, password_hash: str, role: str = "user") -> None:
    """Append new user to users.txt."""
    with open(USERS_FILE, "a", encoding="utf-8", newline="") as fh:
        fh.write(f"{username},{password_hash},{role}\n")


def load_contacts() -> List[Dict[str, Any]]:
    """Load all contacts from contacts.txt."""
    contacts: List[Dict[str, Any]] = []
    lines = safe_read_lines(CONTACTS_FILE)
    for line in lines:
        if not line.strip():
            continue
        parts = [p.strip() for p in list(csv.reader([line]))[0]]
        while len(parts) < 7:
            parts.append("")
        try:
            cid = int(parts[0])
        except Exception:
            continue
        contact = {
            "id": cid,
            "name": parts[1],
            "phone": parts[2],
            "email": parts[3],
            "category": parts[4] or "Others",
            "date_added": parts[5] or datetime.utcnow().strftime("%Y-%m-%d"),
            "owner": parts[6] or "",
        }
        contacts.append(contact)
    return contacts


def save_contacts(contacts: List[Dict[str, Any]]) -> None:
    """Atomically save contacts list to contacts.txt."""
    fd, tmp = tempfile.mkstemp(dir=BASE_DIR, prefix="contacts-", suffix=".tmp")
    os.close(fd)
    try:
        with open(tmp, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            for c in contacts:
                writer.writerow([
                    c.get("id"),
                    c.get("name", ""),
                    c.get("phone", ""),
                    c.get("email", ""),
                    c.get("category", ""),
                    c.get("date_added", ""),
                    c.get("owner", ""),
                ])
        os.replace(tmp, CONTACTS_FILE)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def get_next_contact_id(contacts: List[Dict[str, Any]]) -> int:
    """Get next available contact ID."""
    if not contacts:
        return 1
    return max(c["id"] for c in contacts) + 1


def is_duplicate_contact(contacts: List[Dict[str, Any]], name: str, phone: str, owner: str) -> bool:
    """Check if contact with same name+phone already exists for owner."""
    n = (name or "").strip().lower()
    p = (phone or "").strip()
    for c in contacts:
        if c.get("owner") == owner and c.get("name", "").strip().lower() == n:
            if not p or not c.get("phone") or c.get("phone") == p:
                return True
    return False


def login_required(fn):
    """Decorator to require login."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        if "username" not in session:
            return redirect(url_for("login"))
        return fn(*a, **kw)
    return wrapper


@app.route("/")
def index():
    """Redirect to login."""
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login route."""
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        users = load_users()
        user = users.get(username)
        if user and check_password_hash(user["password"], password):
            session["username"] = username
            session["role"] = user.get("role", "user")
            flash("Logged in successfully!")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials. Try again.")
    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    """Register new user."""
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    if not username or not password:
        flash("Username and password required.")
        return redirect(url_for("login"))
    users = load_users()
    if username in users:
        flash("Username already exists.")
        return redirect(url_for("login"))
    append_user(username, generate_password_hash(password), "user")
    flash("Account created! Please log in.")
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """Logout user."""
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Dashboard route."""
    users = load_users()
    contacts = load_contacts()
    username = session.get("username")
    role = session.get("role", "user")

    # filters
    search = (request.args.get("search") or "").strip()
    selected_category = request.args.get("category") or "all"
    owner_filter = request.args.get("owner_filter") or None
    sort_key = request.args.get("sort") or "name"

    def visible(c):
        if role == "admin":
            return True
        return c.get("owner") == username

    filtered = [c for c in contacts if visible(c)]
    if search:
        s = search.lower()
        filtered = [c for c in filtered if s in (c.get("name","") or "").lower() or s in (c.get("phone","") or "") or s in (c.get("email","") or "")]
    if selected_category and selected_category != "all":
        filtered = [c for c in filtered if (c.get("category") or "").lower() == selected_category.lower()]
    if owner_filter:
        filtered = [c for c in filtered if (c.get("owner") or "") == owner_filter]

    if sort_key == "name":
        filtered.sort(key=lambda x: (x.get("name") or "").lower())
    elif sort_key == "date_newest":
        filtered.sort(key=lambda x: x.get("date_added") or "", reverse=True)
    elif sort_key == "date_oldest":
        filtered.sort(key=lambda x: x.get("date_added") or "")

    # edit request
    edit_obj = None
    edit_id = request.args.get("edit_id")
    if edit_id:
        try:
            eid = int(edit_id)
            for c in contacts:
                if c["id"] == eid:
                    edit_obj = c
                    break
        except Exception:
            edit_obj = None

    categories = sorted({(c.get("category") or "Others") for c in contacts})

    return render_template(
        "dashboard.html",
        contacts=filtered,
        users=list(users.keys()),
        username=username,
        role=role,
        total_users=len(users),
        total_contacts=len(contacts),
        total_global_contacts=len(contacts),
        personal_contacts=len([c for c in contacts if c.get("owner") == username]),
        categories=categories,
        search_query=search,
        selected_category=selected_category,
        sort_key=sort_key,
        owner_filter=owner_filter,
        edit_contact=edit_obj,
    )


@app.route("/add_contact", methods=["POST"])
@login_required
def add_contact():
    """Add new contact with duplicate check."""
    username = session.get("username")
    role = session.get("role", "user")
    name = (request.form.get("name") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    email = (request.form.get("email") or "").strip()
    category = (request.form.get("category") or "Others").strip()
    owner = username
    if role == "admin":
        owner = (request.form.get("record_owner") or username).strip() or username

    if not name or not phone:
        flash("Name and phone are required.")
        return redirect(url_for("dashboard"))

    contacts = load_contacts()
    if is_duplicate_contact(contacts, name, phone, owner):
        flash("⚠️ Duplicate contact detected! Contact not added.")
        return redirect(url_for("dashboard"))

    cid = get_next_contact_id(contacts)
    contacts.append({
        "id": cid,
        "name": name,
        "phone": phone,
        "email": email,
        "category": category,
        "date_added": datetime.utcnow().strftime("%Y-%m-%d"),
        "owner": owner,
    })
    save_contacts(contacts)
    flash(f"✓ Contact '{name}' added successfully!")
    return redirect(url_for("dashboard"))


@app.route("/edit_contact", methods=["POST"])
@login_required
def edit_contact():
    """Edit existing contact."""
    username = session.get("username")
    role = session.get("role", "user")
    try:
        cid = int(request.form.get("contact_id"))
    except Exception:
        flash("Invalid contact ID.")
        return redirect(url_for("dashboard"))

    name = (request.form.get("name") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    email = (request.form.get("email") or "").strip()
    category = (request.form.get("category") or "Others").strip()
    contacts = load_contacts()
    changed = False
    for c in contacts:
        if c.get("id") == cid:
            if session.get("role") != "admin" and c.get("owner") != username:
                flash("Permission denied.")
                return redirect(url_for("dashboard"))
            c["name"] = name
            c["phone"] = phone
            c["email"] = email
            c["category"] = category
            if role == "admin":
                c["owner"] = (request.form.get("record_owner") or c.get("owner"))
            changed = True
            break
    if changed:
        save_contacts(contacts)
        flash(f"✓ Contact updated successfully!")
    else:
        flash("Contact not found.")
    return redirect(url_for("dashboard"))


@app.route("/delete_contact/<int:contact_id>", methods=["POST"])
@login_required
def delete_contact(contact_id: int):
    """Delete contact."""
    username = session.get("username")
    contacts = load_contacts()
    new = []
    deleted = False
    for c in contacts:
        if c.get("id") == contact_id:
            if session.get("role") != "admin" and c.get("owner") != username:
                flash("Permission denied.")
                return redirect(url_for("dashboard"))
            deleted = True
            continue
        new.append(c)
    if deleted:
        save_contacts(new)
        flash("✓ Contact deleted successfully!")
    else:
        flash("Contact not found.")
    return redirect(url_for("dashboard"))


def _contacts_visible_to_request(contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter contacts visible to current user."""
    role = session.get("role", "user")
    username = session.get("username")
    if role == "admin":
        return contacts
    return [c for c in contacts if c.get("owner") == username]


@app.route("/export_txt")
@login_required
def export_txt():
    """Export visible contacts as TXT file."""
    contacts = load_contacts()
    visible = _contacts_visible_to_request(contacts)
    output_lines = []
    for c in visible:
        output_lines.append(
            ",".join([str(c.get(k, "")) for k in ("id", "name", "phone", "email", "category", "date_added", "owner")])
        )
    txt = "\n".join(output_lines)
    return Response(txt, mimetype="text/plain", headers={"Content-Disposition": "attachment; filename=contacts.txt"})


@app.route("/export_registry")
@login_required
def export_registry():
    """Admin-only full registry export."""
    if session.get("role") != "admin":
        flash("Admin only.")
        return redirect(url_for("dashboard"))
    return export_txt()


@app.route("/import_txt", methods=["POST"])
@login_required
def import_txt():
    """Import contacts from uploaded TXT file with duplicate checks."""
    if "txt_file" not in request.files:
        flash("No file provided.")
        return redirect(url_for("dashboard"))
    f = request.files["txt_file"]
    if not f.filename:
        flash("No file selected.")
        return redirect(url_for("dashboard"))
    try:
        content = f.read().decode("utf-8", errors="ignore")
    except Exception:
        flash("Failed to read uploaded file.")
        return redirect(url_for("dashboard"))
    lines = [l for l in content.splitlines() if l.strip()]
    contacts = load_contacts()
    added = 0
    skipped = 0
    for line in lines:
        try:
            parts = list(csv.reader([line]))[0]
            while len(parts) < 7:
                parts.append("")
            name = parts[1].strip() if len(parts) > 1 else ""
            phone = parts[2].strip() if len(parts) > 2 else ""
            owner = (parts[6].strip() if len(parts) > 6 else "") or session.get("username")
            if not name or not phone:
                continue
            if is_duplicate_contact(contacts, name, phone, owner):
                skipped += 1
                continue
            cid = get_next_contact_id(contacts)
            contacts.append({
                "id": cid,
                "name": name,
                "phone": phone,
                "email": parts[3].strip() if len(parts) > 3 else "",
                "category": (parts[4].strip() if len(parts) > 4 else "") or "Others",
                "date_added": (parts[5].strip() if len(parts) > 5 else "") or datetime.utcnow().strftime("%Y-%m-%d"),
                "owner": owner,
            })
            added += 1
        except Exception:
            continue
    if added:
        save_contacts(contacts)
    msg = f"✓ Imported {added} contacts."
    if skipped:
        msg += f" ({skipped} duplicates skipped)"
    flash(msg)
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_data_files()
    app.run(host="127.0.0.1", port=5000, debug=False)
