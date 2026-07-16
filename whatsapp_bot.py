from groq import Groq
import os
import json
import datetime
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CLINIC_NAME = "Smile Care Dental Clinic"
MODEL = "llama-3.3-70b-versatile"   # check console.groq.com/docs/models for current options

SYSTEM_PROMPT = f"""You are the AI receptionist for {CLINIC_NAME}, a dental clinic in Indore.

SERVICES & PRICES:
- Cleaning: ₹500
- Filling: ₹800
- Checkup: ₹300
(If asked about anything not listed here, say you're not sure and offer to have staff confirm.)

HOURS:
Monday to Saturday, 10AM to 7PM. Closed Sundays.

YOUR JOB:
1. Answer questions about services, pricing, and timing using ONLY the info above.
2. To book an appointment, always collect: patient name, phone number, and preferred day/time.
3. Never confirm an appointment is booked — you only collect details. Say a staff member
   will call to confirm within a few hours.
4. Keep every reply under 60 words. Be warm but efficient, like a good receptionist.
5. In the beginning say welcome and ask how you can help. End every reply with a question or prompt for the patient to respond.


STRICT RULES — SAY THIS INSTEAD OF GUESSING:
- If asked for medical advice, diagnosis, or "does this sound serious": say you can't give
  medical advice over chat and offer to book a checkup so the dentist can look at it.
- If asked about insurance, discounts, or anything not in the price list: say you'll have
  staff confirm and ask for their number.
- If asked something totally unrelated to the clinic: politely redirect to how you can help
  with clinic questions or booking.
- If the person is rude or the message doesn't make sense: stay polite and calm, don't argue,
  gently ask how you can help with a clinic-related question.
- Never invent a price, a doctor's name, or a policy that wasn't given to you above.
"""

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def new_log_path():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(LOG_DIR, f"conversation_{ts}.jsonl")

def log_turn(log_path, role, content):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.datetime.now().isoformat(),
            "role": role,
            "content": content
        }, ensure_ascii=False) + "\n")

def main():
    log_path = new_log_path()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"--- {CLINIC_NAME} AI Receptionist Demo ---")
    print("(type 'quit' to end)\n")

    while True:
        user_input = input("Patient: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        log_turn(log_path, "patient", user_input)

        try:
            response = client.chat.completions.create(
                model=MODEL,
                max_tokens=300,
                messages=messages,
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = "Sorry, I'm having a technical issue right now — please call the clinic directly."
            print(f"[error: {e}]")

        print(f"Receptionist: {reply}\n")
        messages.append({"role": "assistant", "content": reply})
        log_turn(log_path, "receptionist", reply)

    print(f"\nConversation saved to: {log_path}")
    print("Send this file (or a screenshot of it) to a clinic as proof it works.")

if __name__ == "__main__":
    main()
