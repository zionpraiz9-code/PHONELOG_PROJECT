# 📞 Phone Log Project

## Production-Ready Flask Contact Manager

A premium, self-contained Flask application for managing contacts with flat-file storage. The system uses `users.txt` and `contacts.txt` to persist data, and supports user roles, secure authentication, duplicate protection, search, filtering, and CSV export/import.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or newer
- pip package manager

### Setup
```powershell
cd C:/Users/User pc/Desktop/HTML-CSS-COURSE/PHONE_LOG_PROJECT
pip install -r requirements.txt
python app.py
```

Open your browser at: ** OLALERUPRAISE.pythonanywhere.com**

---

## 🔐 Built-in Users

The project seeds three accounts on first launch:

| Username | Role | Notes |
|----------|------|-------|
| `admin` | Admin | Full system access, export/import support |
| `praise` | User | Own contact management only |
| `zion` | User | Own contact management only |

> Passwords are stored securely as hashes in `users.txt`.

---

## 📦 What’s Included

- Admin and regular user roles
- Flat-file persistence using `users.txt` and `contacts.txt`
- Secure password hashing with Werkzeug
- Duplicate contact validation by name, phone, owner
- Full CRUD: add, edit, delete contacts
- Search, category filtering, and sorting
- Admin-only CSV export/import
- Premium dark/light theme toggle with persistence

---

## 📁 File Structure

```
PHONE_LOG_PROJECT/
├── app.py
├── requirements.txt
├── users.txt
├── contacts.txt
├── templates/
│   ├── login.html
│   └── dashboard.html
└── README.md
```

---

## 🧠 Architecture

- `app.py`: Flask backend, session auth, flat-file parsing
- `templates/`: Jinja2 views for login and dashboard
- `users.txt`: comma-separated user records
- `contacts.txt`: comma-separated contact records

---

## 🛠️ Backend Details

### Authentication
- Uses `generate_password_hash()` and `check_password_hash()`
- Session-based login
- Admin and regular users have different access levels

### Contact Data
- Stored as CSV text in `contacts.txt`
- Fields: `id,name,phone,email,category,date_added,owner`
- Admin can view and manage all records
- Users can only manage their own records

### Duplicate Handling
Contacts are checked for duplicates based on:
- Name
- Phone number
- Owner

If a duplicate is detected, the app prevents creation and updates.

---

## 🧾 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Redirect to login/dashboard |
| GET | `/login` | Login page |
| POST | `/login` | Authenticate user |
| GET | `/register` | Create account page |
| POST | `/register` | Register new user |
| GET | `/logout` | Logout and clear session |
| GET | `/dashboard` | Main dashboard |
| POST | `/add_contact` | Add a contact |
| POST | `/edit_contact/<id>` | Edit a contact |
| POST | `/delete_contact/<id>` | Delete a contact |
| GET | `/export_master` | Download all contacts as CSV (Admin) |
| POST | `/import_master` | Upload CSV contacts (Admin) |

---

## 📌 Sample Contact Format

`contacts.txt` stores records like:

```csv
1,Sarah Johnson,555-0101,sarah.j@company.com,Work,2024-01-15 09:30:00,admin
```

| Column | Description |
|--------|-------------|
| id | Auto-generated numeric identifier |
| name | Contact name |
| phone | Contact phone number |
| email | Contact email |
| category | Contact category |
| date_added | Timestamp when created |
| owner | Username who owns the contact |

---

## 🎮 How to Use

### Regular User
1. Login with your username and password
2. View your contacts in the dashboard
3. Search by name, phone, or email
4. Filter by category pills
5. Sort contacts by A-Z, newest, or oldest
6. Add, edit, or delete your own contacts
7. Toggle theme using the button in the top-right

### Admin User
1. Login as `admin`
2. View all contacts across all users
3. Add contacts for any user
4. Export full contact registry as CSV
5. Import contacts from a CSV file

---

## 🧪 Testing Scenarios

### Multi-User Behavior
- `admin` sees all contacts
- `praise` sees only praise-owned contacts
- `zion` sees only zion-owned contacts

### Data Operations
- Add a new contact
- Edit an existing contact
- Delete a contact and verify removal
- Attempt duplicate entry and confirm prevention

---

## 🚨 Troubleshooting

### Port 5000 Already in Use
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Dependency Issues
```powershell
pip install --upgrade -r requirements.txt
```

### Data File Errors
- Ensure `users.txt` and `contacts.txt` exist
- Verify CSV format is intact
- Restart the app after fixing files

---

## 💾 Backup & Reset

### Backup
```powershell
copy contacts.txt contacts.txt.backup
```

### Restore
```powershell
copy contacts.txt.backup contacts.txt
```

### Reset
```powershell
Remove-Item users.txt, contacts.txt
python app.py
```

---

## ✅ Notes

- Built as a flat-file project with no database dependency
- Admin can manage the full dataset and export/import CSV
- Regular users only manage their own records
- Theme preferences persist locally in the browser
