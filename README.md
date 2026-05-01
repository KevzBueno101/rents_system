# RENTS - Residents Entry, Navigation, and Tenant Tracking System

A Django-based boarding house management system for managing tenants, rooms, billing, maintenance, and violations.

## Current Status: **Production Ready** v2.7

**Latest Updates (May 2, 2026):**
- ✅ **Tenant System Revert** - Successfully reverted to original simple tenant dashboard structure
- ✅ **Navigation Cleanup** - Removed modular navigation system components for cleaner interface
- ✅ **Audit Trail Improvements** - Removed export functionality, moved filters to table top, fixed pagination
- ✅ **Login Flow Fix** - Removed automatic redirect, login page now shows first
- ✅ **Template Structure Cleanup** - Fixed UnboundLocalError, improved responsive layouts
- ✅ **UI Component Enhancement** - Uniform filter heights and improved responsive design

**Previous Updates (April 28, 2026 - Evening):**
- ✅ **Centralized Context Processors** - Implemented unified context processors for global template access
- ✅ **Modular Views Architecture** - Refactored monolithic views.py into feature-specific modules
- ✅ **Enhanced UI Components** - Dynamic tenant payment status, scrollable feeds, improved layouts
- ✅ **Database Query Optimization** - Added select_related/prefetch_related across all views
- ✅ **Custom Template Tags** - Created reusable template tags for tenant status and utilities
- ✅ **Dashboard Improvements** - Recent Tenants on right side, 3-per-row billing stats, compact feeds
- ✅ **Payment Activity Enhancement** - Recent payments show tenant names instead of bill numbers
- ✅ **Backward Compatibility** - All changes maintain existing functionality without breaking changes

**Previous Updates (April 28, 2026 - Morning):**
- ✅ **Comprehensive Activity Logging** - Added activity logging to all major system actions
- ✅ **Tenant Activity Tracking** - Log tenant creation, updates, and deletions
- ✅ **Room Activity Tracking** - Log room creation, updates, and deletions
- ✅ **Admin Activity Tracking** - Log admin registration, status changes, and deletions
- ✅ **Recent Activity Feed** - Now displays all system-wide actions with icons and colors
- ✅ **Recent Tenants Limit** - Reduced display from 8 to 7 tenants for better layout
- ✅ **Non-Breaking Changes** - All activity logging additions are modular and don't affect existing features

**Previous Updates (April 27, 2026 - Night):**
- ✅ **Maintenance Management System** - Create, list, update status (Open → Ongoing → Completed), delete maintenance reports
- ✅ **Violation Management System** - Record, list, and delete tenant violations with date tracking
- ✅ **Tenant Reminders System** - Send reminders to tenants (cleanliness, rules, payment, general)
- ✅ **Scheduled Reminders** - Schedule reminders for future delivery with datetime picker
- ✅ **Notification System** - Generic notification model for tenant alerts and system messages
- ✅ **Timer/Trigger Logic** - Django management command for sending scheduled reminders
- ✅ **Activity Logging for Reminders** - Track reminder creation and sending in activity feed
- ✅ **Dynamic Tenant Dropdowns** - Maintenance and violation modals now have dynamic tenant selection
- ✅ **Sidebar Navigation** - Fixed Maintenance and Violations links to point to actual pages
- ✅ **Non-Breaking Implementation** - All new features are modular and don't affect existing modules

**Previous Updates (April 27, 2026 - Late Night):**
- ✅ **Activity Logging System** - Added ActivityLog model for tracking user actions across the system
- ✅ **Activity Helper Functions** - Created activity_utils.py with log_activity, get_recent_activities helpers
- ✅ **Activity Template Tags** - Dynamic icons and colors for different activity types
- ✅ **Reusable Activity Feed** - Created activity_feed.html partial template for dashboards
- ✅ **Billing Activity Integration** - Activity logging for bill generation, edits, deletions, payments
- ✅ **Mobile Responsive Stats** - Stats cards display 3 per row on mobile with smaller fonts
- ✅ **Dashboard Mobile Fix** - Improved stat card layout for mobile devices
- ✅ **Billing View Template** - Added billing_view.html for detailed bill viewing
- ✅ **Forms Module** - Created forms.py for centralized form definitions
- ✅ **Fixed view_bill Function** - Restored missing view_bill view function

**Previous Updates (April 27, 2026 - Evening):**
- ✅ **Modal Stacking Fixes** - Fixed stuck backdrops and modal overlap issues
- ✅ **Global Backdrop Cleanup** - Automatic cleanup when no modals are open
- ✅ **Modal Instance Reuse** - Reuse Bootstrap instances instead of creating new ones
- ✅ **Profile Confirmation Lifecycle** - Improved modal management for profile edits
- ✅ **CSS Safety Net** - Added body overflow fix for orphaned modal states
- ✅ **Tenant Modal JavaScript** - Created dedicated tenant-modal.js for better organization
- ✅ **Room List Improvements** - Added bed count calculations and better formatting
- ✅ **Tenant Room Selection** - Simplified room details display (removed appliances section)
- ✅ **Code Formatting** - Improved consistency across JS and CSS files
- ✅ **Template Cleanup** - Better formatting in room_list.html and tenant_list.html

**Previous Updates (April 27, 2026 - Morning):**
- ✅ **AJAX Authentication Fixes** - Added @login_required to all API endpoints
- ✅ **Proper AJAX Headers** - X-Requested-With header for all fetch calls
- ✅ **JSON Error Responses** - Return JSON instead of HTML redirects for unauthorized requests
- ✅ **Phone Number Flexibility** - Changed phone field from BigIntegerField to CharField
- ✅ **Phone Number Parser** - Added parse_phone helper to clean phone numbers to digits
- ✅ **UI Consistency** - Improved role button styling (removed .active class dependency)
- ✅ **Code Cleanup** - Removed debug console.log statements from production code
- ✅ **Template Formatting** - Improved login.html readability and structure
- ✅ **Tenant Dashboard Security** - Fixed AnonymousUser error with proper authentication

**Previous Updates (April 24, 2026):**
- ✅ **Enhanced Navigation System** - Added breadcrumbs with active page highlighting (blue/bold)
- ✅ **Improved Room Layout** - Fixed 3 cards per row with proper Bootstrap g-4 spacing
- ✅ **Relocated Inclusions Button** - Moved from sidebar to room list header for better accessibility
- ✅ **Extended Add Room Modal** - Added dynamic inclusions and appliances functionality matching Edit Room
- ✅ **Fixed Template Issues** - Resolved duplications and syntax errors in room management
- ✅ **Dynamic Room Features System** - Added flexible inclusions and appliances management
- ✅ **Room Feature Management Page** - Centralized interface for managing room features
- ✅ **Edit Modal Enhancements** - Add/remove inclusions and appliances directly from room edit
- ✅ **Real-time Feature Updates** - Dynamic addition and removal of room features
- ✅ **Feature Management CRUD** - Complete create, read, update, delete operations
- ✅ **Reorganized static files structure** (centralized JS/CSS to root `static/` directory)
- ✅ Implemented Django `staticfiles/` with cache-busting (hash versioning)
- ✅ Secured `.env` file - removed from git tracking, added to `.gitignore`
- ✅ Created `.env.example` template for configuration reference
- ✅ Generated new SECRET_KEY (old one was exposed in version history)
- ✅ Updated template references to use new centralized paths
- ✅ Added `.gitignore` at project root level

**Previous Updates (March-April 2026):**
- Fixed profile modal password visibility toggle functionality
- Enhanced tenant profile section in login page
- Resolved JavaScript errors for role selection and eye icons
- Improved error handling across all JavaScript functions
- Added comprehensive null checks and try-catch blocks
- Enhanced user experience with better visual feedback

---

## 🗂️ Project Structure

```
rents_system/
│
├── manage.py
├── requirements.txt
├── .env                          ← environment variables (NOT in repo)
├── .env.example                  ← template for .env configuration
├── .gitignore                    ← defines what's excluded from git
│
├── static/                       ← CENTRALIZED static files (source)
│   ├── js/
│   │   ├── login.js
│   │   ├── login_fixed.js
│   │   ├── dashboard.js
│   │   └── profile-confirmation.js
│   └── css/
│       ├── dashboard.css
│       ├── avatar.css
│       └── modal-fix.css  
|       |__ base.css
|       |__ components.css
|       |__ layout.css
|       |___ pages
|           |__tenant_mobile.css
|
│
├── staticfiles/                  ← AUTO-GENERATED (NOT in repo)
│   ├── js/
│   │   ├── login.js
│   │   ├── login.[hash].js       ← versioned for cache-busting
│   │   └── ...
│   └── css/
│       ├── dashboard.css
│       ├── dashboard.[hash].css  ← versioned for cache-busting
│       └── ...
│
├── rents_system/                 ← project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── accounts/                     ← main app
    ├── migrations/
    ├── templates/
    │   ├── login.html
    │   ├── base_dashboard.html
    │   ├── admin/
    │   │   ├── dashboard.html
    │   │   ├── admin_list.html
    │   │   ├── tenant_list.html
    │   │   ├── room_list.html
    │   │   └── billing_list.html
    │   ├── tenant/
    │   │   └── dashboard.html
    │   ├── partials/
    │   │   ├── avatar.html
    │   │   └── sidebar.html
    │   └── registration/
    │       ├── password_reset_form.html
    │       └── ...
    │
    ├── views/                     ← MODULARIZED view components
    │   ├── __init__.py           ← backward compatibility
    │   ├── auth_views.py         ← login, signup, logout, profile
    │   ├── admin_views.py        ← admin CRUD operations
    │   ├── tenant_views.py       ← tenant CRUD operations
    │   ├── room_views.py         ← room CRUD, features
    │   ├── billing_views.py      ← billing, payments
    │   ├── maintenance_views.py  ← maintenance, violations
    │   ├── reminder_views.py     ← reminders, notifications
    │   └── helpers.py            ← shared helper functions
    │
    ├── templatetags/              ← custom template tags
    │   ├── __init__.py
    │   ├── avatar_tags.py         ← avatar display utilities
    │   ├── tenant_tags.py         ← tenant status tags
    │   └── json_filters.py        ← JSON processing filters
    │
    ├── context_processors.py      ← global context providers
    ├── activity_utils.py          ← activity logging utilities
    ├── forms.py                   ← centralized form definitions
    ├── models.py
    ├── views.py.backup           ← legacy views (backup)
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

### `accounts_inclusion`
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| name | VARCHAR | Inclusion name (unique) |
| created_at | DATETIME | Creation timestamp |

### `accounts_appliance`
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| name | VARCHAR | Appliance name (unique) |
| created_at | DATETIME | Creation timestamp |

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
| dynamic_inclusions | M2M | → accounts_inclusion |
| dynamic_appliances | M2M | → accounts_appliance |

### `accounts_activitylog`
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| user_id | FK | → auth_user (nullable) |
| action | VARCHAR | Action type (bill_generated, payment_recorded, etc.) |
| description | TEXT | Human-readable description |
| content_type | VARCHAR | Related model name (e.g., Bill, TenantProfile) |
| object_id | INT | ID of related object |
| timestamp | DATETIME | When the action occurred |

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
- **Login System**: Role toggle (Admin / Tenant) with enhanced JavaScript
- **Tenant Self-Signup**: Real-time room selection with detailed room information
- **Password Visibility Toggle**: Fixed for both login and signup forms
- **Profile Management**: Clickable profile sections with photo preview
- **Enhanced Security**: CSRF protection and session-based authentication
- **Smart Redirects**: Automatic redirect if already logged in
- **Improved Error Handling**: Comprehensive JavaScript error prevention
- **Mobile Responsive**: Optimized for all device sizes

### Room Management
- **Room Creation**: Add rooms with detailed specifications
- **Room Features**: Bed type, area, CR count, appliances, inclusions
- **Room Photos**: Upload and display room images
- **Room Sorting**: Sort by rate, capacity, floor, or room number
- **Real-time Availability**: Show occupied/available beds
- **Room Details Modal**: View complete room information
- **Vacant Badges**: Display available bed count
- **Room Codes**: Format like "Room 1-A", "Room 2-B"

### Dynamic Features Management
- **Centralized Management**: Dedicated "Features" page for managing inclusions and appliances
- **Flexible System**: Add custom inclusions (Water, Internet, Parking, etc.) and appliances (Microwave, Water Heater, etc.)
- **Room Integration**: Assign features to rooms via edit modal with checkboxes
- **Data Persistence**: Features saved to database and available across all rooms
- **Duplicate Prevention**: Smart handling of existing features

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

### Billing System
- **Bill Generation**: Create bills for tenants with period tracking
- **Bill Management**: Edit, delete, and mark bills as sent
- **Payment Recording**: Record payments with proof of payment
- **Payment Tracking**: View payment history and status
- **Activity Logging**: Track all billing-related actions
- **Recent Activity Feed**: Dynamic activity feed with icons and timestamps
- **Status Management**: Draft, sent, partial, paid, overdue statuses
- **Statistics Dashboard**: Real-time billing statistics

### Dashboard
- **Enhanced Stats**: Total tenants, vacant rooms, occupancy rate
- **Real-time Data**: Live bed availability calculations
- **Recent Activity**: Recent tenants and room updates
- **Visual Indicators**: Progress bars for occupancy
- **Dark sidebar navigation**
- **Mobile responsive** (Pixel 7 optimized)
- **Clickable stat cards** with navigation

### User Experience
- **Modern UI**: Clean, professional interface with dark sidebar
- **Responsive Design**: Works on all devices (Pixel 7 optimized)
- **Interactive Elements**: Dynamic room details display with real-time updates
- **Visual Feedback**: Loading states, hover effects, and smooth transitions
- **Enhanced Error Handling**: Comprehensive JavaScript error prevention
- **Accessibility**: Semantic HTML, ARIA labels, and keyboard navigation
- **Profile Integration**: Clickable profile sections with photo management
- **Password Management**: Secure password visibility toggles with proper validation

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

Copy `.env.example` and fill in your values:
```bash
cp .env.example .env
```

```
SECRET_KEY=your_secret_key_here
DEBUG=True
DB_NAME=rents_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

⚠️ **IMPORTANT**: Never commit `.env` to git. It should be in `.gitignore`

### 4. Create MySQL database
```sql
CREATE DATABASE rents_db;
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Collect static files
```bash
python manage.py collectstatic --noinput
```

### 7. Create Superadmin
```bash
python manage.py createsuperuser
```

### 8. Seed Initial Features (Optional)
```bash
python manage.py seed_inclusions_appliances
```
This creates default inclusions (Water, Electricity, Internet, etc.) and appliances (Fan, Air Conditioner, Microwave, etc.)

### 9. Run the server
```bash
python manage.py runserver
```

### 10. Open in browser
```
http://127.0.0.1:8000/
```

---

## � Static Files Management

### Understanding `static/` vs `staticfiles/`

**`static/` directory** (source - what you edit)
- Where you write and edit `.js`, `.css`, and other static files
- Always committed to git
- Should be edited directly during development

**`staticfiles/` directory** (generated - production-ready)
- Auto-generated by `python manage.py collectstatic`
- Contains versioned files with cache-busting hashes (e.g., `login.78bc3e5a20d3.js`)
- **NEVER** manually edited or committed to git
- Ignored by `.gitignore`

### Development Workflow

```bash
# 1. Edit your static files
nano static/js/login.js

# 2. Collect static files (generates versioned copies)
python manage.py collectstatic --noinput

# 3. Test locally
python manage.py runserver

# 4. Commit changes
git add static/
git commit -m "Update login.js functionality"
git push origin dev
```

---

## 🔐 Security & Environment Configuration

### Configuration Files

| File | Location | Git Tracked | Purpose |
|---|---|---|---|
| `.env` | Root | ❌ NO | Your actual secrets (never commit) |
| `.env.example` | Root | ✅ YES | Template for other developers |
| `.gitignore` | Root | ✅ YES | Defines what to exclude from git |

### Best Practices

1. **Never commit `.env`** - always ensure it's in `.gitignore`
2. **Use `.env.example`** - provide template for configuration
3. **Regenerate SECRET_KEY** if compromised - use `python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
4. **Different keys per environment** - dev, staging, production should have different SECRET_KEYs
5. **On production servers** - manually create `.env` file with production credentials

---

## �🛠️ Tech Stack

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

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django cryptographic key (keep secure!) | `3ot&+cue4i760gjrayixr!1a3tq_%h#...` |
| `DEBUG` | True (local) / False (production) | `True` |
| `DB_NAME` | Database name | `rents_db` |
| `DB_USER` | Database user | `root` |
| `DB_PASSWORD` | Database password | (leave empty for local dev) |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `3306` |
| `EMAIL_HOST` | SMTP server for emails | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS encryption | `True` |
| `EMAIL_HOST_USER` | Email account for sending | `your_email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Email app password | (your app password) |
| `DEFAULT_FROM_EMAIL` | Default "from" email | `RENTS System <email@example.com>` |

---

## 👨‍💻 Developer

**Kevin Bueno** — RENTS System  
GitHub: [@KevzBueno101](https://github.com/KevzBueno101)
