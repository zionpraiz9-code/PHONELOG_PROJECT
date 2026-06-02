from pathlib import Path

base_dir = Path(__file__).resolve().parent

app_code = '''import csv
import os
from datetime import datetime
from io import StringIO
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
USERS_FILE = BASE_DIR / 'users.txt'
CONTACTS_FILE = BASE_DIR / 'contacts.txt'
CATEGORIES = ['Family', 'Work', 'Friends', 'Others']

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key')


def init_data_files():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    USERS_FILE.touch(exist_ok=True)
    CONTACTS_FILE.touch(exist_ok=True)

    if not load_users():
        append_user('admin', generate_password_hash('adminpassword'), 'admin')
        append_user('praise', generate_password_hash('praisepassword'), 'user')
        append_user('zion', generate_password_hash('zionpassword'), 'user')

    if CONTACTS_FILE.stat().st_size == 0 or not load_contacts():
        sample_contacts = [
            {'id': '1', 'name': 'Avery Bennett', 'phone': '555-0101', 'email': 'avery.bennett@studio.com', 'category': 'Work', 'date_added': '2024-05-01 08:12:00', 'owner': 'admin'},
            {'id': '2', 'name': 'Mia Carter', 'phone': '555-0102', 'email': 'mia.carter@studio.com', 'category': 'Friends', 'date_added': '2024-05-01 09:05:00', 'owner': 'admin'},
            {'id': '3', 'name': 'Ethan Morris', 'phone': '555-0103', 'email': 'ethan.morris@family.com', 'category': 'Family', 'date_added': '2024-05-01 10:23:00', 'owner': 'admin'},
            {'id': '4', 'name': 'Sophia Hayes', 'phone': '555-0104', 'email': 'sophia.hayes@design.co', 'category': 'Work', 'date_added': '2024-05-01 11:30:00', 'owner': 'admin'},
            {'id': '5', 'name': 'Noah Patel', 'phone': '555-0105', 'email': 'noah.patel@travel.io', 'category': 'Others', 'date_added': '2024-05-01 12:44:00', 'owner': 'admin'},
            {'id': '6', 'name': 'Emma Thompson', 'phone': '555-0201', 'email': 'emma.thompson@friends.io', 'category': 'Friends', 'date_added': '2024-05-02 08:52:00', 'owner': 'praise'},
            {'id': '7', 'name': 'Liam Walker', 'phone': '555-0202', 'email': 'liam.walker@consults.com', 'category': 'Work', 'date_added': '2024-05-02 09:40:00', 'owner': 'praise'},
            {'id': '8', 'name': 'Olivia Brooks', 'phone': '555-0203', 'email': 'olivia.brooks@family.com', 'category': 'Family', 'date_added': '2024-05-02 10:15:00', 'owner': 'praise'},
            {'id': '9', 'name': 'Lucas Reed', 'phone': '555-0204', 'email': 'lucas.reed@studio.com', 'category': 'Work', 'date_added': '2024-05-02 11:28:00', 'owner': 'praise'},
            {'id': '10', 'name': 'Chloe Hayes', 'phone': '555-0205', 'email': 'chloe.hayes@social.io', 'category': 'Others', 'date_added': '2024-05-02 12:49:00', 'owner': 'praise'},
            {'id': '11', 'name': 'Mason Price', 'phone': '555-0301', 'email': 'mason.price@home.net', 'category': 'Family', 'date_added': '2024-05-03 08:15:00', 'owner': 'zion'},
            {'id': '12', 'name': 'Isabella Ross', 'phone': '555-0302', 'email': 'isabella.ross@friends.io', 'category': 'Friends', 'date_added': '2024-05-03 09:22:00', 'owner': 'zion'},
            {'id': '13', 'name': 'Logan Bennett', 'phone': '555-0303', 'email': 'logan.bennett@venture.io', 'category': 'Work', 'date_added': '2024-05-03 10:05:00', 'owner': 'zion'},
            {'id': '14', 'name': 'Ava Morgan', 'phone': '555-0304', 'email': 'ava.morgan@family.com', 'category': 'Family', 'date_added': '2024-05-03 11:50:00', 'owner': 'zion'},
            {'id': '15', 'name': 'Noah King', 'phone': '555-0305', 'email': 'noah.king@creative.io', 'category': 'Others', 'date_added': '2024-05-03 13:12:00', 'owner': 'zion'},
        ]
        save_contacts(sample_contacts)


def load_users():
    users = []
    if not USERS_FILE.exists():
        return users
    with USERS_FILE.open('r', encoding='utf-8', newline='') as opened:
        reader = csv.reader(opened)
        for row in reader:
            if len(row) < 3:
                continue
            users.append({'username': row[0].strip(), 'password': row[1].strip(), 'role': row[2].strip()})
    return users


def append_user(username, password_hash, role):
    with USERS_FILE.open('a', encoding='utf-8', newline='') as opened:
        writer = csv.writer(opened)
        writer.writerow([username, password_hash, role])


def load_contacts():
    contacts = []
    if not CONTACTS_FILE.exists():
        return contacts
    with CONTACTS_FILE.open('r', encoding='utf-8', newline='') as opened:
        reader = csv.reader(opened)
        for row in reader:
            if len(row) < 7:
                continue
            row = [item.strip() for item in row]
            contacts.append({
                'id': row[0],
                'name': row[1],
                'phone': row[2],
                'email': row[3],
                'category': row[4] or 'Others',
                'date_added': row[5],
                'owner': row[6],
            })
    return contacts


def save_contacts(contacts):
    temp_path = CONTACTS_FILE.with_suffix('.tmp')
    with temp_path.open('w', encoding='utf-8', newline='') as opened:
        writer = csv.writer(opened)
        for contact in contacts:
            writer.writerow([
                contact['id'],
                contact['name'],
                contact['phone'],
                contact['email'],
                contact['category'],
                contact['date_added'],
                contact['owner'],
            ])
    temp_path.replace(CONTACTS_FILE)


def normalize_value(value):
    return str(value or '').strip().lower()


def find_user(username):
    return next((user for user in load_users() if user['username'] == username), None)


def filter_owner_contacts(contacts, username, role):
    if role == 'admin':
        return contacts
    return [contact for contact in contacts if contact['owner'] == username]


def get_next_contact_id(contacts):
    numeric_ids = [int(contact['id']) for contact in contacts if str(contact['id']).isdigit()]
    return str(max(numeric_ids) + 1 if numeric_ids else 1)


def is_duplicate_contact(contacts, name, phone, owner, exclude_id=None):
    normalized_name = normalize_value(name)
    normalized_phone = normalize_value(phone)
    for contact in contacts:
        if exclude_id and str(contact['id']) == str(exclude_id):
            continue
        if (
            contact['owner'] == owner
            and normalize_value(contact['name']) == normalized_name
            and normalize_value(contact['phone']) == normalized_phone
        ):
            return True
    return False


def require_authentication():
    if not session.get('username'):
        flash('Please sign in to continue.', 'warning')
        return redirect(url_for('login'))
    return None


@app.route('/')
def home():
    return redirect(url_for('dashboard')) if session.get('username') else redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html', show_register=False)
        user = find_user(username)
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome back, {user["username"]}.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
        return render_template('login.html', show_register=False)
    return render_template('login.html', show_register=False)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        if not username or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('login.html', show_register=True)
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('login.html', show_register=True)
        if find_user(username):
            flash('That username already exists. Choose another.', 'danger')
            return render_template('login.html', show_register=True)
        append_user(username, generate_password_hash(password), 'user')
        flash('Account created successfully. Sign in to continue.', 'success')
        return redirect(url_for('login'))
    return render_template('login.html', show_register=True)


@app.route('/logout')
def logout():
    session.clear()
    flash('Signed out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    auth = require_authentication()
    if auth:
        return auth

    username = session['username']
    role = session['role']
    contacts = filter_owner_contacts(load_contacts(), username, role)
    all_users = load_users()
    total_contacts = len(load_contacts())
    personal_contacts = sum(1 for item in load_contacts() if item['owner'] == username)
    return render_template(
        'dashboard.html',
        username=username,
        role=role,
        contacts=contacts,
        categories=CATEGORIES,
        users=all_users,
        total_users=len(all_users),
        total_contacts=total_contacts,
        personal_contacts=personal_contacts,
    )


@app.route('/add_contact', methods=['POST'])
def add_contact():
    auth = require_authentication()
    if auth:
        return auth

    username = session['username']
    role = session['role']
    contacts = load_contacts()
    target_owner = request.form.get('record_owner', username).strip() if role == 'admin' else username
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    category = request.form.get('category', '').strip() or 'Others'

    if not name or not phone:
        flash('Contact name and phone are required.', 'danger')
        return redirect(url_for('dashboard'))

    if target_owner and not find_user(target_owner):
        flash('Selected owner is not valid.', 'danger')
        return redirect(url_for('dashboard'))

    if is_duplicate_contact(contacts, name, phone, target_owner):
        flash('A similar contact already exists for this owner.', 'danger')
        return redirect(url_for('dashboard'))

    contacts.append({
        'id': get_next_contact_id(contacts),
        'name': name,
        'phone': phone,
        'email': email,
        'category': category if category in CATEGORIES else 'Others',
        'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'owner': target_owner,
    })
    save_contacts(contacts)
    flash('Contact added successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/edit_contact', methods=['POST'])
def edit_contact():
    auth = require_authentication()
    if auth:
        return auth

    username = session['username']
    role = session['role']
    contact_id = request.form.get('contact_id', '').strip()
    name = request.form.get('edit_name', '').strip()
    phone = request.form.get('edit_phone', '').strip()
    email = request.form.get('edit_email', '').strip()
    category = request.form.get('edit_category', '').strip() or 'Others'
    target_owner = request.form.get('edit_owner', username).strip() if role == 'admin' else username

    if not contact_id or not name or not phone:
        flash('All contact fields are required for update.', 'danger')
        return redirect(url_for('dashboard'))

    contacts = load_contacts()
    contact = next((item for item in contacts if item['id'] == contact_id), None)
    if not contact:
        flash('Contact not found.', 'danger')
        return redirect(url_for('dashboard'))

    if role != 'admin' and contact['owner'] != username:
        flash('You do not have permission to edit this contact.', 'danger')
        return redirect(url_for('dashboard'))

    if target_owner and not find_user(target_owner):
        flash('Selected owner is not valid.', 'danger')
        return redirect(url_for('dashboard'))

    if is_duplicate_contact(contacts, name, phone, target_owner, exclude_id=contact_id):
        flash('A duplicate contact exists with that name and phone number.', 'danger')
        return redirect(url_for('dashboard'))

    contact.update({
        'name': name,
        'phone': phone,
        'email': email,
        'category': category if category in CATEGORIES else 'Others',
        'owner': target_owner,
    })
    save_contacts(contacts)
    flash('Contact updated successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_contact/<contact_id>', methods=['POST'])
def delete_contact(contact_id):
    auth = require_authentication()
    if auth:
        return auth

    username = session['username']
    role = session['role']
    contacts = load_contacts()
    contact = next((item for item in contacts if item['id'] == contact_id), None)
    if not contact:
        flash('Contact not found.', 'danger')
        return redirect(url_for('dashboard'))

    if role != 'admin' and contact['owner'] != username:
        flash('You do not have permission to remove this contact.', 'danger')
        return redirect(url_for('dashboard'))

    save_contacts([item for item in contacts if item['id'] != contact_id])
    flash('Contact deleted successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/import_txt', methods=['POST'])
def import_txt():
    auth = require_authentication()
    if auth:
        return auth

    username = session['username']
    uploaded = request.files.get('txt_file')
    if not uploaded or uploaded.filename == '':
        flash('Please select a text file to import.', 'danger')
        return redirect(url_for('dashboard'))

    text = uploaded.stream.read().decode('utf-8', errors='replace')
    reader = csv.reader(StringIO(text), skipinitialspace=True)
    contacts = load_contacts()
    imported = 0
    skipped = 0
    for row in reader:
        if len(row) < 2:
            continue
        name = str(row[0]).strip()
        phone = str(row[1]).strip()
        email = str(row[2]).strip() if len(row) > 2 else ''
        category = str(row[3]).strip() if len(row) > 3 else 'Others'
        if not name or not phone:
            continue
        if is_duplicate_contact(contacts, name, phone, username):
            skipped += 1
            continue
        contacts.append({
            'id': get_next_contact_id(contacts),
            'name': name,
            'phone': phone,
            'email': email,
            'category': category if category in CATEGORIES else 'Others',
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'owner': username,
        })
        imported += 1
    if imported:
        save_contacts(contacts)
    flash(f'Imported {imported} contacts. Skipped {skipped} duplicates.', 'success' if imported else 'warning')
    return redirect(url_for('dashboard'))


@app.route('/export_txt')
def export_txt():
    auth = require_authentication()
    if auth:
        return auth

    username = session['username']
    role = session['role']
    contacts = filter_owner_contacts(load_contacts(), username, role)
    output = StringIO()
    for contact in contacts:
        output.write(f"{contact['name']},{contact['phone']},{contact['email']},{contact['category']}\n")
    response = Response(output.getvalue(), mimetype='text/plain; charset=utf-8')
    response.headers['Content-Disposition'] = f'attachment; filename=contacts_{username}.txt'
    return response


if __name__ == '__main__':
    init_data_files()
    app.run(host='0.0.0.0', port=5000)
'''

login_code = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Secure Address Book Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" integrity="sha384-VuO2amGktrwz7VhE2gQXc+qBTSJpqXRD3wgj+NQJj89Kql5pF3U8Xc0MRm5+v8T8" crossorigin="anonymous" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" />
    <style>
      :root {
        --bg: #000000;
        --panel: rgba(255, 255, 255, 0.06);
        --panel-strong: rgba(255, 255, 255, 0.12);
        --text: #ffffff;
        --muted: #94a3b8;
        --border: rgba(0, 229, 255, 0.32);
        --accent: #00e5ff;
      }
      html.light-mode {
        --bg: #f8f9fa;
        --panel: #ffffff;
        --panel-strong: #f1f5f9;
        --text: #0f172a;
        --muted: #475569;
        --border: rgba(14, 165, 233, 0.24);
        --accent: #0ea5e9;
      }
      * { box-sizing: border-box; transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease; }
      body { margin: 0; min-height: 100vh; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
      .page-shell { min-height: 100vh; display: grid; place-items: center; padding: 48px 24px; }
      .theme-button { position: fixed; top: 20px; right: 20px; width: 56px; height: 56px; border-radius: 50%; border: 1px solid var(--border); background: var(--panel); color: var(--text); display: grid; place-items: center; cursor: pointer; z-index: 30; }
      .auth-card { width: min(620px, 100%); background: var(--panel); border: 1px solid var(--border); border-radius: 32px; padding: 44px; box-shadow: 0 40px 120px rgba(0, 0, 0, 0.25); }
      .page-title { margin: 0 0 10px; font-size: clamp(2rem, 3vw, 2.8rem); letter-spacing: -0.06em; line-height: 1.05; }
      .page-copy { margin: 0 0 34px; color: var(--muted); max-width: 38rem; line-height: 1.8; }
      .form-toggle { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 30px; }
      .toggle-button { border-radius: 999px; border: 1px solid var(--border); background: transparent; color: var(--text); padding: 16px 20px; font-weight: 700; cursor: pointer; }
      .toggle-button.active { background: rgba(0, 229, 255, 0.16); border-color: rgba(0, 229, 255, 0.5); }
      .form-group { margin-bottom: 1.5rem; }
      .form-label { display: block; margin-bottom: 0.85rem; font-weight: 700; }
      .form-control { width: 100%; border-radius: 999px; border: 1px solid var(--border); background: var(--panel-strong); color: var(--text); padding: 18px 22px; min-height: 56px; }
      .form-control::placeholder { color: var(--muted); }
      .form-control:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 0.2rem rgba(0, 229, 255, 0.15); }
      .btn-primary { width: 100%; border-radius: 999px; border: none; background: linear-gradient(135deg, #00e5ff 0%, #4fd8ff 100%); color: #030712; font-weight: 800; padding: 16px 0; }
      .alert { border-radius: 22px; }
      .helper-copy { margin-top: 28px; color: var(--muted); line-height: 1.8; }
    </style>
  </head>
  <body>
    <button id="themeToggle" class="theme-button" aria-label="Toggle theme"><i class="bi bi-brightness-high-fill"></i></button>
    <main class="page-shell">
      <section class="auth-card">
        <h1 class="page-title">Secure Contact Hub</h1>
        <p class="page-copy">Access your suite of contact workflows with a spacious, centered sign-in experience built for presentation-grade security and clarity.</p>

        <div class="form-toggle">
          <button id="signInBtn" type="button" class="toggle-button active">Sign In</button>
          <button id="registerBtn" type="button" class="toggle-button">Register</button>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        <div class="mb-4">
          {% for category, message in messages %}
          <div class="alert alert-{{ 'danger' if category == 'danger' else 'warning' if category == 'warning' else 'success' if category == 'success' else 'info' }}" role="alert">{{ message }}</div>
          {% endfor %}
        </div>
        {% endif %}
        {% endwith %}

        <div id="signInPanel">
          <form action="{{ url_for('login') }}" method="post" autocomplete="off">
            <div class="form-group">
              <label class="form-label" for="loginUsername">Username</label>
              <input id="loginUsername" name="username" type="text" class="form-control" placeholder="Enter your username" required />
            </div>
            <div class="form-group">
              <label class="form-label" for="loginPassword">Password</label>
              <input id="loginPassword" name="password" type="password" class="form-control" placeholder="Enter your password" required />
            </div>
            <button type="submit" class="btn btn-primary">Sign In</button>
          </form>
        </div>

        <div id="registerPanel" style="display: none;">
          <form action="{{ url_for('register') }}" method="post" autocomplete="off">
            <div class="form-group">
              <label class="form-label" for="registerUsername">Username</label>
              <input id="registerUsername" name="username" type="text" class="form-control" placeholder="Choose a username" required />
            </div>
            <div class="form-group">
              <label class="form-label" for="registerPassword">Password</label>
              <input id="registerPassword" name="password" type="password" class="form-control" placeholder="Create a secure password" required />
            </div>
            <div class="form-group">
              <label class="form-label" for="registerConfirm">Confirm Password</label>
              <input id="registerConfirm" name="confirm_password" type="password" class="form-control" placeholder="Confirm your password" required />
            </div>
            <button type="submit" class="btn btn-primary">Create Account</button>
          </form>
        </div>
      </section>
    </main>

    <script>
      const html = document.documentElement;
      const themeToggle = document.getElementById('themeToggle');
      const signInBtn = document.getElementById('signInBtn');
      const registerBtn = document.getElementById('registerBtn');
      const signInPanel = document.getElementById('signInPanel');
      const registerPanel = document.getElementById('registerPanel');
      const storedTheme = localStorage.getItem('theme') || 'dark';

      function applyTheme(theme) {
        html.classList.toggle('light-mode', theme === 'light');
        themeToggle.innerHTML = theme === 'light' ? '<i class="bi bi-moon-stars-fill"></i>' : '<i class="bi bi-brightness-high-fill"></i>';
        localStorage.setItem('theme', theme);
      }

      function showPanel(registerMode) {
        signInPanel.style.display = registerMode ? 'none' : 'block';
        registerPanel.style.display = registerMode ? 'block' : 'none';
        signInBtn.classList.toggle('active', !registerMode);
        registerBtn.classList.toggle('active', registerMode);
      }

      themeToggle.addEventListener('click', () => applyTheme(html.classList.contains('light-mode') ? 'dark' : 'light'));
      signInBtn.addEventListener('click', () => showPanel(false));
      registerBtn.addEventListener('click', () => showPanel(true));

      applyTheme(storedTheme);
      {% if show_register %}
      showPanel(true);
      {% endif %}
    </script>
  </body>
</html>
'''

dash_code = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Address Book Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" integrity="sha384-VuO2amGktrwz7VhE2gQXc+qBTSJpqXRD3wgj+NQJj89Kql5pF3U8Xc0MRm5+v8T8" crossorigin="anonymous" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" />
    <style>
      :root {
        color-scheme: dark;
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --bg: #000000;
        --panel: rgba(255, 255, 255, 0.06);
        --panel-soft: rgba(255, 255, 255, 0.08);
        --text: #ffffff;
        --muted: #8ba5ba;
        --border: rgba(0, 229, 255, 0.22);
        --accent: #00e5ff;
        --accent-strong: #00b2d8;
        --button-bg: rgba(0, 229, 255, 0.12);
      }
      html.light-mode {
        color-scheme: light;
        --bg: #f8f9fa;
        --panel: #ffffff;
        --panel-soft: #f1f5f9;
        --text: #0f172a;
        --muted: #475569;
        --border: rgba(14, 165, 233, 0.24);
        --accent: #0ea5e9;
        --accent-strong: #0b79b4;
        --button-bg: rgba(14, 165, 233, 0.1);
      }
      *, *::before, *::after { box-sizing: border-box; transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease, transform 0.2s ease; }
      body { margin: 0; min-height: 100vh; background: var(--bg); color: var(--text); }
      .page-wrap { min-height: 100vh; background: var(--bg); }
      .container-fluid { max-width: 1600px; padding-left: 3rem; padding-right: 3rem; }
      .top-bar { display: flex; flex-wrap: wrap; align-items: flex-start; justify-content: space-between; gap: 1rem; padding: 32px 0 20px; }
      .brand-copy h1 { margin: 0; font-size: clamp(2rem, 3vw, 3rem); letter-spacing: -0.05em; }
      .brand-copy p { margin: 14px 0 0; max-width: 720px; color: var(--muted); line-height: 1.7; }
      .action-group { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
      .theme-button { border-radius: 999px; border: 1px solid var(--border); background: var(--panel); color: var(--text); width: 56px; height: 56px; display: grid; place-items: center; cursor: pointer; }
      .hero-pill { border-radius: 999px; border: 1px solid var(--accent); background: rgba(0, 229, 255, 0.12); color: var(--accent); padding: 10px 18px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
      .dashboard-grid { display: grid; grid-template-columns: 1fr; gap: 24px; }
      .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 28px; padding: 28px; box-shadow: 0 40px 110px rgba(0, 0, 0, 0.18); }
      .panel h2 { margin: 0 0 12px; font-size: 1.05rem; }
      .panel p { margin: 0; color: var(--muted); line-height: 1.8; }
      .metric-stack { display: grid; gap: 18px; }
      .metric-card { display: flex; flex-direction: column; justify-content: space-between; padding: 22px; border-radius: 24px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(0, 229, 255, 0.16); min-height: 140px; }
      .metric-card--action { cursor: pointer; }
      .metric-card strong { display: block; font-size: 2.45rem; line-height: 1; }
      .metric-card small { color: var(--muted); text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.8rem; }
      .form-section { display: grid; gap: 16px; }
      .field-label { display: block; margin-bottom: 0.75rem; font-weight: 700; }
      .form-control, .form-select { width: 100%; border-radius: 999px; border: 1px solid var(--border); background: var(--panel-soft); color: var(--text); padding: 16px 20px; min-height: 56px; }
      .form-control::placeholder, .form-select option { color: var(--muted); }
      .form-control:focus, .form-select:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 0.2rem rgba(0, 229, 255, 0.16); }
      .submit-action { width: 100%; border-radius: 999px; border: none; padding: 16px 24px; background: linear-gradient(135deg, #00e5ff 0%, #4fd8ff 100%); color: #030712; font-weight: 800; }
      .controls-top { display: grid; gap: 18px; margin-bottom: 22px; }
      .table-controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
      .filter-pills { display: flex; flex-wrap: wrap; gap: 10px; }
      .filter-pill { border-radius: 999px; border: 1px solid var(--border); background: var(--panel); color: var(--text); padding: 10px 18px; font-weight: 700; cursor: pointer; }
      .filter-pill.active { border-color: var(--accent); background: rgba(0, 229, 255, 0.14); color: var(--accent); }
      .table-wrap { overflow-x: auto; }
      table { width: 100%; min-width: 980px; border-collapse: collapse; }
      thead th { text-align: left; padding: 18px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.12); text-transform: uppercase; font-size: 0.78rem; letter-spacing: 0.14em; color: var(--muted); }
      tbody tr { transition: background-color 0.2s ease; }
      tbody tr:hover { background: rgba(255, 255, 255, 0.05); }
      td { padding: 18px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); vertical-align: middle; }
      .contact-name { font-weight: 700; }
      .contact-email { display: block; color: var(--muted); margin-top: 4px; }
      .tag { display: inline-flex; align-items: center; justify-content: center; border-radius: 999px; padding: 8px 14px; font-size: 0.82rem; font-weight: 700; background: rgba(0, 229, 255, 0.12); color: var(--accent); }
      .action-button { border-radius: 999px; border: 1px solid var(--border); background: transparent; color: var(--text); padding: 10px 16px; font-weight: 700; cursor: pointer; }
      .action-button:hover { background: rgba(255, 255, 255, 0.08); }
      .badge-small { font-size: 0.78rem; padding: 6px 12px; border-radius: 999px; border: 1px solid var(--border); }
      .modal-content { background: var(--panel); border: 1px solid var(--border); color: var(--text); }
      .modal-header, .modal-footer { border-color: rgba(255, 255, 255, 0.08); }
      .search-input { min-width: 320px; }
      @media (min-width: 992px) { .dashboard-grid { grid-template-columns: 0.92fr 1.55fr; } }
    </style>
  </head>
  <body>
    <div class="page-wrap">
      <div class="container-fluid px-5">
        <header class="top-bar">
          <div class="brand-copy">
            <span class="hero-pill">Pitch Black Registry</span>
            <h1>Contact Authority Console</h1>
            <p>Balanced widescreen layout, secure multi-user contact sync, and a polished admin-ready dashboard.</p>
          </div>
          <div class="action-group">
            <button id="themeToggle" class="theme-button" aria-label="Toggle theme"><i class="bi bi-moon-stars-fill"></i></button>
            <a href="{{ url_for('logout') }}" class="action-button">Sign Out</a>
          </div>
        </header>

        <div class="dashboard-grid row g-4">
          <aside class="col-xl-3 col-lg-4">
            <div class="metric-stack">
              <div class="metric-card">
                <small>My Active Contacts</small>
                <strong>{{ personal_contacts }}</strong>
                <p>Contacts owned by {{ username }}.</p>
              </div>
              <div class="metric-card metric-card--action" data-bs-toggle="modal" data-bs-target="#usersModal">
                <small>Registered Users</small>
                <strong>{{ total_users }}</strong>
                <p>Click to reveal system users and filter the directory.</p>
              </div>
              <div class="metric-card">
                <small>Master Contact Pool</small>
                <strong>{{ total_contacts }}</strong>
                <p>Total records in the flat-file registry.</p>
              </div>
            </div>

            <section class="panel mt-4">
              <h2>Add New Contact</h2>
              <p>Use the form below to add a contact. Admins may assign an owner.</p>
              <form action="{{ url_for('add_contact') }}" method="post" class="form-section">
                <div>
                  <label class="field-label" for="name">Name</label>
                  <input id="name" name="name" type="text" class="form-control" placeholder="Contact name" required />
                </div>
                <div>
                  <label class="field-label" for="phone">Phone</label>
                  <input id="phone" name="phone" type="text" class="form-control" placeholder="e.g. 555-0123" required />
                </div>
                <div>
                  <label class="field-label" for="email">Email</label>
                  <input id="email" name="email" type="email" class="form-control" placeholder="email@example.com" />
                </div>
                <div>
                  <label class="field-label" for="category">Category</label>
                  <select id="category" name="category" class="form-select">
                    {% for category in categories %}
                    <option value="{{ category }}">{{ category }}</option>
                    {% endfor %}
                  </select>
                </div>
                {% if role == 'admin' %}
                <div>
                  <label class="field-label" for="record_owner">Record Owner</label>
                  <select id="record_owner" name="record_owner" class="form-select">
                    {% for user in users %}
                    <option value="{{ user.username }}" {% if user.username == username %}selected{% endif %}>{{ user.username }}</option>
                    {% endfor %}
                  </select>
                </div>
                {% endif %}
                <button type="submit" class="btn submit-action">Add Contact</button>
              </form>
            </section>

            <section class="panel mt-4">
              <h2>TXT Import / Export</h2>
              <p>Upload a flat text file of rows or download your current contact set.</p>
              <form action="{{ url_for('import_txt') }}" method="post" enctype="multipart/form-data" class="form-section">
                <input type="file" name="txt_file" accept=".txt" class="form-control" required />
                <button type="submit" class="btn submit-action">Import TXT</button>
              </form>
              <a href="{{ url_for('export_txt') }}" class="btn submit-action" style="text-align: center;">Export TXT</a>
            </section>
          </aside>

          <main class="col-xl-9 col-lg-8">
            <section class="panel">
              <div class="controls-top">
                <div class="table-controls">
                  <input id="searchInput" type="search" class="form-control search-input" placeholder="Search contacts" />
                  <select id="sortSelect" class="form-select" style="max-width: 220px;">
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="az">Name A-Z</option>
                    <option value="za">Name Z-A</option>
                  </select>
                </div>
                <div class="filter-pills" id="categoryPills">
                  <span class="filter-pill active" data-category="All">All</span>
                  {% for category in categories %}
                  <span class="filter-pill" data-category="{{ category }}">{{ category }}</span>
                  {% endfor %}
                </div>
              </div>

              <div class="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Phone</th>
                      <th>Email</th>
                      <th>Category</th>
                      <th>Owner</th>
                      <th>Date Added</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody id="contactsTable">
                    {% for contact in contacts %}
                    <tr data-owner="{{ contact.owner }}" data-category="{{ contact.category }}" data-search="{{ contact.name }} {{ contact.phone }} {{ contact.email }} {{ contact.category }} {{ contact.owner }}">
                      <td>
                        <span class="contact-name">{{ contact.name }}</span>
                        <span class="contact-email">{{ contact.email }}</span>
                      </td>
                      <td>{{ contact.phone }}</td>
                      <td>{{ contact.email }}</td>
                      <td><span class="tag">{{ contact.category }}</span></td>
                      <td>{{ contact.owner }}</td>
                      <td>{{ contact.date_added }}</td>
                      <td>
                        <button type="button" class="action-button edit-button" data-contact='{{ contact | tojson }}'>Edit</button>
                        <form action="{{ url_for('delete_contact', contact_id=contact.id) }}" method="post" style="display: inline-block; margin-left: 8px;">
                          <button type="submit" class="action-button">Delete</button>
                        </form>
                      </td>
                    </tr>
                    {% endfor %}
                  </tbody>
                </table>
              </div>
            </section>
          </main>
        </div>
      </div>
    </div>

    <div class="modal fade" id="usersModal" tabindex="-1" aria-labelledby="usersModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title" id="usersModalLabel">System User Filters</h5>
              <p class="mb-0">Select a username to isolate records in the contact table.</p>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="d-grid gap-2">
              {% for user in users %}
              <button type="button" class="btn action-button user-filter-btn" data-owner="{{ user.username }}">{{ user.username }}</button>
              {% endfor %}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn submit-action" id="clearOwnerFilter">Clear Filter</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editModal" tabindex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editModalLabel">Edit Contact</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form id="editForm" action="{{ url_for('edit_contact') }}" method="post" class="form-section">
              <input type="hidden" name="contact_id" id="editContactId" />
              <div>
                <label class="field-label" for="editName">Name</label>
                <input id="editName" name="edit_name" type="text" class="form-control" required />
              </div>
              <div>
                <label class="field-label" for="editPhone">Phone</label>
                <input id="editPhone" name="edit_phone" type="text" class="form-control" required />
              </div>
              <div>
                <label class="field-label" for="editEmail">Email</label>
                <input id="editEmail" name="edit_email" type="email" class="form-control" />
              </div>
              <div>
                <label class="field-label" for="editCategory">Category</label>
                <select id="editCategory" name="edit_category" class="form-select">
                  {% for category in categories %}
                  <option value="{{ category }}">{{ category }}</option>
                  {% endfor %}
                </select>
              </div>
              {% if role == 'admin' %}
              <div>
                <label class="field-label" for="editOwner">Owner</label>
                <select id="editOwner" name="edit_owner" class="form-select">
                  {% for user in users %}
                  <option value="{{ user.username }}">{{ user.username }}</option>
                  {% endfor %}
                </select>
              </div>
              {% endif %}
              <div class="d-flex justify-content-end gap-3 mt-3">
                <button type="button" class="btn action-button" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn submit-action">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-ENjdO4Dr2bkBIFxQpeo4EnKQxO/X5Qzqqz5fRnM5M4wt9HHJN1b6GVI1jM2U8pKz" crossorigin="anonymous"></script>
    <script>
      const html = document.documentElement;
      const themeToggle = document.getElementById('themeToggle');
      const storedTheme = localStorage.getItem('theme') || 'dark';
      const searchInput = document.getElementById('searchInput');
      const sortSelect = document.getElementById('sortSelect');
      const categoryPills = document.querySelectorAll('.filter-pill');
      const contactRows = Array.from(document.querySelectorAll('#contactsTable tr'));
      let activeCategory = 'All';
      let activeOwner = '';

      function applyTheme(theme) {
        html.classList.toggle('light-mode', theme === 'light');
        themeToggle.innerHTML = theme === 'light' ? '<i class="bi bi-moon-stars-fill"></i>' : '<i class="bi bi-brightness-high-fill"></i>';
        localStorage.setItem('theme', theme);
      }

      function filterTable() {
        const query = searchInput.value.trim().toLowerCase();
        contactRows.forEach((row) => {
          const text = row.dataset.search.toLowerCase();
          const matchesQuery = !query || text.includes(query);
          const matchesCategory = activeCategory === 'All' || row.dataset.category === activeCategory;
          const matchesOwner = !activeOwner || row.dataset.owner === activeOwner;
          row.style.display = matchesQuery && matchesCategory && matchesOwner ? '' : 'none';
        });
      }

      function sortTable() {
        const tbody = document.querySelector('#contactsTable');
        const visibleRows = Array.from(contactRows).filter((row) => row.style.display !== 'none');
        visibleRows.sort((a, b) => {
          if (sortSelect.value === 'az' || sortSelect.value === 'za') {
            const nameA = a.querySelector('.contact-name').textContent.trim().toLowerCase();
            const nameB = b.querySelector('.contact-name').textContent.trim().toLowerCase();
            return sortSelect.value === 'az' ? nameA.localeCompare(nameB) : nameB.localeCompare(nameA);
          }
          const dateA = new Date(a.cells[5].textContent.trim());
          const dateB = new Date(b.cells[5].textContent.trim());
          return sortSelect.value === 'newest' ? dateB - dateA : dateA - dateB;
        });
        visibleRows.forEach((row) => tbody.appendChild(row));
      }

      function refreshTable() {
        filterTable();
        sortTable();
      }

      applyTheme(storedTheme);
      searchInput.addEventListener('input', refreshTable);
      sortSelect.addEventListener('change', refreshTable);

      categoryPills.forEach((pill) => {
        pill.addEventListener('click', () => {
          categoryPills.forEach((item) => item.classList.remove('active'));
          pill.classList.add('active');
          activeCategory = pill.dataset.category;
          refreshTable();
        });
      });

      document.querySelectorAll('.user-filter-btn').forEach((button) => {
        button.addEventListener('click', () => {
          activeOwner = button.dataset.owner;
          refreshTable();
          const modal = bootstrap.Modal.getInstance(document.getElementById('usersModal'));
          modal.hide();
        });
      });

      document.getElementById('clearOwnerFilter').addEventListener('click', () => {
        activeOwner = '';
        refreshTable();
        const modal = bootstrap.Modal.getInstance(document.getElementById('usersModal'));
        modal.hide();
      });

      document.querySelectorAll('.edit-button').forEach((button) => {
        button.addEventListener('click', () => {
          const data = JSON.parse(button.dataset.contact);
          document.getElementById('editContactId').value = data.id;
          document.getElementById('editName').value = data.name;
          document.getElementById('editPhone').value = data.phone;
          document.getElementById('editEmail').value = data.email;
          document.getElementById('editCategory').value = data.category;
          const ownerField = document.getElementById('editOwner');
          if (ownerField) {
            ownerField.value = data.owner;
          }
          const editModal = new bootstrap.Modal(document.getElementById('editModal'));
          editModal.show();
        });
      });
    </script>
  </body>
</html>
'''

login_path = base_dir / 'templates' / 'login.html'
dash_path = base_dir / 'templates' / 'dashboard.html'
app_path = base_dir / 'app.py'

app_path.write_text(app_code, encoding='utf-8')
login_path.write_text(login_code, encoding='utf-8')
dash_path.write_text(dash_code, encoding='utf-8')
'''}