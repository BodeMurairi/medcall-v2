# MedCall — AI-Powered Telehealth Platform

MedCall is an SMS/USSD and web-based telehealth platform built for East Africa. It allows patients to consult with an AI doctor via USSD on any mobile phone or through a web interface, receive a medical analysis, and get a personalised health recommendation — all without needing a smartphone or internet connection for the core USSD flow.

---

## Author

**Bode Murairi**
- GitHub: [@BodeMurairi2](https://github.com/BodeMurairi2)
- Email: b.murairi@alustudent.com | bodemurairi2@gmail.com
- Linkedin: [@BodeMurairi] (https://www.linkedin.com/in/bode-murairi-2490501aa/)
---

## What It Does

- **USSD Registration** — Patients dial `*384*41992#` on any phone to register their account, personal info, and medical history.
- **Web Consultation** — Registered patients log in to the web app and chat with **Doctor Mshauri**, an AI consultation agent powered by Google Gemini.
- **Medical Analysis** — After the consultation, **Doctor Mjali** (the analysis agent) automatically analyses the collected symptoms, suggests possible conditions with confidence scores, flags emergencies, and recommends medical exams.
- **Health Recommendation** — A decision agent produces a final recommendation: self-care, visit a clinic, or emergency.
- **Consultation History** — Patients can view all past consultations, analyses, and decisions from the History tab.
- **Instant notification** -- Patients receive instant notifications once results are out.
- **SMS Consultation** — Powered by Africa's Talking (Not implemented here).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| Database | PostgreSQL (SQLAlchemy ORM + Alembic) |
| Frontend | React 18 + Vite |
| AI Agents | Google Gemini via LangChain + LangGraph |
| SMS / USSD | Africa's Talking |
| Web Search | Tavily |
| Auth | JWT (HS256) + bcrypt |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |

---

## Project Structure

```
medcall/
├── api/                        # FastAPI backend
│   ├── alembic/                # Database migrations
│   ├── config/                 # Africa's Talking config
│   ├── controllers/            # Request handlers
│   ├── database/               # DB session and engine setup
│   ├── external_integration/
│   │   └── agents/
│   │       ├── agent/          # Consultation, analysis, decision agents
│   │       ├── tools/          # LangChain tools (datasets, web search)
│   │       └── utils/          # Prompts and helpers
│   ├── models/                 # SQLAlchemy models
│   ├── routes/                 # API route definitions
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   ├── utils/                  # JWT utilities
│   ├── main.py                 # App entry point
│   └── requirements.txt
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/                # API client
│   │   ├── components/         # Shared UI components
│   │   ├── context/            # Auth and Toast context
│   │   └── pages/              # Home, Login, Register, Chat, History
│   ├── .env.local              # Local env vars (not committed)
│   ├── .env.production         # Production env vars (not committed)
│   └── vite.config.js
└── README.md
```

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or use SQLite for quick local testing)
- A Google Gemini API key
- A Tavily API key
- An Africa's Talking account (for USSD/SMS)

---

### 1. Clone the repository

```bash
git clone https://github.com/BodeMurairi2/medcall.git
cd medcall
```

---

### 2. Backend Setup

#### 2a. Create and activate a virtual environment

```bash
cd api
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

#### 2b. Install dependencies

```bash
pip install -r requirements.txt
```

#### 2c. Create a `.env` file inside the `api/` folder

```bash
touch .env
```

Add the following to `api/.env`:

```env
# Database
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/medcall

# Authentication
JWT_SECRET_KEY=your-secret-key-change-this-in-production

# Gemini AI (primary + fallback keys for rate limit resilience)
GEMINI_AI_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_KEY_G=your_gemini_api_key
GEMINI_API_KEY_A=your_gemini_api_key
GEMINI_API_KEY_B=your_gemini_api_key
GEMINI_API_KEY_D=your_gemini_api_key
GEMINI_API_KEY_E=your_gemini_api_key
GEMINI_API_KEY_F=your_gemini_api_key
GEMINI_API_KEY_H=your_gemini_api_key
GEMINI_API_KEY_V=your_gemini_api_key
GEMINI_API_KEY_X=your_gemini_api_key

# Web search
TAVILY_API_KEY=your_tavily_api_key

# Africa's Talking (SMS / USSD)
AFRICAUSERNAME=sandbox
AFRICAS_API_KEY=your_africastalking_api_key     # create your afica's talking API key
africastalking_channel=*384*41992#        # replace with your own africa's talking sandbox shared code channel
DATABASE_URL=your-database-url
```

> **Note:** You can use the same Gemini API key for all `GEMINI_API_KEY_*` variables during development. Multiple keys are used in production to handle rate limits. However, it is recommanded to use different API keys to avoid rate limits. Gemini free version provides 20 requests per day.

> **SQLite alternative:** For quick local testing without PostgreSQL, set `DATABASE_URL=sqlite:///medcall.db` if not provided, it will default to medcall.db inside api/

inside api/, run python -m database.init_tables or python3 -m database.init_tables
#### 2d. Run the backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
or python3 -m main or python -m main
```

The API will be available at `http://localhost:8000`
To access MedCall swagger documentation: `http://localhost:8000/docs`

---

### 3. Frontend Setup

Open a new terminal from the project root:

```bash
cd frontend
check if node is installed
npm --version if installed,
run
npm install # this installs all required modules
```

#### 3a. Create a `.env.local` file inside `frontend/`

```bash
touch frontend/.env.local
incude VITE_API_URL=http://localhost:8000
```

Add:

```env
VITE_API_URL=http://localhost:8000
```

#### 3b. Run the frontend

```bash
npm run dev
```

The web app will be available at `http://localhost:3000`

---

## Access the application
Link to the application:
**https://medcall-hazel.vercel.app**


## USSD Flow

For this MVP, use africa's talking sandbox to interact with MedCall USSD Application

```
Replace *384-41992# with your short code
for local testing, Africa's talking needs to reach the local backend application. The localhost enables the application to run locally. Therefore, the localhost http needs to be forwarded to https to be accessible by africa's talking. Use ngrok to forward http to https.
```
### Steps to setup ngrok and forward http to https
```
Create your account at ngrok https://ngrok.com/
```
Download ngrok
```bash snap installation
sudo snap install ngrok
```
``` bash apt installation
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok
```
```visit official documentation inside your account setup & installation to find the manual installation step```
then
``` bash 
ngrok config add-authtoken your-tocken # you will find your login tocket inside ngrok plateform setup & installation page
open a new terminal,run
ngrok http $port # replace port with the port number your local app is running
in our case, $port = 8000
a link will be generated like:
https:/your-link.ngrok-free.dev -> http://localhost:8000
```
#### Update USSD callback link inside Africa's talking
```
Open your Africa's talking account. Inside dashboard, click on sandbox, find USSD the inside services codes, update callback url
https://your-link.ngrok-free.dev/ussd then save
Create channel and save inside api/.env africastalking_channel=*384*your-channel# # eg. *384*46256#
Update your Africa's talking api key inside this variable AFRICAS_API_KEY=your-api-key
Africa's talking username remains as AFRICAUSERNAME=sandbox # for sandbox user.
```
Navigate to the simulator # Launch simulator, enter any phone number then continue
Dial your short code to interact with the local application.

Follow the on-screen prompts to register as a patient, register personal and medical information. Once registered via USSD, you can log in to the web app using the same phone number and PIN.

#### Important notes: Registration can also be done using the web app as it is possible with the USSD. Using the web app is faster and simpler than USSD
---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string | # if not setup, app default to medcall.db sqlite database
| `JWT_SECRET_KEY` | Yes | Secret key for signing JWT tokens |
| `GEMINI_AI_MODEL` | Yes | Gemini model name (e.g. `gemini-2.5-flash`) |
| `GEMINI_API_KEY` | Yes | Primary Gemini API key |
| `GEMINI_API_KEY_G` to `GEMINI_API_KEY_X` | Yes | Fallback Gemini API keys (for rate limit resilience) |
| `TAVILY_API_KEY` | Yes | Tavily web search API key |
| `AFRICAUSERNAME` | Yes | Africa's Talking username (`sandbox` for testing) |
| `AFRICAS_API_KEY` | Yes | Africa's Talking API key |
| `africastalking_channel` | Yes | USSD channel code |
| `VITE_API_URL` | Yes (frontend) | Backend API base URL |
---

Register to different plateforms to have access to different keys
## Contact
Contact the author for any questions or concerns regarding the app or setup.
Enjoy!

## License
This project is MedCall V1
