# MedCall — System Design Document

**Project:** MedCall v2 — AI-Powered Telehealth Platform
**Version:** 2.0
**Date:** April 2026
**Live Prototype:** https://medcall-hazel.vercel.app/

---

## Table of Contents

1. System Overview
2. Architecture Diagram
3. Tech Stack
4. Database Design
5. Backend Architecture
6. AI Agent Architecture
7. Frontend Architecture
8. Authentication Flow
9. USSD Flow
10. SMS Flow
11. External Integrations
12. Deployment & Infrastructure
13. Environment Configuration
14. Security Considerations

---

## 1. System Overview

MedCall is an AI-powered telehealth platform designed for patients in rural East Africa and refugee camps. It enables patients to receive medical consultations and triage guidance using any basic mobile phone — no internet or smartphone required — through USSD and SMS. A web-based chat interface is also available for users with internet access.

**Core Value Proposition:**

- Patients in low-connectivity environments dial a USSD shortcode to register and access their health history.
- A web chat interface connects patients to Doctor Mshauri, an AI consultation agent, which gathers symptoms through a structured conversation.
- On completion, two further AI agents run automatically in the background: one analyzes the symptoms and identifies possible conditions, and a second delivers a final triage recommendation (self-care, clinic visit, or emergency).
- Results are sent back to the patient by SMS.

**Key Actors:**

| Actor | Interaction |
|---|---|
| Patient (feature phone) | USSD registration, USSD consultation history lookup |
| Patient (smartphone/web) | Web chat consultation, history review, notifications |
| Doctor Mshauri (AI) | Conversational symptom collection agent |
| Doctor Mjali (AI) | Symptom analysis and differential diagnosis agent |
| Dr. Mshuli (AI) | Final triage decision and referral agent |

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│                                                                     │
│  ┌──────────────────┐          ┌──────────────────────────────┐    │
│  │  Feature Phone   │          │   Web Browser (React SPA)    │    │
│  │  (USSD / SMS)    │          │   medcall-hazel.vercel.app   │    │
│  └────────┬─────────┘          └──────────────┬───────────────┘    │
└───────────┼────────────────────────────────────┼────────────────────┘
            │ USSD/SMS                            │ HTTPS REST
            ▼                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY / BACKEND (FastAPI)                  │
│                        Render — Python 3.x                          │
│                                                                     │
│  /auth     /consultation     /history     /ussd    /sms             │
│  /notifications                                                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   AI AGENT LAYER (LangGraph)                  │  │
│  │                                                               │  │
│  │  [Doctor Mshauri]  →  [Doctor Mjali]  →  [Dr. Mshuli]        │  │
│  │  Consultation          Analysis           Decision            │  │
│  └───────────────────────────┬──────────────────────────────────┘  │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
   ┌─────────────────┐ ┌──────────────────┐ ┌──────────────────┐
   │   PostgreSQL    │ │  Google Gemini   │ │  SMSGateway24Pro │
   │   (Render DB)   │ │  (AI / LLM)      │ │  (SMS / USSD)    │
   └─────────────────┘ └──────────────────┘ └──────────────────┘
                                │
                       ┌────────┴──────────┐
                       │  Tavily Web Search│
                       └───────────────────┘
```

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, React Router v6 |
| Backend | FastAPI, Uvicorn, Python 3.x |
| ORM & Migrations | SQLAlchemy, Alembic |
| Database | PostgreSQL (production), SQLite (local dev) |
| AI / LLM | Google Gemini 2.5-Flash via LangChain |
| Agent Orchestration | LangGraph (stateful multi-agent graph) |
| Web Search | Tavily API |
| SMS / USSD Gateway | SMSGateway24Pro |
| Authentication | JWT (HS256), bcrypt |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |

---

## 4. Database Design

### Entity Relationship Overview

The database is PostgreSQL. All tables use SQLAlchemy ORM with Alembic managing schema migrations.

### 4.1 `patients`

Stores core patient credentials and identity.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| patient_id | String | Unique identifier (e.g. Patient-abc123) |
| first_name | String | — |
| last_name | String | — |
| phone_number | String | Unique; used as login identifier |
| email | String | Optional |
| pin | String | bcrypt-hashed PIN |
| updated_at | DateTime | Auto-updated |

### 4.2 `patient_personal_info`

Extended demographic information collected after registration.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| patient_id | String | FK → patients.patient_id |
| age | String | — |
| gender | String | — |
| nationality | String | — |
| country_of_residence | String | — |
| city_of_residence | String | — |
| address | String | — |
| next_of_kin | String | — |
| next_of_kin_phone | String | — |
| preferred_language | String | — |

### 4.3 `patient_medical_info`

Medical background used to inform AI agent analysis.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| patient_id | String | FK → patients.patient_id |
| blood_type | String | — |
| allergies | String | Comma-separated or freetext |
| chronic_illness | String | — |
| recent_vaccination | String | — |

### 4.4 `consultations`

One record per consultation session.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| patient_id | String | FK → patients.patient_id |
| consultation_id | String | Unique UUID |
| start_time | DateTime | — |
| risk_level | JSON | Set by analysis agent |
| last_updated | DateTime | — |
| consultation_summary | Text | Summary from consultation agent |
| consultation_status | Boolean | True = active session |
| thread_id | String | LangGraph thread isolation ID |

### 4.5 `consultation_sms`

Message log for every SMS exchanged in a consultation.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| consultation_id | String | FK → consultations.consultation_id |
| sms_id | String | External SMS gateway message ID |
| message_type | String | "inbound" or "outbound" |
| content | Text | Message body |
| sms_metadata | JSON | Provider metadata |
| timestamp | DateTime | — |

### 4.6 `consultation_analysis`

Results from Doctor Mjali after symptom analysis.

| Column | Type | Notes |
|---|---|---|
| id | String | Primary key |
| consultation_id | String | FK → consultations.consultation_id (CASCADE) |
| detected_symptoms | Text/JSON | List of identified symptoms |
| possible_conditions | JSON | Array of {name, confidence} objects |
| exams | JSON | Recommended examinations |
| risk_level | String | "low" or "high" |
| mark_emergency | Boolean | True if emergency detected |
| reasoning | Text | AI reasoning explanation |
| created_at / updated_at | DateTime | — |

### 4.7 `consultation_decisions`

Final recommendation from Dr. Mshuli.

| Column | Type | Notes |
|---|---|---|
| id | String | Primary key |
| consultation_id | String | FK → consultations.consultation_id (unique, CASCADE) |
| message | Text | Human-readable recommendation |
| urgency | String | "low", "medium", or "high" |
| action | String | "self_care", "visit_clinic", or "emergency" |
| referral_type | String | Facility type if referral issued |
| created_at | DateTime | — |

### 4.8 `referrals` and `clinic_facilities`

Stores referral records and matched clinic/hospital information.

### 4.9 `system_logs`

Audit trail of system-level actions.

---

## 5. Backend Architecture

### 5.1 Entry Point

`api/main.py` initialises the FastAPI application, applies CORS middleware (allowing all origins for development), and registers six routers.

### 5.2 Route Map

| Router | Prefix | Key Endpoints |
|---|---|---|
| auth | /auth | POST /login, /register, /register/personal, /register/medical, /change-password, GET /me |
| consultation | /consultation | POST /consultation |
| history | /history | GET /history |
| notifications | /notifications | GET /notifications |
| ussd | /ussd | POST /ussd |
| sms | /sms | POST /sms/inbound, POST /sms/delivery_status |

### 5.3 Request Lifecycle

```
HTTP Request
    │
    ▼
FastAPI Router → Route Handler
    │
    ▼
Controller (validates, extracts JWT patient)
    │
    ▼
Service Layer (business logic, DB calls)
    │
    ▼
SQLAlchemy ORM → PostgreSQL
    │
    ▼
(If consultation) → Background Thread → AI Agents
    │
    ▼
HTTP Response (JSON)
```

### 5.4 Consultation Invocation Flow

1. Patient sends message via web chat → `POST /consultation`
2. Consultation controller invokes **Doctor Mshauri** (synchronous, returns AI response)
3. When consultation is marked `complete`, a background thread launches:
   - **Doctor Mjali** runs analysis → saves `ConsultationAnalysis`
   - **Dr. Mshuli** runs decision → saves `ConsultationDecision`
4. Patient polls `GET /notifications` or receives an SMS

---

## 6. AI Agent Architecture

All three agents use **Google Gemini 2.5-Flash** via LangChain, orchestrated by **LangGraph** with an `InMemorySaver` checkpointer. Each consultation gets an isolated `thread_id` so conversation state does not bleed between sessions.

A `ModelFallbackMiddleware` cycles through up to 10 Gemini API keys automatically on rate-limit errors.

### 6.1 Doctor Mshauri — Consultation Agent

**Role:** Friendly AI doctor that conducts a structured symptom intake conversation.

**Tools:** `verify_registration`, `collect_user_personal_info`, `collect_medical_information`

**Behavior:**
- Greets the patient and asks for their main health concern
- Asks one follow-up question at a time (duration, severity, associated symptoms, context)
- Draws on stored personal and medical info to personalize questions
- Closes the session with reassurance once sufficient data is gathered

**Output Schema:**
```json
{
  "status": "in_progress | complete",
  "doctor_questions": ["..."],
  "patient_responses": ["..."],
  "collected_data": {...},
  "summary": "..."
}
```

### 6.2 Doctor Mjali — Analysis Agent

**Role:** Differential diagnosis engine that maps symptoms to probable medical conditions.

**Tools:** `get_latest_consultation`, `web_search`, `load_east_africa_diseases_sample`, `load_health_dataset`, `load_healthcare_diseases`

**Behavior:**
- Retrieves completed consultation data
- Cross-references symptoms against local East African disease datasets and CSV-based health datasets
- Uses Tavily web search for supplementary verification
- Assigns a confidence score (0–1) to each possible condition
- Sets `mark_emergency = true` if any red-flag symptoms are detected

**Output Schema:**
```json
{
  "detected_symptoms": ["..."],
  "possible_conditions": [{"name": "...", "confidence": 0.87}],
  "exams": {"recommended": ["..."]},
  "risk_level": "low | high",
  "mark_emergency": false,
  "reasoning": "..."
}
```

### 6.3 Dr. Mshuli — Decision Agent

**Role:** Triage decision-maker that converts analysis into an actionable recommendation.

**Tools:** `web_search`, `load_clinics_by_country`, `load_all_clinics`, `collect_user_personal_info`

**Decision Logic:**

| Condition | Action | Urgency |
|---|---|---|
| mark_emergency = true | emergency | high |
| risk_level = high | visit_clinic | medium |
| risk_level = low | self_care | low |

**Output Schema:**
```json
{
  "message": "Human-readable recommendation...",
  "urgency": "low | medium | high",
  "action": "self_care | visit_clinic | emergency",
  "referral_type": "clinic | hospital | emergency_room"
}
```

### 6.4 Agent Execution Pipeline

```
POST /consultation
        │
        ▼
[Doctor Mshauri]  ←→  Patient (iterative turns)
        │
  status = complete
        │
        ▼  (background thread)
[Doctor Mjali]
        │ saves ConsultationAnalysis
        ▼  (background thread)
[Dr. Mshuli]
        │ saves ConsultationDecision
        ▼
SMS sent to patient via SMSGateway24Pro
```

---

## 7. Frontend Architecture

### 7.1 Pages

| Page | Route | Access | Description |
|---|---|---|---|
| Home | /home | Protected | Welcome screen and navigation |
| Login | /login | Public | Phone number + PIN form |
| Register | /register | Public | 3-step: account → personal info → medical info |
| Chat | /chat | Protected | Live AI consultation interface |
| History | /history | Protected | Past consultations with expandable analysis and decisions |

### 7.2 API Client (`client.js`)

All requests are made through two wrapper functions:

- `apiPost(path, body)` — POST with Bearer token header
- `apiGet(path, params)` — GET with Bearer token header

Both functions read the JWT from `AuthContext` and automatically attach it to every request. Errors are parsed from `response.detail` or the HTTP status code.

### 7.3 State Management

**AuthContext (`AuthContext.jsx`):**

- Stores: `token` (JWT string), `user` object (`{ firstName, lastName, phoneNumber, patientId, hasPersonalInfo, hasMedicalInfo }`)
- Methods: `login(token, userData)`, `updateUser(patch)`, `logout()`
- Persisted to `localStorage` keys: `medcall_token`, `medcall_user`

**ToastContext:** Application-wide notification toasts.

### 7.4 Routing

React Router v6 with protected route wrappers. Unauthenticated users accessing protected routes are redirected to `/login`.

---

## 8. Authentication Flow

### 8.1 Registration

```
Client POST /auth/register  →  validate phone uniqueness
                            →  hash PIN with bcrypt
                            →  generate patient_id
                            →  create Patient record
                            →  issue JWT (7-day expiry)
                            →  return token + user info
```

### 8.2 Login

```
Client POST /auth/login  →  lookup patient by phone_number
                         →  bcrypt.checkpw(input_pin, stored_hash)
                         →  issue JWT (7-day expiry, HS256)
                         →  return token + user info
```

### 8.3 Request Authorization

Every protected route uses an `HTTPBearer` dependency:

```
Request with Authorization: Bearer <token>
    │
    ▼
Decode JWT using JWT_SECRET_KEY
    │
    ▼
Extract patient_id from subject claim
    │
    ▼
Lookup patient in DB → inject into route handler
```

---

## 9. USSD Flow

The USSD interface allows patients on feature phones to register and access their health data with no internet connection.

### 9.1 Entry Point

SMSGateway24Pro (or Africa's Talking in original config) sends a `POST /ussd` callback with:

```
sessionId, phoneNumber, text (accumulated user input), serviceCode
```

### 9.2 Session State Machine

USSD sessions are tracked in an in-memory dictionary keyed by `session_id`.

**Main Menu:**
```
CON Welcome to MedCall
1. Register new account
2. Complete personal info
3. Add medical info
4. View medical info
5. View personal info
6. View past consultations
7. Subscribe
8. Exit
```

**Registration Sub-flow:**
```
REGISTER_FIRST_NAME → REGISTER_LAST_NAME → REGISTER_EMAIL
    → REGISTER_PIN → REGISTER_CONFIRM_PIN → SAVE → END
```

**Personal Info Sub-flow:**
```
AGE → GENDER → NATIONALITY → COUNTRY → CITY → ADDRESS
    → NEXT_OF_KIN → NEXT_OF_KIN_PHONE → LANGUAGE → SAVE → END
```

**Medical Info Sub-flow:**
```
BLOOD_TYPE → ALLERGIES → CHRONIC_ILLNESS → VACCINATION → SAVE → END
```

### 9.3 Response Format

- `CON <text>` — Session continues; patient can respond
- `END <text>` — Session terminates

### 9.4 Phone Normalization

All phone numbers are normalized via `normalize_phone_number()` before storage (e.g., `0712345678` → `+254712345678`).

---

## 10. SMS Flow

### 10.1 Outbound SMS (Consultation Results)

When Dr. Mshuli completes a decision, an outbound SMS is sent to the patient summarizing:
- The top detected condition
- The urgency level
- The recommended action (self-care / visit clinic / emergency)
- A safety disclaimer

Delivery uses SMSGateway24Pro with `GATEWAY_TOKEN` and `DEVICE_ID` from environment config.

### 10.2 Inbound SMS (`POST /sms/inbound`)

Accepts form-encoded payloads from SMSGateway24Pro:

```
phone, message, timestamp, sms_id, ...
```

Validated against the `InboundSMS` schema and passed to the inbound SMS controller for processing.

### 10.3 Delivery Status Callback (`POST /sms/delivery_status`)

Receives delivery confirmation events from SMSGateway24Pro and logs the `sms_id`, `status_message`, and `timestamp` for audit purposes.

---

## 11. External Integrations

### 11.1 Google Gemini (via LangChain)

- **Model:** `gemini-2.5-flash`
- **Max tokens:** ~8,000 per request
- **Temperature:** 0.1 for consultation (conversational), 0.0 for analysis and decision (deterministic)
- **Fallback:** 10 API keys (GEMINI_API_KEY variants A through X) cycled automatically on rate limits via `ModelFallbackMiddleware`

### 11.2 Tavily Web Search

- Used by the analysis and decision agents to supplement local datasets
- Searches for condition details, drug interactions, and local clinic information
- API key: `TAVILY_API_KEY`

### 11.3 SMSGateway24Pro

- **USSD:** Callback to `POST /ussd` on each user input keystroke
- **Outbound SMS:** REST call to gateway API with `GATEWAY_TOKEN` + `DEVICE_ID`
- **Inbound SMS:** Webhook to `POST /sms/inbound`
- **Delivery Status:** Webhook to `POST /sms/delivery_status`

### 11.4 Local Health Datasets

The analysis agent loads static health reference data:

| Dataset | Format | Content |
|---|---|---|
| `east_africa_diseases_sample.json` | JSON | East African disease profiles and symptom patterns |
| `health_dataset.csv` | CSV | General disease-symptom mappings |
| `healthcare_diseases` | CSV | Extended disease classification data |

---

## 12. Deployment & Infrastructure

### 12.1 Backend — Render

- FastAPI application served by Uvicorn
- PostgreSQL managed database (Render Postgres or external)
- Alembic handles all schema migrations (`/alembic/versions/`)
- Automatic restarts on failure

### 12.2 Frontend — Vercel

- React + Vite production build (`npm run build` → `dist/`)
- `vercel.json` configures SPA routing: all paths rewrite to `/index.html`
- Environment variable: `VITE_API_URL` points to the Render backend

### 12.3 Local Development

- Backend: `uvicorn api.main:app --reload` on `http://localhost:8000`
- Frontend: `npm run dev` on `http://localhost:5173`
- Database: SQLite fallback (`sqlite:///medcall.db`) when `DATABASE_URL` is not set
- USSD testing: ngrok exposes localhost to HTTPS for gateway callbacks

---

## 13. Environment Configuration

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (falls back to SQLite) |
| `JWT_SECRET_KEY` | Secret used to sign and verify JWTs |
| `GEMINI_AI_MODEL` | Gemini model name (`gemini-2.5-flash`) |
| `GEMINI_API_KEY_G/A/B/D/E/F/H/V/X` | 10 Gemini API keys for rate-limit fallback |
| `TAVILY_API_KEY` | Tavily web search API key |
| `GATEWAY_TOKEN` | SMSGateway24Pro authentication token |
| `DEVICE_ID` | SMSGateway24Pro device identifier |
| `AFRICAUSERNAME` | Africa's Talking username (`sandbox` or production) |
| `AFRICAS_API_KEY` | Africa's Talking API key |
| `africastalking_channel` | USSD shortcode (e.g. `*384*41992#`) |
| `VITE_API_URL` | Frontend base URL for API calls |

---

## 14. Security Considerations

| Area | Measure |
|---|---|
| Password / PIN storage | bcrypt with per-user salt |
| API authentication | JWT HS256 with 7-day expiry; Bearer token on every protected route |
| Patient data isolation | All queries filter by authenticated `patient_id` from JWT |
| Data in transit | HTTPS enforced on Render and Vercel |
| Health data compliance | Kenya Data Protection Act and GDPR applicable; data encrypted at rest in Render PostgreSQL |
| AI safety | Hard-coded safety filters in decision agent; every response includes a medical disclaimer and emergency escalation prompt |
| API key management | All secrets stored as environment variables; no keys committed to source code |
| USSD session isolation | Each session tracked by unique `session_id` in memory; no cross-session data leakage |
