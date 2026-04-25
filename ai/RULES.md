# 🏠 RENTS – Boarding House Management System

## 📌 Overview

RENTS is a Django-based web application designed to manage boarding house operations such as tenant records, room assignments, and administrative workflows.

This project follows Django's **MVT (Model–View–Template)** architecture and is structured into modular apps.

---

## 🎯 Core Features

* Tenant Management (Add, View, Update, Delete)
* Room Management
* Image Upload (Room photos, tenant data)
* Authentication (Admin/User login)
* Dashboard for monitoring

---

## 🛠️ Tech Stack

* Backend: Django (Python)
* Database: MySQL
* Frontend: HTML, CSS, Bootstrap
* Media Handling: Django Media Files
* Deployment Target: (Optional) Oracle Cloud / Render

---

## 📁 Project Structure (High-Level)

```
rents_system/
│
├── accounts/        # Authentication, admin profiles
├── tenants/         # Tenant-related logic
├── rooms/           # Room management
├── templates/       # HTML templates
├── static/          # CSS, JS, assets
├── media/           # Uploaded files (images)
├── manage.py
└── settings.py
```

---

## 🧠 Architecture Overview

### Django MVT Flow

1. URL → routes request to a View
2. View → processes logic and interacts with Models
3. Model → handles database operations (MySQL)
4. Template → renders UI response

---

## 🔄 Data Flow Example

Tenant Creation Flow:

```
User submits form → View (POST) → Model (save to DB) → Redirect → Tenant List (GET)
```

---

## ⚠️ CRITICAL SYSTEM COMPONENTS (DO NOT BREAK)

* Authentication system (login/logout, sessions)
* Database schema (models & migrations)
* Media file handling (`MEDIA_URL`, `MEDIA_ROOT`)
* URL routing structure
* Existing working CRUD features

---

## 🤖 AI ASSISTED DEVELOPMENT RULES (STRICT)

### 🔍 1. Always Analyze Before Coding

AI MUST:

* Read this README completely
* Analyze project structure
* Understand app responsibilities
* Identify dependencies

❗ DO NOT generate code immediately

---

### 🧱 2. Respect Existing Architecture

* Follow Django MVT pattern
* Do NOT introduce new architecture unless requested
* Keep logic consistent with current structure

---

### ⚠️ 3. Safe Modification Policy

AI MUST:

* Avoid modifying working features
* Avoid rewriting entire files
* Prefer **additive changes (extend, not replace)**

If unsure:
👉 STOP and ask for clarification

---

### 🔗 4. Dependency Awareness

Before any change:

* Check affected apps
* Check related models/views/templates
* Evaluate side effects

---

### 🧪 5. Change Planning (REQUIRED)

Before coding, AI must output:

1. What files will be modified
2. What logic will be added
3. Why it is safe

Then WAIT for user approval

---

### 💻 6. Coding Standards

* Follow existing code style
* Keep functions small and readable
* Avoid unnecessary complexity
* Ensure MySQL compatibility
* Avoid breaking migrations

---

### 🔁 7. After Code Generation

AI must:

* Explain changes clearly
* Identify risks
* Provide manual testing steps

---

### 🚫 STRICT PROHIBITIONS

AI MUST NOT:

* Perform blind refactoring
* Modify unrelated modules
* Break authentication or database
* Assume missing logic without checking
* Over-engineer solutions

---

## 🧩 Development Guidelines

### ✔️ When Adding Features

* Extend existing views/models where appropriate
* Reuse templates/components
* Keep UI consistent (Bootstrap-based)

---

### ✔️ When Modifying Features

* Identify all dependencies first
* Avoid breaking existing routes and templates

---

### ✔️ When Working with Forms

* Always include CSRF protection
* Validate input properly
* Use Django forms or clean methods if applicable

---

## 🗄️ Database Notes (MySQL)

* Ensure proper field types
* Avoid destructive migrations
* Backup before major schema changes

---

## 📦 Media & Static Files

* Media files stored in `/media/`
* Static files stored in `/static/`
* Ensure proper configuration in production

---

## 🧪 Testing Checklist (Manual)

Before marking a feature as complete:

* [ ] Page loads without error
* [ ] Form submission works (POST → Redirect)
* [ ] Data saved correctly in database
* [ ] UI renders properly
* [ ] No existing feature is broken

---

## 🚀 Future Improvements

* Reporting & analytics
* Payment tracking
* Role-based access control
* API integration (Django REST Framework)

---

## 📣 Instructions for AI Assistants

Before responding to ANY request:

1. Analyze system based on this README
2. Identify affected components
3. Provide a plan
4. Wait for approval
5. Then generate code

👉 Your role is to **maintain system stability**, not just generate code.

---

## 👨‍💻 Developer Notes

This project is actively developed with AI-assisted programming tools.
Strict adherence to structure and rules is required to prevent regressions.
