import csv
import os
from io import StringIO
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "users.txt"
CONTACTS_FILE = BASE_DIR / "contacts.txt"
CATEGORIES = ["Family", "Work", "Friends", "Others"]

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")


def init_data_files():
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.touch(exist_ok=True)
    CONTACTS_FILE.touch(exist_ok=True)

    if not load_users():
        append_user("admin", generate_password_hash("adminpassword"), "admin")
        append_user("praise", generate_password_hash("praisepassword"), "user")
        append_user("zion", generate_password_hash("zionpassword"), "user")

    if CONTACTS_FILE.stat().st_size == 0:
        sample_contacts = [
            {"id": "1", "name": "Avery Bennett", "phone": "555-0101", "email": "avery.bennett@studio.com", "category": "Work", "date_added": "2024-05-01 08:12:00", "owner": "admin"},
            {"id": "2", "name": "Mia Carter", "phone": "555-0102", "email": "mia.carter@studio.com", "category": "Friends", "date_added": "2024-05-01 09:05:00", "owner": "admin"},
            {"id": "3", "name": "Ethan Morris", "phone": "555-0103", "email": "ethan.morris@family.com", "category": "Family", "date_added": "2024-05-01 10:23:00", "owner": "admin"},
            {"id": "4", "name": "Sophia Hayes", "phone": "555-0104", "email": "sophia.hayes@design.co", "category": "Work", "date_added": "2024-05-01 11:30:00", "owner": "admin"},
            {"id": "5", "name": "Noah Patel", "phone": "555-0105", "email": "noah.patel@travel.io", "category": "Others", "date_added": "2024-05-01 12:44:00", "owner": "admin"},
            {"id": "6", "name": "Emma Thompson", "phone": "555-0201", "email": "emma.thompson@friends.io", "category": "Friends", "date_added": "2024-05-02 08:52:00", "owner": "praise"},
            {"id": "7", "name": "Liam Walker", "phone": "555-0202", "email": "liam.walker@consults.com", "category": "Work", "date_added": "2024-05-02 09:40:00", "owner": "praise"},
            {"id": "8", "name": "Olivia Brooks", "phone": "555-0203", "email": "olivia.brooks@family.com", "category": "Family", "date_added": "2024-05-02 10:15:00", "owner": "praise"},
            {"id": "9", "name": "Lucas Reed", "phone": "555-0204", "email": "lucas.reed@studio.com", "category": "Work", "date_added": "2024-05-02 11:28:00", "owner": "praise"},
            {"id": "10", "name": "Chloe Hayes", "phone": "555-0205", "email": "chloe.hayes@social.io", "category": "Others", "date_added": "2024-05-02 12:49:00", "owner": "praise"},
            {"id": "11", "name": "Mason Price", "phone": "555-0301", "email": "mason.price@home.net", "category": "Family", "date_added": "2024-05-03 08:15:00", "owner": "zion"},
            {"id": "12", "name": "Isabella Ross", "phone": "555-0302", "email": "isabella.ross@friends.io", "category": "Friends", "date_added": "2024-05-03 09:22:00", "owner": "zion"},
            {"id": "13", "name": "Logan Bennett", "phone": "555-0303", "email": "logan.bennett@venture.io", "category": "Work", "date_added": "2024-05-03 10:05:00", "owner": "zion"},
            {"id": "14", "name": "Ava Morgan", "phone": "555-0304", "email": "ava.morgan@family.com", "category": "Family", "date_added": "2024-05-03 11:50:00", "owner": "zion"},
            {"id": "15", "name": "Noah King", "phone": "555-0305", "email": "noah.king@creative.io", "category": "Others", "date_added": "2024-05-03 13:12:00", "owner": "zion"},
            {"id": "16", "name": "Grace Parker", "phone": "555-0401", "email": "grace.parker@operations.com", "category": "Work", "date_added": "2024-05-04 08:42:00", "owner": "admin"},
            {"id": "17", "name": "Owen Campbell", "phone": "555-0402", "email": "owen.campbell@friends.io", "category": "Friends", "date_added": "2024-05-04 09:35:00", "owner": "admin"},
            {"id": "18", "name": "Zoe Foster", "phone": "555-0403", "email": "zoe.foster@family.com", "category": "Family", "date_added": "2024-05-04 10:44:00", "owner": "admin"},
            {"id": "19", "name": "Eli Harrison", "phone": "555-0404", "email": "eli.harrison@studio.com", "category": "Others", "date_added": "2024-05-04 12:10:00", "owner": "admin"},
            {"id": "20", "name": "Lily Cooper", "phone": "555-0405", "email": "lily.cooper@design.co", "category": "Work", "date_added": "2024-05-04 13:22:00", "owner": "admin"},
        ]
        save_contacts(sample_contacts)


def load_users():
    users = []
    if not USERS_FILE.exists():
        return users

    with open(USERS_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row or len(row) < 3:
                continue
            users.append(
                {
                    "username": row[0].strip(),
                    "password": row[1].strip(),
                    "role": row[2].strip(),
                }
            )
    return users


def append_user(username, password_hash, role):
    with open(USERS_FILE, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, password_hash, role])


def load_contacts():
    contacts = []
    if not CONTACTS_FILE.exists():
        return contacts

    with open(CONTACTS_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row or len(row) < 7:
                continue
            row = [value.strip() for value in row]
            contacts.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "phone": row[2],
                    "email": row[3],
                    "category": row[4] or "Others",
                    "date_added": row[5],
                    "owner": row[6],
                }
            )
    return contacts


def save_contacts(contacts):
    with open(CONTACTS_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for contact in contacts:
            writer.writerow(
                [
                    contact["id"],
                    contact["name"],
                    contact["phone"],
                    contact["email"],
                    contact["category"],
                    contact["date_added"],
                    contact["owner"],
                ]
            )


def normalize_value(value):
    return value.strip().lower()


def find_user(username):
    return next((user for user in load_users() if user["username"] == username), None)


def find_contact(contact_id):
    return next((contact for contact in load_contacts() if contact["id"] == str(contact_id)), None)


def filter_owner_contacts(contacts, username, role):
    if role == "admin":
        return contacts
    return [contact for contact in contacts if contact["owner"] == username]


def can_manage_contact(contact, username, role):
    return role == "admin" or contact["owner"] == username


def get_next_contact_id(contacts):
    highest = 0
    for contact in contacts:
        try:
            highest = max(highest, int(contact["id"]))
        except ValueError:
            continue
    return str(highest + 1)


def is_duplicate_contact(contacts, name, phone, owner, exclude_id=None):
    normalized_name = normalize_value(name)
    normalized_phone = normalize_value(phone)
    for contact in contacts:
        if exclude_id and contact["id"] == str(exclude_id):
            continue
        if (
            contact["owner"] == owner
            and normalize_value(contact["name"]) == normalized_name
            and normalize_value(contact["phone"]) == normalized_phone
        ):
            return True
    return False


def require_authentication():
    username = session.get("username")
    if not username:
        flash("Please sign in to continue.", "warning")
        return redirect(url_for("login"))
    return None


@app.route("/")
def home():
    if session.get("username"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = find_user(username)

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html", show_register=False)

        if user and check_password_hash(user["password"], password):
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")
        return render_template("login.html", show_register=False)

    return render_template("login.html", show_register=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("login.html", show_register=True)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("login.html", show_register=True)

        if find_user(username):
            flash("That username already exists.", "danger")
            return render_template("login.html", show_register=True)

        append_user(username, generate_password_hash(password), "user")
        flash("Account created successfully. Sign in to continue.", "success")
        return redirect(url_for("login"))

    return render_template("login.html", show_register=True)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    auth_redirect = require_authentication()
    if auth_redirect:
        return auth_redirect

    username = session.get("username")
    role = session.get("role")
    contacts = filter_owner_contacts(load_contacts(), username, role)

    owner_filter = request.args.get("owner_filter", "").strip()
    if owner_filter:
        contacts = [contact for contact in contacts if contact["owner"] == owner_filter]

    selected_category = request.args.get("category", "all")
    if selected_category != "all":
        contacts = [contact for contact in contacts if contact["category"] == selected_category]

    search_query = request.args.get("search", "").strip()
    if search_query:
        search_query_lower = search_query.lower()
        contacts = [
            contact
            for contact in contacts
            if search_query_lower in contact["name"].lower()
            or search_query_lower in contact["phone"].lower()
            or search_query_lower in contact["email"].lower()
        ]

    sort_key = request.args.get("sort", "name")
    if sort_key == "date_newest":
        contacts = sorted(contacts, key=lambda item: datetime.strptime(item["date_added"], "%Y-%m-%d %H:%M:%S"), reverse=True)
    elif sort_key == "date_oldest":
        contacts = sorted(contacts, key=lambda item: datetime.strptime(item["date_added"], "%Y-%m-%d %H:%M:%S"))
    else:
        contacts = sorted(contacts, key=lambda item: item["name"].lower())

    edit_id = request.args.get("edit_id")
    edit_contact = None
    if edit_id:
        candidate = find_contact(edit_id)
        if candidate and can_manage_contact(candidate, username, role):
            edit_contact = candidate
        else:
            flash("Unable to load that contact for editing.", "warning")

    users = [user["username"] for user in load_users()]

    return render_template(
        "dashboard.html",
        username=username,
        role=role,
        contacts=contacts,
        categories=CATEGORIES,
        users=users,
        selected_category=selected_category,
        search_query=search_query,
        sort_key=sort_key,
        owner_filter=owner_filter,
        edit_contact=edit_contact,
        total_contacts=len(filter_owner_contacts(load_contacts(), username, role)),
        total_users=len(users),
        total_global_contacts=len(load_contacts()),
    )


@app.route("/add_contact", methods=["POST"])
def add_contact():
    auth_redirect = require_authentication()
    if auth_redirect:
        return auth_redirect

    username = session.get("username")
    role = session.get("role")
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    category = request.form.get("category", "Others").strip() or "Others"
    owner = request.form.get("owner", username).strip() if role == "admin" else username

    if not name or not phone:
        flash("Name and phone are required.", "danger")
        return redirect(url_for("dashboard"))

    if role == "admin" and owner and not find_user(owner):
        flash("The selected owner does not exist.", "danger")
        return redirect(url_for("dashboard"))

    contacts = load_contacts()
    if is_duplicate_contact(contacts, name, phone, owner):
        flash("Duplicate contact detected. Please verify Name and Phone.", "warning")
        return redirect(url_for("dashboard"))

    new_contact = {
        "id": get_next_contact_id(contacts),
        "name": name,
        "phone": phone,
        "email": email,
        "category": category if category in CATEGORIES else "Others",
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "owner": owner,
    }
    contacts.append(new_contact)
    save_contacts(contacts)
    flash("Contact created successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/edit_contact", methods=["POST"])
def edit_contact():
    auth_redirect = require_authentication()
    if auth_redirect:
        return auth_redirect

    username = session.get("username")
    role = session.get("role")
    contact_id = request.form.get("contact_id")
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    category = request.form.get("category", "Others").strip() or "Others"
    owner = request.form.get("owner", username).strip() if role == "admin" else None

    if not contact_id or not name or not phone:
        flash("Contact ID, name, and phone are required.", "danger")
        return redirect(url_for("dashboard"))

    contacts = load_contacts()
    contact = find_contact(contact_id)
    if not contact or not can_manage_contact(contact, username, role):
        flash("Unable to update this contact.", "danger")
        return redirect(url_for("dashboard"))

    target_owner = contact["owner"] if role != "admin" else owner or contact["owner"]
    if role == "admin" and owner and not find_user(owner):
        flash("The selected owner does not exist.", "danger")
        return redirect(url_for("dashboard", edit_id=contact_id))

    if is_duplicate_contact(contacts, name, phone, target_owner, exclude_id=contact_id):
        flash("Duplicate contact detected for this owner. Please verify Name and Phone.", "warning")
        return redirect(url_for("dashboard", edit_id=contact_id))

    for item in contacts:
        if item["id"] == str(contact_id):
            item["name"] = name
            item["phone"] = phone
            item["email"] = email
            item["category"] = category if category in CATEGORIES else "Others"
            if role == "admin":
                item["owner"] = target_owner
            break

    save_contacts(contacts)
    flash("Contact updated successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/delete_contact/<contact_id>", methods=["POST"])
def delete_contact(contact_id):
    auth_redirect = require_authentication()
    if auth_redirect:
        return auth_redirect

    username = session.get("username")
    role = session.get("role")
    contact = find_contact(contact_id)
    if not contact or not can_manage_contact(contact, username, role):
        flash("Unable to remove this contact.", "danger")
        return redirect(url_for("dashboard"))

    contacts = [item for item in load_contacts() if item["id"] != str(contact_id)]
    save_contacts(contacts)
    flash("Contact deleted successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/export_registry")
def export_registry():
    username = session.get("username")
    role = session.get("role")
    if role != "admin":
        flash("Registry export is only available to administrators.", "danger")
        return redirect(url_for("dashboard"))

    contacts = load_contacts()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Phone", "Email", "Category", "Date_Added", "Record_Owner"])
    for contact in contacts:
        writer.writerow(
            [
                contact["id"],
                contact["name"],
                contact["phone"],
                contact["email"],
                contact["category"],
                contact["date_added"],
                contact["owner"],
            ]
        )

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=contacts_registry.csv"
    return response


if __name__ == "__main__":
    init_data_files()
    app.run(host="0.0.0.0", port=5000, debug=False)
