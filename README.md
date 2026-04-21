# RENTS — Residents Entry, Navigation, and Tenant Tracking System

A Django-based boarding house management system for managing tenants, rooms, billing, maintenance, and violations.

---

## 🗂️ Project Structure

```
rents_system/
│
├── manage.py
├── requirements.txt
├── .env                          ← environment variables (not in repo)
├── .gitignore
│
├── rents_system/                 ← project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── accounts/                     ← main app
    ├── migrations/
    ├── static/
    │   └── accounts/
    │       ├── css/
    │       │   └── dashboard.css
    │       └── js/
    │           ├── login.js
    │           └── dashboard.js
    │
    ├── templates/
    │   ├── login.html
    │   ├── base_dashboard.html
    │   ├── admin_dashboard.html
    │   ├── admin_list.html
    │   ├── tenant_list.html
    │   ├── tenant_dashboard.html
    │   └── partials/
    │       └── avatar.html
    │
    ├── templatetags/
    │   ├── __init__.py
    │   └── avatar_tags.py
    │
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    └── apps.py
```

---

## 🗄️ Database Structure

### `auth_user` (Django built-in)
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| username | VARCHAR | Login username |
| password | VARCHAR | Hashed password |
| email | VARCHAR | Email address |
| is_staff | BOOL | True = Admin |
| is_superuser | BOOL | True = Superadmin |
| is_active | BOOL | False = Deactivated |

### `accounts_tenantprofile`
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| user_id | FK | → auth_user |
| full_name | VARCHAR | Full name |
| phone | VARCHAR | Phone number |
| room_number | VARCHAR | Assigned room |
| photo | IMAGE | Profile photo (optional) |
| created_at | DATETIME | Account creation date |

### `accounts_adminprofile`
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| user_id | FK | → auth_user |
| full_name | VARCHAR | Full name |
| phone | VARCHAR | Phone number |
| photo | IMAGE | Profile photo (optional) |
| created_by_id | FK | → auth_user (Superadmin) |
| created_at | DATETIME | Account creation date |

### `accounts_room`
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| room_number | VARCHAR | Room number (unique) |
| capacity | INT | Max beds |
| monthly_rate | DECIMAL | Rent price |

### `accounts_bill`
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| tenant_id | FK | → tenantprofile |
| amount | DECIMAL | Bill amount |
| due_date | DATE | Due date |
| is_paid | BOOL | Payment status |
| created_at | DATETIME | Created date |

### `accounts_maintenancereport`
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| tenant_id | FK | → tenantprofile |
| description | TEXT | Report description |
| status | VARCHAR | open / ongoing / completed |
| created_at | DATETIME | Submitted date |

### `accounts_violation`
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| tenant_id | FK | → tenantprofile |
| description | TEXT | Violation description |
| date | DATE | Violation date |
| created_at | DATETIME | Logged date |

---

## 👥 User Roles

| Role | is_staff | is_superuser | Access |
|---|---|---|---|
| **Superadmin** | ✅ | ✅ | Full access + Register Admins |
| **Admin** | ✅ | ❌ | Manage tenants, rooms, billing |
| **Tenant** | ❌ | ❌ | View own profile, bills, reports |

---

## ✅ Features (Current)

### Authentication
- Login with role toggle (Admin / Tenant)
- Tenant self-signup
- Password visibility toggle
- CSRF protection
- Session-based authentication
- Redirect if already logged in

### Admin Management (Superadmin only)
- Register new admins
- View all admins list
- Activate / Deactivate admin accounts
- Delete admin accounts
- Profile photos

### Tenant Management
- View all tenants
- Add tenant (admin side)
- Edit tenant info
- Delete tenant
- Profile photos
- Clickable rows → redirect to tenant list

### Dashboard
- Summary stat cards (Total Tenants, Vacant Rooms, Unpaid Bills, Open Repairs)
- Recent tenants table
- Dark sidebar navigation
- Mobile responsive (Pixel 7 optimized)
- Clickable stat cards

---

## 🚧 Features (Planned)

- [ ] Rooms Page — room map, vacancy status
- [ ] Billing — monthly rent, mark as paid
- [ ] Maintenance — submit and track reports
- [ ] Violations — log and view violations
- [ ] Tenant Dashboard — view own info, bills, reports
- [ ] Edit Admin profile
- [ ] Search and filter tenants

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/KevzBueno101/rents_system.git
cd rents_system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file
```
SECRET_KEY=your_secret_key_here
DEBUG=True
DB_NAME=rents_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```

### 4. Create MySQL database
```sql
CREATE DATABASE rents_db;
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superadmin
```bash
python manage.py createsuperuser
```

### 7. Run the server
```bash
python manage.py runserver
```

### 8. Open in browser
```
http://127.0.0.1:8000/
```

---

## 🛠️ Tech Stack

| Technology | Usage |
|---|---|
| Python 3.12 | Backend language |
| Django 4.2.7 | Web framework |
| MySQL | Database |
| Bootstrap 5.3 | Frontend UI |
| Bootstrap Icons | Icons |
| Pillow | Image handling |
| python-dotenv | Environment variables |
| WhiteNoise | Static files |

---

## 📁 Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | True (local) / False (production) |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `DB_HOST` | Database host |
| `DB_PORT` | Database port |

---

## 👨‍💻 Developer

**Kevin Bueno** — RENTS System  
GitHub: [@KevzBueno101](https://github.com/KevzBueno101)
