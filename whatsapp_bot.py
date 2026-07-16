import os
import json
import datetime
from flask import Flask, request
from groq import Groq
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CLINIC_NAME = "Smile Care Dental Clinic"
MODEL = "llama-3.3-70b-versatile"

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

STRICT RULES:
- If asked for medical advice or diagnosis: say you can't give medical advice over chat and offer to book a checkup.
- If asked about insurance/discounts or anything not in the price list: say staff will confirm, ask for their number.
- If asked something unrelated to the clinic: politely redirect to clinic questions or booking.
- If the person is rude or unclear: stay calm, don't argue, ask how you can help.
- Never invent a price, doctor's name, or policy not given above.
"""

conversations = {}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    if sender not in conversations:
        conversations[sender] = [{"role": "system", "content": SYSTEM_PROMPT}]

    conversations[sender].append({"role": "user", "content": incoming_msg})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=300,
            messages=conversations[sender],
        )
        reply_text = response.choices[0].message.content
    except Exception as e:
        reply_text = "Sorry, I'm having a technical issue right now — please call the clinic directly."
        print(f"[error: {e}]")

    conversations[sender].append({"role": "assistant", "content": reply_text})

    twiml = MessagingResponse()
    twiml.message(reply_text)
    return str(twiml)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
