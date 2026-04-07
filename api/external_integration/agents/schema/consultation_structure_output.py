#!/usr/bin/env python3

structured_output_consultation = {
  "status": "in_progress|complete",
  "current_message": "next question|Closing message to the user to end consultation",

  "consultation_sms": [
    {
      "doctor_question": "AI question",
      "patient_response": "Patient response here"
    },
    {
      "doctor_question": "AI question",
      "patient_response": "Patient response here"
    }
  ],

  "doctor_questions": [
    "Question 1",
    "Question 2",
    "Question 3"
  ],

  "patient_responses": [
    "Response 1",
    "Response 2",
    "Response 3"
  ],

  "collected_data": {
    "symptoms": [
      "symptom1",
      "symptom2",
      "symptom3"
    ],
    "duration": {
      "symptom1": "5 days",
      "symptom2": "2 days"
    },
    "severity": {
      "symptom1": "moderate",
      "symptom2": "high"
    },
    "allergies": [
      "allergy1",
      "allergy2"
    ],
    "past_diseases": [
      "disease1",
      "disease2"
    ],
    "additional_notes": "string"
  },

  "consultation_summary": "partial summary|Clear and concise summary of the full conversation (max 1000 characters)"
}
