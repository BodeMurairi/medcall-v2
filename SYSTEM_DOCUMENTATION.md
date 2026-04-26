# MedCall — What It Is and What It Does

## What is MedCall?

MedCall is an AI-powered telehealth platform built for East Africa. It gives patients access to a medical consultation from any device — whether they own a smartphone or a basic feature phone.

The core idea is simple: a patient describes their symptoms, and MedCall's AI doctors ask follow-up questions, analyse what they've said, and give them a clear recommendation — whether that's home care, a clinic visit, or emergency attention.

MedCall works through two channels:

- **The web app** — a full chat interface accessible from any browser.
- **USSD** — dial `*384*41992#` from any phone, no internet or smartphone needed. The patient navigates a text menu and receives their results the same way.

Both channels connect to the same system and the same AI pipeline.

---

## Features

### Creating an Account

Before using MedCall, a patient registers an account. They provide their name, phone number, email, and a PIN they'll use to log in. Registration is split into three stages:

1. **Basic account** — name, phone number, email, and PIN.
2. **Personal information** — age, gender, nationality, country and city of residence, home address, and next-of-kin details.
3. **Medical background** — blood type, any known allergies, chronic illnesses, and recent vaccinations.

This profile is stored and used by the AI during consultations to give more relevant and personalised results. Registration is available both on the web app and through the USSD menu.

---

### Logging In

Patients log in with their phone number and PIN. Once logged in, they stay signed in across sessions until they choose to log out. On the web app, patients can also change their PIN at any time from the profile menu.

---

### AI Consultation (Chat)

The main feature of MedCall. The patient opens the chat screen and starts describing what they're feeling. They are talking to **Doctor Mshauri** — MedCall's consultation AI.

Doctor Mshauri asks one focused question at a time, gathering a clear picture of the patient's symptoms, how long they've been experiencing them, and anything else relevant. The conversation continues naturally until the doctor has enough information.

The conversation is saved, so if the patient closes the app and comes back, the consultation picks up where it left off.

Once Doctor Mshauri is satisfied, the consultation is marked complete. In the background, two more AI doctors immediately take over — the patient doesn't need to do anything.

---

### AI Analysis (Doctor Mjali)

After the consultation ends, **Doctor Mjali** analyses everything that was said. This doctor works in the background without any input needed from the patient.

Doctor Mjali compares the patient's symptoms against East African health datasets and, if needed, searches current medical sources on the internet. The analysis produces:

- The symptoms that were identified
- The conditions the patient may have
- Recommended medical examinations or tests
- An overall risk level
- A flag if the situation may be an emergency

---

### Clinical Decision (Dr. Mshuli)

After Doctor Mjali finishes, **Dr. Mshuli** takes the analysis and makes a practical decision. This is the final recommendation the patient receives.

Dr. Mshuli tells the patient one of three things:

- **Self-care** — the situation can be managed at home with guidance.
- **Visit a clinic** — the patient should see a doctor, with a recommendation of what type of facility to go to.
- **Emergency** — the patient needs urgent medical attention immediately.

Dr. Mshuli also considers the patient's location and can reference clinics and hospitals in their country to inform the referral.

---

### Consultation History

Every consultation a patient has ever had is saved and accessible from the History page. Each entry shows:

- The full conversation with Doctor Mshauri
- Doctor Mjali's analysis (symptoms, possible conditions, recommended tests, risk level)
- Dr. Mshuli's final recommendation (urgency, action, referral)

Patients can review any past consultation at any time.

---

### Notifications

Because the analysis and decision happen in the background after the chat ends, MedCall notifies the patient when results are ready. A notification bell in the navigation bar lights up and a message pops up telling the patient their results are available. They can then go to History to read them.

---

### USSD Access (Feature Phones)

Patients without smartphones or internet access can access MedCall by dialling `*384*41992#` from any mobile phone. The USSD menu gives them access to:

- Registering a new account
- Entering or updating their personal and medical information
- Viewing their personal and medical information
- Viewing a summary of their last consultations

This ensures that the platform is accessible to patients in areas with limited connectivity or who cannot afford smartphones — which is a core part of MedCall's mission for East Africa.

---

## The Three AI Doctors — A Summary

| Doctor | Role | When they work |
|---|---|---|
| Doctor Mshauri | Conducts the consultation — asks questions, listens, gathers information | During the chat, responding to the patient in real time |
| Doctor Mjali | Analyses the symptoms against medical data and research | Automatically, after the consultation ends |
| Dr. Mshuli | Makes the final clinical recommendation and referral | Automatically, after Doctor Mjali finishes |

The patient only directly interacts with Doctor Mshauri. The other two work silently and deliver their results to the patient's History and Notifications.
