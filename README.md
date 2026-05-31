# 📞 Premium Contact / Address Book Application
## Project 04 - Production-Ready Flask Application

---

## 🎯 Project Overview

A sophisticated, **self-contained offline contact management system** built with Flask and text-file persistence. Designed for a course defense presentation with premium UI/UX, secure authentication, and role-based access control.

**Key Features:**
- ✅ Pitch-black dark mode + smooth light mode toggle
- ✅ Responsive split-panel layout (sidebar + main content)
- ✅ 20 pre-populated sample contacts across 3 user accounts
- ✅ Secure authentication with password hashing
- ✅ Full CRUD operations with duplicate prevention
- ✅ Advanced search, filtering, and sorting
- ✅ Admin master import/export functionality
- ✅ Theme persistence via localStorage
- ✅ Zero database dependencies (text file only)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation & Launch

```bash
# Navigate to project directory
cd PHONE_LOG_PROJECT

# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
```

Access the application at: **http://127.0.0.1:5000**

---

## 👤 Demo Credentials

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| **admin** | adminpassword | Admin | Full system access, sees all contacts globally |
| **praise** | praisepassword | User | Can only view/manage their own contacts |
| **zion** | zionpassword | User | Can only view/manage their own contacts |

---

## 📊 Sample Data

The application includes **20 realistic pre-populated contacts** distributed across:

- **Admin**: 6 contacts (Work & Family categories)
- **Praise**: 7 contacts (Work, Friends, Family, Others)
- **Zion**: 7 contacts (Work, Friends, Family, Others)

All contacts are created with realistic names, phone numbers, emails, categories, and timestamps.

---

## 🎨 Theme System

### Dark Mode (Default)
- **Background**: Pitch-black (#000000) with gradient overlay
- **Text**: Light cyan (#e7edf5)
- **Accent**: Vibrant cyan (#08d0ff)
- **Cards**: Translucent glass effect (rgba with backdrop blur)

### Light Mode
- **Background**: Clean (#f8f9fa)
- **Text**: Dark (#212529)
- **Accent**: Professional blue (#0d6efd)
- **Cards**: White with subtle shadows

### Theme Toggle
- Located at top-right corner on both pages
- Clicking toggles between dark/light modes
- Theme preference saved to browser localStorage
- Smooth 300ms CSS transitions

---

## 🏗️ Architecture

### File Structure
```
PHONE_LOG_PROJECT/
├── app.py                 # Flask backend (586 lines)
├── templates/
│   ├── login.html        # Authentication UI with theme toggle
│   └── dashboard.html    # Main dashboard with split layout
├── requirements.txt      # Python dependencies
├── users.txt             # Auto-generated (user credentials)
├── contacts.txt          # Auto-generated (contact records)
└── README.md             # This file
```

### Technology Stack
- **Framework**: Flask 2.3.2+
- **Authentication**: Werkzeug password hashing (scrypt)
- **Data Format**: CSV (comma-separated in text files)
- **Frontend**: Bootstrap 5.3.2, Bootstrap Icons
- **Styling**: CSS3 with custom variables
- **JavaScript**: Vanilla JS (no jQuery)

---

## 🔐 Security Features

### Password Management
- Passwords hashed using werkzeug's `generate_password_hash()`
- Verified with `check_password_hash()`
- No plaintext passwords stored
- Uses scrypt algorithm (FIPS 140-2 compliant)

### Access Control
- Session-based authentication
- Role-based filtering (admin sees all, users see own only)
- Owner-based contact permissions
- Duplicate prevention (name + phone validation)

### Data Validation
- Form field validation on both client and server
- Email format validation
- Category whitelist enforcement
- Owner verification for admin operations

---

## 📱 User Interface

### Login Page
- Professional card layout (520px max-width)
- Tab-based Sign In / Create Account modes
- Separate username/password fields with proper spacing
- Demo credentials displayed at footer
- Theme toggle button (top-right)
- Form validation with flash messages

### Dashboard
**Left Sidebar:**
- User profile greeting
- Role badge (Admin/User)
- Metrics cards:
  - My Active Contacts (all users)
  - Registered Users (admin only)
  - Master Contacts (admin only)

**Main Content Area:**
- Dashboard header with subtitle
- Add Contact button (opens modal)
- Sign Out button
- Search input (real-time)
- Sort dropdown (A-Z, Newest, Oldest)
- Category filter pills (All, Family, Work, Friends, Others)
- Responsive contacts table with Edit/Delete actions
- Admin: Master Import/Export section

### Add/Edit Contact Modal
- Form fields: Name, Phone, Email, Category
- Admin: Record Owner field (for assigning to other users)
- Form validation (Name & Phone required)
- Cancel / Save buttons
- Smooth modal transitions

---

## 🔄 API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/` | Home (redirects to login/dashboard) | No |
| GET | `/login` | Login page | No |
| POST | `/login` | Process login | No |
| GET | `/register` | Registration page | No |
| POST | `/register` | Create new account | No |
| GET | `/logout` | Sign out & clear session | Yes |
| GET | `/dashboard` | Main dashboard | Yes |
| POST | `/add_contact` | Create new contact | Yes |
| POST | `/edit_contact/<id>` | Update contact | Yes |
| POST | `/delete_contact/<id>` | Delete contact | Yes |
| GET | `/export_master` | Download all contacts (CSV) | Yes (Admin) |
| POST | `/import_master` | Bulk upload contacts | Yes (Admin) |

---

## 🔧 Backend Features

### Authentication System
```python
# User creation with secure hashing
append_user("username", generate_password_hash("password"), "user")

# Login verification
user = find_user(username)
if check_password_hash(user["password"], password):
    # Authenticated
```

### Contact Management
- **CRUD Operations**: Create, Read, Update, Delete
- **Duplicate Prevention**: Checks (Name + Phone + Owner)
- **Search**: Full-text search across name/phone/email
- **Filtering**: By category, by owner
- **Sorting**: Alphabetical (A-Z), Date (Newest/Oldest)
- **Import/Export**: CSV format for bulk operations

### Data Persistence
```
users.txt format:
username,password_hash,role

contacts.txt format (CSV):
id,name,phone,email,category,date_added,owner
```

---

## 📋 Sample Contact Entry

```csv
1,Sarah Johnson,555-0101,sarah.j@company.com,Work,2024-01-15 09:30:00,admin
```

| Field | Value |
|-------|-------|
| ID | 1 (auto-generated) |
| Name | Sarah Johnson |
| Phone | 555-0101 |
| Email | sarah.j@company.com |
| Category | Work |
| Date Added | 2024-01-15 09:30:00 |
| Owner | admin |

---

## 🎮 Usage Guide

### For Regular Users
1. Sign in with username/password
2. View your contacts in the dashboard
3. **Search**: Type in search box → Click Search button
4. **Filter by Category**: Click category pills (Family, Work, etc.)
5. **Sort**: Select from Sort dropdown (A-Z, Newest, Oldest)
6. **Add Contact**: Click "Add Contact" button → Fill form → Save
7. **Edit Contact**: Click "Edit" button on any row → Modify → Update
8. **Delete Contact**: Click "Delete" → Confirm
9. **Theme Toggle**: Click sun/moon icon (top-right) → Theme changes

### For Admin Users
1. All regular user features +
2. **View All Contacts**: See all 20 contacts from all users globally
3. **Admin Metrics**: View user count and total contact count
4. **Add for Others**: Click "Add Contact" → Set "Record Owner" field
5. **Bulk Import**: Navigate to "Master Import/Export" → Upload CSV
6. **Export All**: Download all contacts as CSV file

### Keyboard Shortcuts
- **Enter** in search box: Trigger search
- **Tab**: Navigate form fields
- **Escape**: Close modal dialogs

---

## 🧪 Testing Scenarios

### Scenario 1: Multi-User Access
1. Login as **admin** → See all 20 contacts
2. Logout → Login as **praise** → See only 7 contacts (owned by praise)
3. Logout → Login as **zion** → See only 7 contacts (owned by zion)

### Scenario 2: Search & Filter
1. Login as admin
2. Search "Sarah" → Should find "Sarah Johnson"
3. Filter by "Work" category → Show only work contacts
4. Sort by "Newest First" → See date order reversed

### Scenario 3: CRUD Operations
1. Add new contact (as regular user)
2. Verify it appears in table
3. Edit the contact → Change category
4. Delete the contact → Confirm removal
5. Verify not in list

### Scenario 4: Theme Toggle
1. Click theme button → Background changes
2. Reload page → Theme persists
3. Add Contact modal → Theme applies to modal too

### Scenario 5: Admin Import/Export
1. Login as admin
2. Click "Export System CSV" → Download file
3. Verify CSV contains all 20 contacts
4. Can be imported into another instance

---

## 📈 Application Statistics

| Metric | Value |
|--------|-------|
| Sample Contacts | 20 |
| User Accounts | 3 (1 admin, 2 regular) |
| Categories | 4 (Family, Work, Friends, Others) |
| Backend Lines of Code | 586 |
| CSS Variables | 8 (theme customizable) |
| API Endpoints | 12 |
| Authentication Method | Session-based |
| Data Persistence | Text files (CSV format) |
| Database Required | None |

---

## 🐛 Troubleshooting

### Issue: "Port 5000 already in use"
```bash
# Kill existing process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :5000
kill -9 <PID>
```

### Issue: ImportError for Flask/Werkzeug
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: Contacts not loading
1. Check `contacts.txt` exists in project directory
2. Verify text file isn't corrupted (open in text editor)
3. Restart Flask app (Ctrl+C then `python app.py`)

### Issue: Theme toggle not working
1. Clear browser localStorage: DevTools → Storage → Clear
2. Hard refresh page: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
3. Check console for JavaScript errors (F12)

---

## 💾 Backup & Data Recovery

### Backup Contacts
```bash
# Manual backup
cp contacts.txt contacts.txt.backup

# Or export via admin UI
# Login as admin → "Export System CSV" button
```

### Restore Contacts
```bash
# From manual backup
cp contacts.txt.backup contacts.txt

# Or import via admin UI
# Prepare CSV file → Login as admin → "Import Contacts" → Select file
```

### Reset Application
```bash
# Remove data files (reinitialize on app start)
rm users.txt contacts.txt

# Restart app
python app.py
```

---

## 🎓 Presentation Highlights

### For Course Defense
1. **Self-Contained**: No external database, complete offline functionality
2. **Custom Algorithms**: 
   - Text file parsing (CSV format)
   - Duplicate detection loop
   - Custom sorting (alphabetical, date-based)
3. **Premium UI/UX**:
   - Professional dark mode default
   - Responsive design
   - Real-time search
4. **Production-Ready**:
   - Secure password hashing
   - Form validation
   - Error handling
   - Session management
5. **Multi-User System**:
   - 3 demo accounts
   - 20 sample contacts
   - Role-based access
6. **Advanced Features**:
   - Theme switching with persistence
   - Bulk import/export
   - Category-based filtering
   - Date-based sorting

---

## 📝 License & Usage

This application is provided for educational purposes as part of an HTML/CSS course project.

---

## 📞 Support Notes

- **Application runs on**: http://127.0.0.1:5000
- **Development server only**: Use production WSGI server for deployment
- **All data stored locally**: No cloud upload or external storage
- **Offline-capable**: Once loaded, works completely offline
- **No tracking or analytics**: Privacy-first design

---

**Built with ❤️ for Course Defense Presentation**

Version 1.0 | May 2026
