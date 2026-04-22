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
    │   ├── admin/
    │   │   ├── dashboard.html
    │   │   ├── admin_list.html
    │   │   ├── tenant_list.html
    │   │   └── room_list.html
    │   ├── tenant/
    │   │   └── dashboard.html
    │   ├── partials/
    │   │   ├── avatar.html
    │   │   └── sidebar.html
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
| room_id | FK | → accounts_room |
| room_number | VARCHAR | Legacy room number |
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
| room_number | VARCHAR | Room identifier (A, B, 1, etc.) |
| floor | INT | Floor number |
| capacity | INT | Max beds |
| monthly_rate | DECIMAL | Rent price |
| photo | IMAGE | Room photo (optional) |
| area | DECIMAL | Area in sqm |
| num_cr | INT | Number of CRs |
| bed_type | VARCHAR | Single/Double Deck/Both |
| has_sink | BOOL | Has sink |
| water_included | BOOL | Water included |
| electricity_included | BOOL | Electricity included |
| has_fan | BOOL | Has fan |
| has_aircon | BOOL | Has aircon |
| has_ref | BOOL | Has refrigerator |
| has_tv | BOOL | Has TV |
| has_wifi | BOOL | Has WiFi |

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
- Tenant self-signup with real-time room selection
- Password visibility toggle
- CSRF protection
- Session-based authentication
- Redirect if already logged in
- Enhanced form validation with proper error handling

### Room Management
- **Room Creation**: Add rooms with detailed specifications
- **Room Features**: Bed type, area, CR count, appliances, inclusions
- **Room Photos**: Upload and display room images
- **Room Sorting**: Sort by rate, capacity, floor, or room number
- **Real-time Availability**: Show occupied/available beds
- **Room Details Modal**: View complete room information
- **Vacant Badges**: Display available bed count
- **Room Codes**: Format like "Room 1-A", "Room 2-B"

### Tenant Management
- View all tenants with search functionality
- Add tenant with room assignment
- Edit tenant information
- Delete tenant with confirmation
- Profile photos with avatar system
- Room transfer capabilities
- Clickable rows -> redirect to tenant details
- Real-time room availability during signup

### Admin Management (Superadmin only)
- Register new admins
- View all admins list
- Activate / Deactivate admin accounts
- Delete admin accounts
- Profile photos
- Admin activity tracking

### Dashboard
- **Enhanced Stats**: Total tenants, vacant rooms, occupancy rate
- **Real-time Data**: Live bed availability calculations
- **Recent Activity**: Recent tenants and room updates
- **Visual Indicators**: Progress bars for occupancy
- **Dark sidebar navigation**
- **Mobile responsive** (Pixel 7 optimized)
- **Clickable stat cards** with navigation

### User Experience
- **Modern UI**: Clean, professional interface
- **Responsive Design**: Works on all devices
- **Interactive Elements**: Dynamic room details display
- **Visual Feedback**: Loading states, hover effects
- **Error Handling**: Clear validation messages
- **Accessibility**: Semantic HTML, ARIA labels

---

## 🚧 Features (Planned)

- [ ] Room Search & Filtering - advanced room search capabilities
- [ ] Billing System - monthly rent, payment tracking
- [ ] Maintenance Tracking - submit and track repair requests
- [ ] Violation Management - log and view violations
- [ ] Tenant Dashboard - view personal info, bills, reports
- [ ] Bulk Room Operations - edit/delete multiple rooms
- [ ] Room Analytics - occupancy trends and reports
- [ ] Data Export - export tenant and room data
- [ ] Communication System - admin-tenant messaging
- [ ] Move-in/Move-out Tracking - tenant history

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
