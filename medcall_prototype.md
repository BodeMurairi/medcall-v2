# MedCall — Innovate Wellness Challenge
## Design Thinking Submission

**Project Name:** Innovate Wellness Challenge
**Solution:** MedCall — AI-Powered Telehealth via USSD & SMS for East Africa
**Live Prototype:** https://medcall-hazel.vercel.app/

---

# Stage 1: Empathize

*Design Thinking is a human-centered approach to solving challenges. The Empathize stage is designed to fully understand the audience through data analysis, testimonials, and expert consultation.*

## Audience

1. **Primary End Users** — People living in rural areas and refugee camps across East Africa who lack consistent access to medical facilities or trained healthcare professionals.

2. **Delivery Partners** — Humanitarian organizations such as UNHCR and IOM International, and local health organizations such as WHO and community health worker (CHW) networks, who can facilitate trusted access to our solution in the field.

## Observation, Consultation & Feedback

3. **Barrier 1 — Shortage of Medical Facilities and Trained Doctors:**
Through our research, we found that patients in refugee camps and rural areas struggle to access medical care due to a critical lack of healthcare infrastructure. According to UNHCR, there is only 0.1–0.2 doctors per 1,000 patients in these regions. The distance to the nearest medical facility can span many kilometers, making timely care practically impossible for large segments of the population.

4. **Barrier 2 — Overcrowded Hospitals and Misdirected Care:**
With so few hospitals serving so many patients, existing facilities are overcrowded — largely with cases that could have been managed at home or redirected to a more appropriate clinic. Patients do not know which facilities to attend, which conditions are emergencies, or when self-care is appropriate. This mismatch leads to dangerous delays for critical cases and unnecessary strain on limited resources.

---

# Stage 2: Define

*During the Define Stage, insights from the Empathize stage are used to identify the core problem and construct an Actionable Problem Statement (APS).*

## Insights, Problem & Action Steps

1. **Insight:**
The core gap is not only physical access to hospitals — it is the absence of early medical guidance. People in rural areas and refugee camps struggle to decide *when* and *where* to seek care, often until their condition has significantly worsened.

2. **Problem:**
Patients delay treatment or choose the wrong level of care because they lack tools to understand their symptoms. Structural barriers — distance, cost, and low health literacy — compound the problem. Meanwhile, hospitals are overwhelmed with non-critical cases that could have been resolved with early, accurate guidance.

3. **Action Steps:**
Build a system that empowers people in rural areas and refugee camps to access AI-assisted medical guidance quickly, before conditions worsen. Partner with community health workers to drive trust and adoption. Pilot with organizations like UNHCR to validate real-world impact and iterate based on feedback.

## Actionable Problem Statement

4. Refugees and people in rural communities lack timely and reliable guidance to assess their symptoms and decide when and where to seek care, leading to delayed treatment, reliance on informal or inappropriate care, and overcrowding of health facilities with non-critical cases. Existing healthcare systems do not provide accessible, real-time triage support that works in low-connectivity environments, on basic mobile phones, and in local languages — leaving the most vulnerable populations without a first line of medical assistance.

---

# Stage 3: Ideate

*In the Ideate Stage, ideas are generated freely and broadly, then prioritized down to the strongest candidates.*

## Idea Generation

1. Application to book consultation appointments / Symptom checker chatbot / Remote doctor consultation platform / Health education via SMS

2. Pharmacy recommendation system / Digital patient records (light version) / A low-cost community tablet device preloaded with health tools

## Top Three Ideas

3. **Top Ideas (Ranked):**

   a. **Symptom Checker Chatbot** *(Selected — Top Idea)*
   An AI-powered chatbot accessible via USSD on any basic mobile phone. Patients describe symptoms; the system analyzes them and recommends self-care, a clinic visit, or emergency action — no internet or smartphone required.

   b. **Remote Consultation Platform**
   A web-based platform connecting patients to remote doctors for live consultations, targeting areas with at least basic smartphone or kiosk access.

   c. **Smart Patient-to-Hospital Routing**
   A system that analyzes a patient's condition and nearest available facility, then sends them an SMS directing them to the most appropriate care point to reduce misdirected visits and overcrowding.

---

# Stage 4: Prototype

*In the Prototype Stage, the top idea is made tangible. MedCall is a working digital prototype — a symptom checker and AI consultation system delivered via USSD and SMS.*

**Live Prototype:** https://medcall-hazel.vercel.app/

## Prototype Preparation

### 1. Feasibility Assessment & Potential Restrictions

**Overall Feasibility: HIGH** — The core tech stack (FastAPI, Google Gemini AI, SMSGateway24Pro, PostgreSQL) is fully built and deployed.

| Dimension | Assessment |
|---|---|
| Technical | USSD + SMS integration with SMSGateway24Pro is operational; three AI agents (consultation, analysis, decision) are built using LangGraph |
| AI Reliability | Google Gemini 2.5-flash powers the agents with multi-key fallback to handle rate limits |
| Offline Reach | USSD requires zero internet or smartphone — directly addresses rural and refugee camp access barriers |
| Latency | The three-agent AI chain may approach USSD session time limits; async delivery via SMS mitigates this |

**Restrictions to Address:**

- **Medical Liability** — All AI outputs must carry legal disclaimers clearly stating the system is not a substitute for a licensed doctor.
- **USSD Session Timeouts** — SMSGateway24Pro enforces strict session character and time limits; AI processing is offloaded asynchronously with results delivered by SMS.
- **Data Privacy** — Patient health data is subject to the Kenya Data Protection Act and GDPR where applicable; data is encrypted at rest and in transit.
- **Operator Agreements** — Live USSD shortcode activation requires telecom operator approval, which can take 2–4 weeks per country.
- **Sustainability** — Per-consultation AI API costs must be modelled to ensure long-term financial viability, especially for humanitarian deployment.

### 2. Resources & Materials Needed

**APIs & Services:**

- SMSGateway24Pro account with active USSD shortcode (per target country)
- Google Gemini API keys with production-level quota
- Tavily API key for real-time medical web search enrichment

**Infrastructure:**

- Render — backend hosting (FastAPI + PostgreSQL, already deployed)
- Vercel — frontend hosting (React web app, already deployed)
- PostgreSQL managed database for patient records and consultation history
- Domain name + SSL certificate for the production API endpoint

**Development & Testing Tools:**

- SMSGateway24Pro sandbox for USSD flow simulation
- Postman collection and automated scripts for AI agent load and latency testing
- Minimum 2 feature phones (different models) for physical device QA

**Human Resources:**

- Medical advisor to review AI-generated consultation outputs for clinical safety
- Legal advisor for health disclaimer language and regulatory compliance

### 3. Goals

| Goal | Target |
|---|---|
| End-to-end USSD Flow | Patient registers and receives a consultation result via SMS within 3 minutes of completing the USSD session |
| SMS Delivery Rate | ≥95% of outbound SMS messages successfully delivered via SMSGateway24Pro |
| AI Diagnostic Accuracy | Analysis agent returns a clinically plausible top condition with ≥70% confidence on test symptom sets |
| Session Compliance | All USSD menus operate within SMSGateway24Pro session character and time limits |
| Safety Baseline | Every AI response includes a medical disclaimer and an emergency escalation prompt |
| Pilot Scope | 50 successful consultations in Kenya before regional expansion |

---

# Stage 5: Test

*The Test Stage treats the prototype as a pilot program. Standards and measures are set, the prototype is tested against them, and it is iteratively refined until it meets all goals.*

## Resources & Evaluation Measures

### 1. Resources & Personnel

**Technical Resources:**

1. SMSGateway24Pro sandbox account with at least one active USSD shortcode for testing
2. Staging environment on Render (fully isolated from production) running FastAPI + PostgreSQL
3. Feature phones (minimum 2 models) for real-device end-to-end USSD testing
4. Postman collection and automated load scripts to benchmark AI agent chain response times
5. PostgreSQL test database pre-seeded with mock patient profiles and consultation histories

**Personnel:**

1. **Lead Developer** — deploys and maintains staging environment, instruments agent chain latency, resolves bugs
2. **QA Tester** — executes complete USSD flows on physical devices and systematically logs session outcomes and errors
3. **Medical Advisor** — reviews AI-generated consultation responses for clinical accuracy, safety, and appropriate escalation language
4. **Pilot Users (10–20)** — real participants in Kenya recruited through a local clinic or CHW network, using their own feature phones

### 2. Measures of Success

| # | Measure | Target |
|---|---|---|
| 1 | USSD Session Completion Rate | ≥85% of initiated sessions complete without timeout or system error |
| 2 | AI Response Latency | Full 3-agent consultation result delivered via SMS within 3 minutes of session end |
| 3 | SMS Delivery Rate | ≥95% of outbound SMS messages delivered via SMSGateway24Pro |
| 4 | AI Condition Accuracy | Medical advisor validates ≥70% of top suggested conditions as clinically plausible |
| 5 | User Satisfaction | ≥80% of pilot users rate the experience 4 out of 5 or higher in a follow-up SMS survey |
| 6 | Safety Compliance | Zero consultation results delivered without a disclaimer and emergency escalation prompt |
| 7 | Data Privacy | Zero patient records exposed outside the encrypted database during the entire pilot period |

### 3. Anticipated Barriers

1. **USSD Session Timeouts** — The three-agent AI pipeline may exceed the SMSGateway24Pro session window. *Mitigation:* Offload AI analysis to an asynchronous background job; deliver the result via SMS after the USSD session closes.

2. **Pilot Recruitment Challenges** — Reaching non-smartphone users in rural Kenya without existing networks can be slow. *Mitigation:* Partner with a local clinic or community health worker organization for participant referrals.

3. **AI Hallucination / Unsafe Output** — The AI model may occasionally generate medically inaccurate or harmful suggestions. *Mitigation:* Medical advisor reviews all pilot outputs; hard-coded safety filters are applied in the decision agent before any result is sent.

4. **Operator Approval Delays** — Live USSD shortcode activation requires telecom operator sign-off, which can take 2–4 weeks. *Mitigation:* Begin the application process in Week 1, running in parallel with continued development.

5. **Backend Connectivity Outages** — The Render-hosted backend requires stable internet; downtime breaks the SMS delivery callback. *Mitigation:* Configure automatic service restarts and real-time uptime monitoring alerts.

## Timeline

### 4. Test Timeline

| # | Milestone | Duration | Target Date |
|---|---|---|---|
| 1 | **Staging Setup** — deploy backend and database on Render staging, connect SMSGateway24Pro sandbox | Week 1 | 24 April 2026 |
| 2 | **Internal QA** — developer and QA tester run complete USSD flows on physical devices; log all errors and latency data | Week 2 | 1 May 2026 |
| 3 | **Medical Advisor Review** — submit 20 sample AI consultation outputs for clinical accuracy and safety review | Weeks 2–3 | 8 May 2026 |
| 4 | **Fix & Iterate** — resolve bugs, session timeout issues, and any safety flags raised in medical review | Weeks 3–4 | 15 May 2026 |
| 5 | **Pilot Launch** — onboard 10–20 real users in Kenya on the live SMSGateway24Pro shortcode | Week 5 | 22 May 2026 |
| 6 | **Pilot Data Collection** — monitor delivery rates and session completions; collect user satisfaction via follow-up SMS survey | Weeks 5–6 | 29 May 2026 |
| 7 | **Evaluate & Report** — measure all success metrics, document findings, and decide on next iteration or scale-up plan | Week 7 | 5 June 2026 |
