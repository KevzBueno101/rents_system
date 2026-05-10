# RENTS - Residents Entry, Navigation, and Tenant Tracking System

A Django-based boarding house management system for managing tenants, rooms, billing, maintenance, and violations.

## Current Status: **Production Ready** v3.2

**Refactor Highlights (May 10, 2026):**
- Room media now supports modern modal galleries with arrows, counters, keyboard navigation, swipe support, and smooth image transitions.
- Room uploads are organized into per-room folders such as `media/rooms/Room_1-A/primary.jpg`, `1.jpg`, and `2.jpg`.
- `room.all_images` provides one ordered image source for primary photos, additional photos, cards, details modals, and future gallery views.
- `migrate_room_media` can dry-run or migrate existing room images into the new directory structure without breaking existing records.
- The tenant login page now uses a full-bleed, grayscale rental SaaS layout aligned with the landing page styling.

**Latest Updates (May 10, 2026):**
- ✅ **Room Details Modal System** - Interactive modal for room information on home page
- ✅ **Building Background Implementation** - Professional building photo with dark overlay
- ✅ **Mobile Responsive Background** - Optimized background display for all devices
- ✅ **Enhanced User Experience** - Consistent modal behavior across all pages
- ✅ **Template Syntax Fixes** - Resolved Django template parsing errors
- ✅ **Role-Based Access Control (RBAC) System** - Comprehensive role management with decorators and middleware
- ✅ **Security Middleware Implementation** - Admin login protection and security headers
- ✅ **Marketing Views and Landing Page** - Professional landing page with hero section and navigation
- ✅ **Activity Logging and Audit Trail** - Complete tracking system for all user actions
- ✅ **Forgot Password Functionality** - Full password reset flow with email integration
- ✅ **Notification System** - Real-time notifications with user isolation and type-based routing
- ✅ **Reminder System** - Scheduled reminders with delivery tracking and tenant targeting
- ✅ **Admin Login Template** - Dark-themed admin login interface with enhanced security
- ✅ **URL Configuration System** - Modular URL routing with centralized configuration
- ✅ **Utility Functions** - Helper functions for common operations and data processing
- ✅ **Enhanced Security** - CSRF protection, session management, and input validation
- ✅ **Mobile Responsive Design** - Optimized for all device sizes with touch interactions
- ✅ **Performance Optimization** - Database indexes and efficient queries for scalability
- ✅ **Code Organization** - Modular architecture with clear separation of concerns
- ✅ **Git Repository Management** - Proper version control with meaningful commit messages

**Previous Updates (May 8, 2026):**
- ✅ **Critical Violation Routing Fix** - Resolved data routing issue where violation reports were incorrectly saved as maintenance entries
- ✅ **Dedicated Violation Submission** - Added separate violation submission modal with date field and proper endpoint routing
- ✅ **Tab-Aware Modal Selection** - Implemented intelligent modal selection based on active tab (maintenance vs violations)
- ✅ **Mobile Responsive Modals** - Enhanced modal responsiveness with scrollable dialogs for mobile devices
- ✅ **Proper Model Separation** - Ensured strict data separation between MaintenanceReport and Violation models
- ✅ **Non-Breaking Implementation** - Fixed critical bug while preserving all existing functionality
- ✅ **Pay Now Button in My Bills Page** - Added one-click payment access from bills list with modal integration
- ✅ **Complete Modal Integration** - Implemented full Pay Now modal with phone display and payment proof upload in bills page
- ✅ **Dynamic Admin Contact** - Removed hardcoded phone numbers with proper superadmin profile integration
- ✅ **Streamlined Payment Workflow** - Enhanced user experience with direct payment access from bills management
- ✅ **Secure Payment Proof Upload System** - Implemented tenant payment screenshot upload with validation and admin notifications
- ✅ **Copy-to-Clipboard Functionality** - Added one-click GCash number copying with visual feedback
- ✅ **Mobile-Responsive Upload Interface** - Created touch-friendly payment proof upload modal with image preview
- ✅ **Enhanced Security Validation** - File type validation (JPG, PNG, WebP) and 5MB size limits
- ✅ **Admin Notification System** - Automatic admin alerts when tenants upload payment proofs
- ✅ **Activity Logging Integration** - Complete audit trail for payment proof uploads
- ✅ **AJAX Form Handling** - Modern asynchronous upload with loading states and error handling
- ✅ **Non-Destructive Database Implementation** - Extended existing Payment model without schema changes
- ✅ **Mobile Sidebar Overlay Fixes** - Resolved overlay dismissal issues with proper z-index and event handling
- ✅ **Responsive Sidebar Behavior** - Fixed CSS conflicts preventing proper mobile sidebar hide/show functionality
- ✅ **Enhanced Hamburger Menu** - Improved mobile navigation toggle visibility and touch interactions
- ✅ **Mobile Bottom Navigation** - Updated tenant bottom navigation grid layout for better mobile UX
- ✅ **Mobile Profile Display** - Enhanced user profile display in mobile sidebar with role information
- ✅ **CSS Cleanup** - Removed redundant overrides causing mobile responsiveness conflicts
- ✅ **Touch Interaction Improvements** - Enhanced mobile touch events and transitions across all components
- ✅ **Responsive Breakpoint Optimization** - Improved mobile breakpoints for seamless device compatibility

**Previous Updates (May 6, 2026):**
- ✅ **Comprehensive Rules Management System** - Complete CRUD operations for Admins and read-only access for Tenants
- ✅ **Real-Time Rules Synchronization** - API endpoint with caching for immediate rule updates across all dashboards
- ✅ **Professional Admin Interface** - Modal-based rule creation/editing with search and filter functionality
- ✅ **Enhanced Tenant Experience** - Clean card-based rules display with pagination and proper navigation
- ✅ **Activity Logging & Audit Trail** - Complete tracking of all rule modifications for compliance
- ✅ **Sidebar Display Fixes** - Resolved logo and profile display issues with aggressive CSS overrides
- ✅ **Context Processors Resolution** - Fixed missing processors (recent_payments, notifications, app_settings)
- ✅ **Template Syntax Corrections** - Fixed resolver-match errors and URL routing issues
- ✅ **Dynamic Rule Management** - Centralized database-driven system replacing hardcoded rules
- ✅ **Scalable Architecture** - Production-ready system supporting unlimited rules and tenants
- ✅ **Git Repository Migration** - Successfully pushed to dev branch with new remote location

**Previous Updates (May 5, 2026):**
- ✅ **Real-Time Dashboard Synchronization** - Complete real-time data synchronization system for tenant dashboard
- ✅ **JavaScript Polling System** - 10-second interval polling with intelligent change detection
- ✅ **API Endpoints for Dashboard** - RESTful API endpoints for real-time dashboard data delivery
- ✅ **Cache Invalidation System** - Automatic cache updates on bill/payment changes
- ✅ **Template Data Attributes** - Enhanced templates with data attributes for JavaScript targeting
- ✅ **Django Import Errors Fixed** - Resolved NameError and AttributeError preventing server startup
- ✅ **Template Syntax Errors Fixed** - Fixed static tag loading and JavaScript file path issues
- ✅ **Enhanced Dashboard Service** - Unified data source with accurate calculations and caching
- ✅ **Real-Time UI Components** - Stats cards and bills details update without page refresh
- ✅ **Error Handling & Retry Logic** - Robust error handling with automatic retry mechanisms
- ✅ **Cross-Tab Synchronization** - Dashboard updates sync across multiple browser tabs
- ✅ **Performance Optimization** - Efficient data hashing to prevent unnecessary updates
- ✅ **Shared Room Card Component** - Created reusable room card component for admin and tenant dashboards
- ✅ **Unified Room Layout** - Tenant rooms now inherit professional Bootstrap card layout from admin
- ✅ **Room Info Modal Functionality** - Added clickable info icons with detailed room information modal
- ✅ **Template Error Resolution** - Fixed json_attr filter issues and template syntax errors

**Previous Updates (May 4, 2026):**
- ✅ **SendGrid API Email Delivery** - Implemented SendGrid API for reliable email delivery on Render
- ✅ **Email Delivery Chain** - SendGrid API → SMTP → Console fallback for maximum reliability
- ✅ **Render Deployment Ready** - Fixed 500 errors and ensured actual email delivery on production
- ✅ **Production Email System** - Complete email delivery system with robust error handling
- ✅ **Environment Variable Configuration** - Proper setup for SendGrid API keys and email settings
- ✅ **Comprehensive Logging** - Enhanced error tracking and debugging for email delivery
- ✅ **Complete Password Reset System** - Fully functional forgot password flow with email integration
- ✅ **Password Reset Email Templates** - HTML and plain text email templates with proper reset links
- ✅ **Function-Based Reset View** - Custom implementation bypassing Django authentication middleware
- ✅ **AJAX Password Reset Handling** - Fixed JavaScript to handle Django 302 redirects properly
- ✅ **Template Structure Fixes** - Fixed password reset confirm template to be standalone
- ✅ **Tenant Dashboard Template Fix** - Corrected template path for tenant dashboard access
- ✅ **Mobile Billing Cards System** - Collapsible cards for tenant bills with mobile-optimized layout
- ✅ **Responsive Billing Stats** - 2x3 grid layout for mobile billing statistics cards
- ✅ **Mobile Profile Enhancement** - Click-to-edit mobile profile with dynamic photo display
- ✅ **Mobile Sidebar Improvements** - Proper positioning and styling for mobile devices
- ✅ **Mobile Device Detection** - Automatic template switching based on device type
- ✅ **Horizontal Scrollable Tables** - Mobile-friendly table scrolling for admin billing
- ✅ **URL Pattern Fixes** - Corrected mobile billing action URLs to prevent 404 errors
- ✅ **GitIgnore Enhancement** - Excluded local test files from version control

**Previous Updates (May 2, 2026 - Evening):**
- ✅ **Event-Driven Notification System** - Comprehensive notification system with user isolation and security
- ✅ **Centralized Notification Service** - Reusable API for creating notifications across the system
- ✅ **Admin Trigger Integration** - Auto-notifications for payment, billing, and maintenance updates
- ✅ **Dynamic Routing System** - Type-based redirects (payment→billing, maintenance→reports)
- ✅ **Security-First Design** - User isolation enforced at database level with audit logging
- ✅ **Performance Optimization** - Database indexes and efficient queries for scalability
- ✅ **Comprehensive Testing** - 100% test coverage with automated test suite

**Previous Updates (May 2, 2026 - Morning):**
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
    │   ├── api_views.py          ← API endpoints for real-time sync
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

├── services/                    ← Business logic services
    │   ├── user_service.py        ← User management utilities
    │   ├── notification_service.py ← Notification system
    │   └── dashboard_service.py   ← Real-time dashboard data

├── templates/                   ← Template files
    │   ├── tenant/
    │   │   ├── components/
    │   │   │   ├── real_time_sync.js ← Real-time synchronization
    │   │   │   ├── summary_cards.html
    │   │   │   ├── payment_overview.html
    │   │   │   └── ...
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

### `accounts_notification` (NEW)
| Field | Type | Description |
|---|---|---|
| id | INT | Primary key |
| user_id | FK | → auth_user (tenant) |
| title | VARCHAR | Notification title |
| message | TEXT | Notification message |
| link | VARCHAR | Internal URL path for redirect |
| type | VARCHAR | Notification type (payment, billing, maintenance, etc.) |
| is_read | BOOL | Read status (default: False) |
| created_at | DATETIME | Creation timestamp |

---

## 👥 User Roles

| Role | is_staff | is_superuser | Access |
|---|---|---|---|
| **Superadmin** | ✅ | ✅ | Full access + Register Admins |
| **Admin** | ✅ | ❌ | Manage tenants, rooms, billing |
| **Tenant** | ❌ | ❌ | View own profile, bills, reports |

---

## ✅ Features (Current)

### Authentication & Security
- **Role-Based Access Control (RBAC)**: Comprehensive role management with decorators and middleware
- **Security Middleware**: Admin login protection, security headers, and session management
- **Login System**: Role toggle (Admin / Tenant) with enhanced JavaScript
- **Dedicated Admin Login**: Separate admin login interface with dark theme and enhanced security
- **Tenant Self-Signup**: Real-time room selection with detailed room information
- **Password Reset System**: Complete forgot password flow with email integration
- **Email Templates**: HTML and plain text password reset emails with clickable links
- **Token Validation**: Secure token-based password reset with expiration
- **AJAX Handling**: Proper handling of Django redirects in password reset forms
- **Password Visibility Toggle**: Fixed for both login and signup forms
- **Profile Management**: Clickable profile sections with photo preview
- **Enhanced Security**: CSRF protection, session-based authentication, and input validation
- **Smart Redirects**: Automatic redirect if already logged in
- **Improved Error Handling**: Comprehensive JavaScript error prevention
- **Mobile Responsive**: Optimized for all device sizes

### Marketing & Landing Page
- **Professional Landing Page**: Modern hero section with call-to-action buttons
- **Marketing Views**: Dedicated views for marketing and promotional content
- **Hero Graphics**: Custom SVG illustrations and professional imagery
- **Navigation Components**: Responsive navigation with mobile menu support
- **Brand Identity**: Consistent branding across all marketing materials
- **Call-to-Action**: Strategic placement of signup and login buttons
- **Mobile Optimization**: Fully responsive design for all marketing pages

### Activity Logging & Audit Trail
- **Comprehensive Activity Tracking**: Log all user actions across the system
- **Audit Trail System**: Complete tracking of tenant, admin, and system actions
- **Activity Feed**: Real-time activity display with icons and timestamps
- **Security Monitoring**: Track login attempts, failed authentications, and access patterns
- **User Action History**: Detailed history of all user interactions
- **System Event Logging**: Automatic logging of system events and errors
- **Performance Monitoring**: Track response times and system performance metrics

### Notification System
- **Real-Time Notifications**: Instant notifications for important events
- **User Isolation**: Tenants only see their own notifications (security enforced)
- **Type-Based Routing**: Smart routing based on notification type
- **Email Integration**: Email notifications for critical events
- **Notification History**: Complete history of all notifications sent
- **Read Status Tracking**: Track which notifications have been read
- **Mobile Notifications**: Push notifications for mobile devices
- **Customizable Alerts**: Configurable notification preferences per user

### Reminder System
- **Scheduled Reminders**: Set reminders for future delivery
- **Tenant Targeting**: Send reminders to specific tenants or groups
- **Reminder Types**: Support for different reminder categories (cleanliness, rules, payment, etc.)
- **Delivery Tracking**: Track when reminders are sent and received
- **Automated Delivery**: Django management command for automated reminder sending
- **Reminder History**: Complete history of all reminders sent
- **Customizable Templates**: Configurable reminder templates
- **Mobile-Friendly**: Optimized for mobile device delivery

### Email System Configuration
- **SendGrid API Integration**: Primary email delivery via SendGrid API for production reliability
- **Email Delivery Chain**: SendGrid API → SMTP → Console fallback for maximum reliability
- **Render Deployment Ready**: Optimized for cloud deployment with automatic fallback handling
- **Production Email System**: Complete email delivery system with robust error handling
- **Smart Backend Selection**: Automatic backend selection based on environment and credentials
- **Comprehensive Logging**: Enhanced error tracking and debugging for email delivery
- **Email Templates**: Professional HTML and plain text email templates with reset links
- **Security**: Secure token-based password reset with 24-hour expiration
- **Environment Variables**: Configurable email settings via environment variables

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
- **Mobile Billing Cards**: Collapsible cards for mobile bill viewing with expandable details
- **Responsive Billing Stats**: 2x3 grid layout optimized for mobile devices
- **Mobile Device Detection**: Automatic template switching for mobile users
- **Horizontal Scrollable Tables**: Mobile-friendly table scrolling for admin billing

### Notification System (NEW)
- **Event-Driven Architecture**: Automatic notifications on admin actions
- **User Isolation**: Tenants only see their own notifications (security enforced)
- **Centralized Service**: Reusable API for creating notifications system-wide
- **Dynamic Routing**: Type-based redirects (payment→billing, maintenance→reports)
- **Admin Triggers**: Auto-notifications for payment, billing, and maintenance updates
- **Bell UI**: Modern notification bell with unread badge counter
- **Click-to-Read**: Mark notifications as read and redirect to relevant pages
- **Security First**: Database-level isolation with comprehensive audit logging
- **Performance Optimized**: Database indexes and efficient queries
- **Comprehensive Testing**: 100% test coverage with automated test suite

**Notification Types:**
- **Payment**: When admin records a payment → redirects to billing page
- **Billing**: When new bill is generated → redirects to billing page  
- **Maintenance**: When maintenance status is updated → redirects to reports page
- **Announcement**: System announcements → redirects to dashboard
- **System**: General system notifications → redirects to dashboard

### Real-Time Dashboard Synchronization (NEW)
- **Live Data Updates**: Automatic dashboard updates without page refresh
- **JavaScript Polling System**: 10-second interval polling with intelligent change detection
- **API Endpoints**: RESTful API endpoints for real-time dashboard data delivery
- **Cache Invalidation**: Automatic cache updates on bill/payment changes
- **Cross-Tab Synchronization**: Dashboard updates sync across multiple browser tabs
- **Error Handling**: Robust error handling with automatic retry mechanisms
- **Performance Optimization**: Efficient data hashing to prevent unnecessary updates
- **Template Integration**: Data attributes for JavaScript targeting
- **Visual Feedback**: Real-time sync indicators and status updates
- **Mobile Responsive**: Real-time updates work on all device sizes

#### Real-Time Features
- **Stats Cards**: Current balance, due date, payment status update in real-time
- **Payment Overview**: Latest payments and total paid amounts update automatically
- **Bill Details**: Bill status and payment progress update without refresh
- **Notification Count**: Unread notification counter updates instantly
- **Room Information**: Room details and availability update dynamically

#### API Endpoints
| Endpoint | Method | Description | Authentication |
|---|---|---|---|
| `/api/tenant/dashboard-data/` | GET | Real-time dashboard data | @login_required |
| `/api/force-dashboard-refresh/` | POST | Force dashboard refresh | @login_required |

#### JavaScript Integration
```javascript
// Automatic initialization
window.dashboardSync = new DashboardSync();

// Manual refresh
window.forceDashboardUpdate();
```

### Dashboard
- **Enhanced Stats**: Total tenants, vacant rooms, occupancy rate
- **Real-time Data**: Live bed availability calculations
- **Recent Activity**: Recent tenants and room updates
- **Visual Indicators**: Progress bars for occupancy
- **Dark sidebar navigation**
- **Mobile responsive** (Pixel 7 optimized)
- **Clickable stat cards** with navigation
- **Real-time synchronization** with automatic updates

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

## 🔄 Real-Time Dashboard Synchronization API

### DashboardService API

The `DashboardService` provides centralized data management for real-time dashboard updates.

#### Basic Usage

```python
from tenant.services.dashboard_service import DashboardService

# Get unified dashboard data
dashboard_data = DashboardService.get_tenant_dashboard_data(
    user=request.user,
    force_refresh=True  # Optional: bypass cache
)
```

#### Response Structure

```json
{
    "tenant": {
        "id": 1,
        "full_name": "John Doe",
        "room": {
            "room_number": "A-101",
            "monthly_rate": 5000.00
        }
    },
    "balance": 1500.00,
    "due_date": "2026-05-15",
    "payment_status": "partial",
    "payment_status_label": "Partial Payment",
    "latest_payment": {
        "amount": 2000.00,
        "payment_date": "2026-05-01",
        "payment_method": "cash"
    },
    "summary": {
        "total_bills": 3,
        "paid_bills": 1,
        "total_paid": 2000.00,
        "next_bill": {
            "due_date": "2026-05-15",
            "amount": 3500.00
        },
        "is_overdue": false,
        "days_until_due": 10
    },
    "enhanced_status": {
        "total_bills": 3,
        "paid_bills": 1,
        "pending_bills": 2,
        "has_overdue": false,
        "has_urgent_payment": false
    },
    "notifications": [...],
    "unread_notifications": 2
}
```

### API Endpoints

| Endpoint | Method | Description | Authentication | Cache |
|---|---|---|---|---|
| `/api/tenant/dashboard-data/` | GET | Real-time dashboard data | @login_required | 10 min |
| `/api/force-dashboard-refresh/` | POST | Force cache invalidation | @login_required | Instant |

#### JavaScript Integration

```javascript
// Automatic initialization (included in template)
window.dashboardSync = new DashboardSync();

// Manual refresh
window.forceDashboardUpdate();

// Listen for updates
window.addEventListener('dashboard-data-updated', (event) => {
    console.log('Dashboard updated:', event.detail);
});
```

### Cache Management

#### Cache Keys
- `tenant_dashboard_{user_id}` - User-specific dashboard data
- `dashboard_stats_{user_id}` - User-specific statistics

#### Cache Invalidation
- Automatic on bill creation/update/delete
- Automatic on payment recording
- Manual via force refresh endpoint

#### Performance Features
- **Change Detection**: Data hashing prevents unnecessary updates
- **Intelligent Polling**: 10-second intervals with visibility API optimization
- **Cross-Tab Sync**: Updates propagate across browser tabs
- **Error Recovery**: Automatic retry with exponential backoff

### Template Data Attributes

```html
<!-- Stats Cards -->
<div data-balance="current">
    <span class="metric-value">{{ balance }}</span>
</div>

<div data-balance="due-date">
    <span class="metric-value">{{ due_date }}</span>
</div>

<div data-balance="payment-status">
    <span class="metric-value">{{ payment_status_label }}</span>
</div>

<!-- Payment Overview -->
<div data-latest-payment>
    <strong>{{ latest_payment.payment_date }}</strong>
</div>

<div data-total-paid>
    <strong>{{ summary.total_paid }}</strong>
</div>

<div data-remaining-balance>
    <strong>{{ balance }}</strong>
</div>
```

---

## 📊 Dashboard Service Architecture

### Data Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Layer      │    │   Service       │
│                 │    │                  │    │                 │
│ JavaScript      │───▶│ api_views.py     │───▶│ DashboardService│
│ Polling (10s)   │    │                  │    │                 │
│ UI Updates      │    │ JSON Response    │    │ Cache Layer     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   URL Routing    │    │   Database      │
                       │                  │    │                 │
                       │ urls.py          │    │ Models:         │
                       │                  │    │ - Bill          │
                       └──────────────────┘    │ - Payment       │
                                                │ - Tenant        │
                                                └─────────────────┘
```

### Service Methods

```python
# Main data aggregation
DashboardService.get_tenant_dashboard_data(user, force_refresh=False)

# Cache management
DashboardService.invalidate_user_cache(user_id)
DashboardService.get_cache_key(user_id)

# Data helpers
DashboardService._calculate_balance(tenant)
DashboardService._get_payment_summary(tenant)
DashboardService._get_enhanced_status(tenant)
```

### Error Handling

- **Network Errors**: Automatic retry with exponential backoff
- **Server Errors**: Graceful degradation with cached data
- **Authentication**: Proper login_required enforcement
- **Data Validation**: Comprehensive error checking

---

## Notification System API

### NotificationService API

The `NotificationService` provides a centralized API for creating notifications throughout the system.

#### Basic Usage

```python
from accounts.services.notification_service import NotificationService

# Create a basic notification
notification = NotificationService.create_notification(
    user=tenant_user,
    title="Custom Notification",
    message="This is a custom notification",
    link="/tenant/custom-page/",
    notif_type="system"
)
```

#### Helper Methods

```python
# Payment notification
NotificationService.create_payment_notification(
    tenant_user=user,
    amount=1500.00  # Optional
)

# Billing notification
NotificationService.create_billing_notification(
    tenant_user=user,
    bill_number="BILL-2025-00001"  # Optional
)

# Maintenance notification
NotificationService.create_maintenance_notification(
    tenant_user=user,
    status="completed"  # Optional
)

# Announcement notification
NotificationService.create_announcement_notification(
    tenant_user=user,
    announcement_title="System Maintenance"  # Optional
)
```

#### Query Methods

```python
# Get user notifications with unread count
notifications, unread_count = NotificationService.get_user_notifications(
    user=request.user,
    limit=10
)

# Mark notification as read (secure)
success = NotificationService.mark_as_read(
    notification_id=123,
    user=request.user
)

# Mark all notifications as read
count = NotificationService.mark_all_as_read(user=request.user)
```

### URL Endpoints

| Endpoint | Method | Description | Security |
|---|---|---|---|
| `/notification/<int:notif_id>/mark-read/` | GET | Mark notification as read and redirect | User isolation enforced |

### Template Integration

The notification system is automatically available in templates via context processor:

```html
<!-- Notification Bell with Badge -->
<button class="btn btn-light position-relative" id="notifBtn">
    <i class="bi bi-bell-fill"></i>
    {% if unread_count > 0 %}
    <span class="badge bg-danger">{{ unread_count }}</span>
    {% endif %}
</button>

<!-- Notification Dropdown -->
{% for notif in notifications %}
    <a href="{% url 'mark_notification' notif.id %}">
        {{ notif.title }} - {{ notif.message }}
    </a>
{% endfor %}
```

### Security Features

- **User Isolation**: Users can only access their own notifications
- **Database Indexes**: Optimized queries for performance
- **Audit Logging**: All notification interactions are logged
- **Error Handling**: Graceful failure modes that don't break core functionality

---

## 🚧 Features (Planned)

- [ ] Real-time Notifications (WebSockets)
- [ ] Email Notification Fallback
- [ ] Push Notifications (Mobile)
- [ ] Notification Categories
- [ ] "Mark All as Read" Button
- [ ] Notification Scheduling
- [ ] Room Search & Filtering - advanced room search capabilities
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

# Production-only (required when DEBUG=False)
# IMPORTANT: ALLOWED_HOSTS must be hostnames only (no https://)
ALLOWED_HOSTS=your-app.onrender.com

# Public base URL used in password reset emails
SITE_URL=https://your-app.onrender.com

# Email Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=your_verified_email@domain.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

⚠️ **IMPORTANT**: Never commit `.env` to git. It should be in `.gitignore`

### 🚀 Render Deployment Setup

#### Email Configuration for Production
1. **Go to Render Dashboard** → Your RENTS application → **Environment** tab
2. **Add these environment variables**:
   ```
   DEBUG=False
   SECRET_KEY=your_secret_key_here
   ALLOWED_HOSTS=your-app.onrender.com
   SITE_URL=https://your-app.onrender.com
   SENDGRID_API_KEY=your_sendgrid_api_key_here
   FROM_EMAIL=your_verified_email@domain.com
   ```
3. **Click "Save Changes"** and **"Manual Deploy"**

#### Email Delivery Priority on Render
- **Primary**: SendGrid API (most reliable)
- **Fallback**: SendGrid SMTP (if API fails)
- **Final**: Console backend (for debugging)

#### Expected Behavior
- ✅ **Password reset form works** without 500 errors
- ✅ **Emails sent to user inboxes** via SendGrid API
- ✅ **Robust fallback** if primary method fails
- ✅ **Comprehensive logging** for debugging
 - ✅ **Forgot password modal** returns accurate success/error (AJAX uses JSON)

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

### 9. Test Real-Time Dashboard Synchronization (Recommended)
```bash
python manage.py test_dashboard_sync --verbose
```
This runs comprehensive tests for the real-time dashboard system including:
- API endpoint functionality
- Cache invalidation mechanisms
- Data synchronization accuracy
- Error handling and retry logic
- Performance optimization testing
- Cross-tab synchronization

### 10. Test Notification System (Recommended)
```bash
python manage.py test_notification_system --verbose
```
This runs comprehensive tests for the notification system including:
- User isolation (security testing)
- Dynamic routing (redirect testing)
- Admin trigger integration (payment, billing, maintenance)
- Security validation
- Performance testing

### 11. Run the server
```bash
python manage.py runserver
```

### 12. Open in browser
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
| `ALLOWED_HOSTS` | Comma-separated hostnames allowed (required when DEBUG=False) | `your-app.onrender.com,www.example.com` |
| `SITE_URL` | Public base URL for outbound links (password reset emails) | `https://your-app.onrender.com` |
| `DB_NAME` | Database name | `rents_db` |
| `DB_USER` | Database user | `root` |
| `DB_PASSWORD` | Database password | (leave empty for local dev) |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `3306` |
| `SENDGRID_API_KEY` | SendGrid API key for production email delivery | (your SendGrid API key) |
| `FROM_EMAIL` | Verified sender email used for outbound mail | `noreply@yourdomain.com` |
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
