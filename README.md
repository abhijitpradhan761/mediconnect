# MediConnect — Full-Stack Healthcare Management Platform

![MediConnect Banner](https://img.shields.io/badge/Platform-MediConnect-0d6efd?style=for-the-badge&logo=hospital&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.6-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **Major B.Tech CSE Capstone Project & Portfolio Engineering Showcase**  
> A production-style, role-based healthcare management platform connecting **Patients**, **Doctors**, and **Administrators** with real-time appointment scheduling, encrypted medical records, asynchronous background notifications, and responsible AI-powered consultation preparation.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features by Role](#key-features-by-role)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Database Architecture & Schema](#database-architecture--schema)
6. [REST API Documentation](#rest-api-documentation)
7. [Responsible AI Health Guardrails](#responsible-ai-health-guardrails)
8. [Installation & Local Setup](#installation--local-setup)
9. [Turnkey Demo Seed Data](#turnkey-demo-seed-data)
10. [Environment Variables](#environment-variables)
11. [Docker & Containerized Deployment](#docker--containerized-deployment)
12. [Asynchronous Background Tasks with Celery](#asynchronous-background-tasks-with-celery)
13. [Running Automated Tests](#running-automated-tests)
14. [Security & Compliance Highlights](#security--compliance-highlights)
15. [Git & GitHub Submission Commands](#git--github-submission-commands)
16. [Future Roadmap](#future-roadmap)
17. [License & Acknowledgments](#license--acknowledgments)

---

## Project Overview

In traditional healthcare clinics, patients experience fragmented communication, unpredictable waiting times, and difficulty organizing diagnostic test records. Doctors suffer from scheduling double-bookings, manual charting delays, and lack of verified patient background context.

**MediConnect** solves these problems by providing a unified, secure, enterprise-grade web application built on Django and PostgreSQL.

### Core Goals
- **Role-Based Access Control (RBAC):** Strict separation of concerns between Patients, Doctors, and System Administrators.
- **Race-Condition-Proof Scheduling:** Concurrency-safe appointment slot generation with database locks (`select_for_update`) and unique active-slot constraints.
- **Confidential Health Document Vault:** File-level access controls ensuring medical reports are strictly accessible only by the owning patient, attending doctors with confirmed appointments, and authorized clinic administrators.
- **Responsible Generative AI Integration:** Clinical preparation assistant powered by Google Gemini, equipped with strict biomedical safety guardrails (non-diagnostic, non-prescriptive, educational).
- **Asynchronous Task Architecture:** Distributed background job queue powered by Celery & Redis for scheduled appointment reminders and alert notifications.

---

## Key Features by Role

### 1. Patient Portal
- **Secure Registration & Authentication:** Custom credentials with phone validation, blood group, emergency contact details, and dual-identifier login (Username or Email).
- **Doctor Discovery:** Filter certified medical specialists by department, qualifications, experience, and consultation fees.
- **Dynamic Slot Booking:** Real-time availability calculation based on individual doctor schedules; dynamic AJAX slot loading.
- **Appointment Management:** Dedicated dashboard tracking Upcoming vs. Historic visits, with status badges (*Pending*, *Confirmed*, *Completed*, *Cancelled*).
- **Encrypted Medical Document Storage:** Upload lab test reports, imaging scans, and prescriptions with extension and file-size validation.
- **Consultation Notes Access:** Review post-visit doctor observations and follow-up guidance.
- **Notification Center:** Real-time in-app alerts and navbar counter badge for appointment status changes.
- **AI Health Assistant:**
  - *Symptom Organizer:* Structures reported symptoms, timeline, and triggers into an organized brief.
  - *Doctor Questions Generator:* Formulates targeted clinical questions for the upcoming visit.
  - *Document Summarizer:* Explains complex medical report terminology in plain English.

### 2. Doctor Portal
- **Clinical Profile & Licensing:** Medical council registration number verification, specialization, qualifications, and biography.
- **Weekly Schedule & Availability Engine:** Configure working days, shift hours, and consultation slot durations (10 to 120 minutes).
- **Consultation Requests Queue:** Review appointment requests with complete patient background and visit reasons.
- **Consultation Lifecycle Management:** Accept & confirm bookings, record clinical observations, write follow-up care instructions, and mark consultations completed.
- **Legitimate Patient Document Access:** Inspect diagnostic reports uploaded exclusively by patients who have active clinical visits.

### 3. Administrator Console
- **Executive Analytics Dashboard:** Chart.js visual trends showing monthly consultation volumes, active user metrics, and pending requests.
- **Doctor Credential Verification:** Review submitted medical licenses and approve or suspend doctor profiles with automated notifications.
- **User Directory Administration:** Search, inspect, and toggle active/inactive statuses for all registered patients.
- **Global Consultations Oversight:** Filter and monitor platform appointments across all hospital departments.
- **Operational Reports:** Interactive doughnut charts illustrating consultation outcome distributions and specialty demand breakdown.

---

## System Architecture

MediConnect follows the **Model-Template-View (MTV)** architecture layered with a decoupled **REST API (DRF)** and an asynchronous **Celery Task Worker Pipeline**:

```
                                  [ Browser / Client ]
                                            │
                             ┌──────────────┴──────────────┐
                             ▼                             ▼
                    [ Web HTML Views ]            [ REST API (DRF) ]
                    (Bootstrap 5 + JS)             (/api/auth/, /api/...)
                             │                             │
                             └──────────────┬──────────────┘
                                            ▼
                               [ Role-Based Access (RBAC) ]
                                (Decorators & Permissions)
                                            │
                                            ▼
                              [ Application Business Logic ]
                         (accounts, doctors, appointments, ...)
                                            │
                     ┌──────────────────────┼──────────────────────┐
                     ▼                      ▼                      ▼
            [ PostgreSQL / SQLite ]   [ Redis Broker ]    [ Google Gemini AI ]
               (Relational Data)      (Task Messaging)    (Clinical Structuring)
                                            │
                                            ▼
                                     [ Celery Workers ]
                                   (Scheduled Reminders)
```

### Modular Application Structure
```
mediconnect/
├── accounts/          # Custom User model, registration, dual-identifier login, RBAC decorators
├── patients/          # Patient demographic profiles, emergency contacts, blood group metadata
├── doctors/           # Doctor credentials, medical licensing, weekly availability scheduling engine
├── appointments/      # Booking engine, slot conflict resolution, concurrency locks, lifecycle
├── medical_records/   # Secure document storage, authorization checks, doctor consultation notes
├── notifications/     # In-app notification engine, Celery task workers, periodic scheduler
├── ai_assistant/      # Responsible Generative AI integration, symptom organizer, document summarizer
├── dashboard/         # Role-specific workspaces (Patient, Doctor, Admin) and Chart.js analytics
├── templates/         # Clean, responsive Bootstrap 5 HTML layouts with medical disclaimers
├── static/            # Custom CSS stylesheets, main.js notification badge poller, assets
├── config/            # Django project settings, master URL routing, Celery configuration
├── Dockerfile         # Production container definition
├── docker-compose.yml # Multi-container orchestration (web, db, redis, worker, beat)
└── manage.py          # Django administrative controller
```

---

## Technology Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| **Backend Framework** | Python / Django | 3.14 / 6.1 | Web application framework and ORM |
| **REST API Layer** | Django REST Framework | 3.18 | Token/Session-based API endpoints |
| **Database** | PostgreSQL / SQLite | 16 / 3.x | Primary relational store (dual DB fallback) |
| **Task Queue** | Celery & Celery Beat | 5.6 | Asynchronous background workers & periodic tasks |
| **Message Broker** | Redis | 7.0 | In-memory message broker & result backend |
| **AI Integration** | Google Gemini REST API | 1.5 Flash | Responsible pre-consultation information organizer |
| **Frontend UI** | HTML5, CSS3, Bootstrap | 5.3.3 | Responsive healthcare UI with custom design system |
| **Data Visualization** | Chart.js | 4.4 | Executive administrative analytics charts |
| **Containerization** | Docker & Docker Compose | Latest | Reproducible containerized deployment |

---

## Database Architecture & Schema

### Entity-Relationship Overview

```
 [ accounts.User ] ── (1:1) ── [ patients.PatientProfile ]
         │
         ├── (1:1) ── [ doctors.DoctorProfile ] ── (1:N) ── [ doctors.DoctorAvailability ]
         │                     │
         │ (1:N)               │ (1:N)
         ▼                     ▼
 [ appointments.Appointment ] ── (1:1) ── [ medical_records.ConsultationNote ]
         │
         ├── (1:N) ── [ medical_records.MedicalDocument ]
         │
         └── (1:N) ── [ notifications.Notification ]
```

### Models & Constraints
- **`User` (Custom `AbstractUser`):** Extends Django's user model with `role` (`PATIENT`, `DOCTOR`, `ADMIN`), `phone_number`, and helper properties (`is_patient`, `is_doctor`, `is_administrator`).
- **`DoctorProfile`:** Enforces `unique=True` on `license_number` to prevent duplicate medical council claims. Has an `is_approved` boolean regulated by administrators.
- **`DoctorAvailability`:** Maps doctor working hours with a `unique_together = ('doctor', 'day_of_week')` constraint.
- **`Appointment`:** Contains a database-level `UniqueConstraint` on `('doctor', 'appointment_date', 'start_time')` filtered by `status__in=['PENDING', 'CONFIRMED']` to guarantee zero overlapping double bookings.
- **`MedicalDocument`:** Strict validation on file extensions (`pdf`, `jpg`, `png`, `doc`, `docx`, `txt`) and maximum file size (10 MB).
- **`ConsultationNote`:** One-to-one clinical observation record attached to a completed appointment.
- **`Notification`:** Tracks recipient, notification type, message, read status, and reference appointment ID.

---

## REST API Documentation

All endpoints return and accept JSON. Authenticated requests use session or token authentication.

### Authentication Endpoints
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Public | Register new patient account |
| `POST` | `/api/auth/register-doctor/` | Public | Register doctor account (pending verification) |
| `POST` | `/api/auth/login/` | Public | Authenticate via username or email |
| `POST` | `/api/auth/logout/` | Authenticated | Terminate session |
| `GET` | `/api/auth/user/` | Authenticated | Retrieve current user profile and role |

### Doctor & Availability Endpoints
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/doctors/` | Public | List approved doctors (supports `?specialization=`) |
| `GET` | `/api/doctors/<id>/` | Public | Retrieve doctor profile and weekly schedule |
| `GET/POST`| `/api/doctors/<id>/availability/` | Doctor Only | Retrieve or update doctor's working days |
| `GET` | `/api/doctors/<id>/slots/?date=YYYY-MM-DD` | Public | Generate calculated available time slots |

### Appointments Endpoints
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/appointments/` | Authenticated | List appointments for requesting user |
| `POST` | `/api/appointments/` | Patient Only | Book a new consultation slot |
| `GET` | `/api/appointments/<id>/` | Authenticated | Retrieve appointment details |
| `POST` | `/api/appointments/<id>/cancel/` | Owner / Admin | Cancel appointment |

### Medical Records Endpoints
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/medical-records/` | Authenticated | List medical documents |
| `POST` | `/api/medical-records/` | Patient Only | Upload health report or scan |
| `GET` | `/api/medical-records/<id>/` | Authorized | Retrieve document metadata |
| `DELETE`| `/api/medical-records/<id>/` | Owner Only | Delete document |
| `GET/POST`| `/api/notes/?appointment_id=<id>`| Doctor / Patient| Consultation note details |

### In-App Notifications
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/notifications/` | Authenticated | List user notifications |
| `POST` | `/api/notifications/` | Authenticated | Mark all notifications as read |
| `GET` | `/api/notifications/unread-count/` | Authenticated | Live badge counter value |

### Responsible AI Assistant Endpoints
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/ai/symptom-summary/` | Patient Only | Format symptoms into clinical briefing |
| `POST` | `/api/ai/questions/` | Patient Only | Generate doctor consultation questions |
| `POST` | `/api/ai/summarize-document/`| Patient Only | Summarize report text in plain language |

### Administrative Analytics Endpoints
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/admin/dashboard/` | Admin Only | KPI statistics (counts of users, visits) |
| `GET` | `/api/admin/reports/` | Admin Only | Monthly trends & distribution figures |

---

## Responsible AI Health Guardrails

MediConnect adheres strictly to ethical AI engineering standards:
1. **Never Diagnoses:** The AI system will never output a medical diagnosis or claim certainty regarding any illness.
2. **Never Prescribes:** The AI will never recommend pharmaceutical drug brand names, dosages, or self-medication regimens.
3. **Mandatory Disclaimer:** Every AI response automatically appends an explicit medical disclaimer reminding users that AI output is for educational preparation only.
4. **Safety Filter Thresholds:** Google Gemini API calls enforce `BLOCK_MEDIUM_AND_ABOVE` on dangerous content and medical harm categories.
5. **Zero-Key Fallback:** If `GEMINI_API_KEY` is not provided, the system gracefully falls back to structured local clinical templates rather than crashing.

---

## Installation & Local Setup

### Prerequisites
- Python 3.10+ (Tested up to Python 3.14)
- Git 2.x+
- PowerShell (Windows) or Bash (macOS/Linux)

### Step 1: Clone the Repository
```powershell
git clone https://github.com/yourusername/mediconnect.git
cd mediconnect
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```powershell
copy .env.example .env
```
*Note: For instant zero-config local development, `.env` is configured with `USE_SQLITE=True`.*

### Step 5: Run Database Migrations
```powershell
python manage.py migrate
```

### Step 6: Load Turnkey Demo Seed Data
```powershell
python manage.py seed_data
```

### Step 7: Launch the Development Server
```powershell
python manage.py runserver
```
Visit **`http://127.0.0.1:8000`** in your browser!

---

## Turnkey Demo Seed Data

Running `python manage.py seed_data` populates the database with realistic demonstration accounts:

| Role | Username | Password | Notes |
|---|---|---|---|
| **Administrator** | `admin` | `AdminPassword123!` | Full control panel access |
| **Doctor** | `dr_smith` | `DoctorPassword123!` | Cardiology specialist, Approved, Mon-Fri slots |
| **Doctor** | `dr_jones` | `DoctorPassword123!` | Neurology specialist, Approved, Mon/Wed/Fri slots |
| **Doctor** | `dr_williams` | `DoctorPassword123!` | Dermatology specialist, **Pending Review** |
| **Doctor** | `dr_debabrata_das_mohapatra` | `DoctorPassword123!` | General Medicine, **Pending credential verification** |
| **Doctor** | `dr_matrujyoti_nath` | `DoctorPassword123!` | Pediatrics, **Pending credential verification** |
| **Doctor** | `dr_rabindra_dalai` | `DoctorPassword123!` | Orthopedics, **Pending credential verification** |
| **Doctor** | `dr_bhakti_ranjan_das` | `DoctorPassword123!` | Obstetrics & Gynecology, **Pending credential verification** |
| **Doctor** | `dr_bibhudatta_mallick` | `DoctorPassword123!` | Dermatology, **Pending credential verification** |
| **Doctor** | `dr_debasish_mallick` | `DoctorPassword123!` | Cardiology, **Pending credential verification** |
| **Patient** | `patient_alice` | `PatientPassword123!` | Has active & completed consultations |
| **Patient** | `patient_bob` | `PatientPassword123!` | New patient account |

---

## Environment Variables

| Variable | Description | Default | Required in Production |
|---|---|---|---|
| `SECRET_KEY` | Django cryptographic secret key | Insecure dev key | **Yes** |
| `DEBUG` | Enable debug mode | `True` | **No** (Must be `False`) |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames | `127.0.0.1,localhost` | **Yes** |
| `USE_SQLITE` | Fallback to SQLite (zero-config) | `True` | No |
| `DB_NAME` | PostgreSQL database name | `mediconnect_db` | Yes (if PostgreSQL) |
| `DB_USER` | PostgreSQL user | `postgres` | Yes (if PostgreSQL) |
| `DB_PASSWORD` | PostgreSQL password | `postgres` | Yes (if PostgreSQL) |
| `DB_HOST` | Database host | `localhost` | Yes (if PostgreSQL) |
| `DB_PORT` | Database port | `5432` | Yes (if PostgreSQL) |
| `CELERY_BROKER_URL` | Redis connection URI | `redis://localhost:6379/0` | Yes |
| `GEMINI_API_KEY` | Google Gemini API Key | None | Optional (for live AI) |

---

## Docker & Containerized Deployment

MediConnect includes a complete multi-container Docker Compose configuration:

```powershell
# 1. Edit .env to set USE_SQLITE=False and specify DB passwords
# 2. Build and launch all 5 containers
docker compose up --build
```

### Containers Orchestrated:
1. **`web`**: Django Gunicorn / WSGI web application server on port `8000`.
2. **`db`**: PostgreSQL 16 relational database with persistent named volumes.
3. **`redis`**: Redis 7 in-memory cache and task queue broker on port `6379`.
4. **`celery_worker`**: Asynchronous worker processing background notification jobs.
5. **`celery_beat`**: Distributed cron scheduler dispatching daily appointment reminders.

---

## Asynchronous Background Tasks with Celery

To run Celery locally without Docker:

```powershell
# Terminal 1: Run Redis (e.g., via Docker)
docker run -p 6379:6379 redis:7-alpine

# Terminal 2: Run Celery Worker
.\venv\Scripts\Activate.ps1
celery -A config worker --loglevel=info --pool=solo

# Terminal 3: Run Celery Beat Scheduler
.\venv\Scripts\Activate.ps1
celery -A config beat --loglevel=info

# Terminal 4: Run Django Development Server
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

---

## Running Automated Tests

MediConnect includes an automated unit and integration test suite covering authentication, permissions, booking conflicts, document access, and AI safety guardrails.

```powershell
# Run the complete test suite
python manage.py test

# Run tests for a specific module
python manage.py test accounts
python manage.py test doctors
python manage.py test appointments
python manage.py test medical_records
python manage.py test notifications
python manage.py test ai_assistant
python manage.py test dashboard

# Run with detailed verbosity
python manage.py test --verbosity=2
```

**Test Verification Summary:**
```
Ran 35 tests in ~240s
OK (All 35 tests passing with 0 errors)
```

---

## Security & Compliance Highlights

- **Row-Level Authorization:** Custom object access checks prevent horizontal privilege escalation (e.g., Patient A cannot view Patient B's documents).
- **Directory Traversal Defense:** Uploaded medical files are sanitized with `os.path.basename` and partitioned into isolated user directories.
- **Race Condition Prevention:** Appointment bookings execute within an atomic transaction with `select_for_update()` database row locking.
- **Cryptographic Password Hashing:** Standardized on Django's PBKDF2 algorithm with SHA-256 hash.
- **CSRF & XSS Protection:** CSRF tokens required on all state-changing POST requests; Django auto-escaping active in templates.
- **Protected File Downloads:** Document files are served through `SecureDocumentDownloadView` with clinical relationship verification rather than exposed via public web server URLs.

---

## Git & GitHub Submission Commands

Follow these exact commands to push the project to your GitHub repository:

```bash
# 1. Initialize Git repository (if not already initialized)
git init

# 2. Stage all verified files
git add .

# 3. Commit the project
git commit -m "feat: complete MediConnect healthcare platform with all 9 phases"

# 4. Set default branch to main
git branch -M main

# 5. Connect to your GitHub repository
git remote add origin https://github.com/yourusername/mediconnect.git

# 6. Push to GitHub
git push -u origin main
```

---

## Future Roadmap

- [ ] WebRTC Telemedicine video consultation integration.
- [ ] Real-time WebSocket notifications via Django Channels.
- [ ] Two-Factor Authentication (2FA) via TOTP / SMS.
- [ ] Digital e-signatures for official doctor prescription PDFs.
- [ ] Integration with wearable health device APIs (Apple HealthKit / Google Health Connect).

---

## License & Acknowledgments

This project is licensed under the **MIT License** — free for academic, portfolio, and educational use.

Developed with ❤️ as a **B.Tech Computer Science & Engineering Major Capstone Project**.
