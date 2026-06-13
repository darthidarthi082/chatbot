"""
Logistics Customer Support Chatbot
Powered by Groq API (Llama 3) + Streamlit
Developed by: Darthi A | GenAI Internship | June 2026
"""

import streamlit as st
import requests
import csv, json, datetime, os, re

PAGE_TITLE = "LogiSupport AI Chatbot"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

MOCK_SHIPMENTS = {
    "LGX2025061201": {"status": "In Transit", "location": "Chennai Distribution Hub", "updated": "12 Jun 2026, 10:32 AM", "eta": "14 Jun 2026"},
    "LGX2025061202": {"status": "Out for Delivery", "location": "Local Delivery Agent", "updated": "12 Jun 2026, 09:15 AM", "eta": "Today by 6:00 PM"},
    "LGX2025061203": {"status": "Delivered", "location": "Delivered to Doorstep", "updated": "11 Jun 2026, 03:45 PM", "eta": "Delivered"},
    "LGX2025061204": {"status": "Delayed", "location": "Bangalore Sorting Facility", "updated": "12 Jun 2026, 06:00 AM", "eta": "16 Jun 2026"},
}
SERVICEABLE_PINCODES = {
    "607001": "Cuddalore, Tamil Nadu", "600001": "Chennai, Tamil Nadu",
    "110001": "Delhi", "400001": "Mumbai, Maharashtra", "560001": "Bangalore, Karnataka",
}
WAREHOUSES = {
    "chennai":   {"name": "Chennai Central Hub",   "address": "45, Nehru Street, Perambur, Chennai - 600011",     "hours": "Mon-Sat 8AM-8PM", "phone": "044-12345678"},
    "delhi":     {"name": "Delhi NCR Mega Hub",    "address": "Plot 12, Sector 5, Dwarka, New Delhi - 110075",     "hours": "24/7",            "phone": "011-87654321"},
    "bangalore": {"name": "Bangalore South Hub",   "address": "No. 8, Industrial Layout, Hosur Road, BLR-560068", "hours": "Mon-Sat 8AM-8PM", "phone": "080-11223344"},
    "mumbai":    {"name": "Mumbai Logistics Park",  "address": "Unit 3, Turbhe MIDC, Navi Mumbai - 400705",        "hours": "Mon-Sat 7AM-9PM", "phone": "022-55667788"},
}
PRICING = {
    "standard": {"label": "Standard (3-5 days)", "base": 50,  "per_kg": 20},
    "express":  {"label": "Express (1-2 days)",  "base": 150, "per_kg": 50},
    "overnight":{"label": "Overnight Delivery",  "base": 300, "per_kg": 80},
}

def load_faq(filepath="02_FAQ_Knowledge_Base.csv"):
    faqs = []
    if os.path.exists(filepath):
        with open(filepath, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                faqs.append(row)
    return faqs

def build_faq_context(faqs):
    lines = ["LOGISTICS FAQ KNOWLEDGE BASE:", ""]
    for faq in faqs:
        lines.append(f"Q: {faq['Customer Query']}")
        lines.append(f"A: {faq['Chatbot Response']}")
        lines.append("")
    return "\n".join(lines)

def track_shipment(tid):
    tid = tid.strip().upper()
    if tid in MOCK_SHIPMENTS:
        s = MOCK_SHIPMENTS[tid]
        return f"Tracking ID: {tid}\nStatus: {s['status']}\nLocation: {s['location']}\nUpdated: {s['updated']}\nETA: {s['eta']}"
    return f"No shipment found for {tid}. Please verify the ID."

def check_serviceability(pc):
    pc = pc.strip()
    if pc in SERVICEABLE_PINCODES:
        return f"Pincode {pc} ({SERVICEABLE_PINCODES[pc]}) is serviceable. Standard and Express delivery available."
    return f"Pincode {pc} is not directly serviceable. Drop-off at nearest facility is available."

def get_warehouse_info(city):
    for k, info in WAREHOUSES.items():
        if k in city.lower():
            return f"{info['name']}\nAddress: {info['address']}\nHours: {info['hours']}\nPhone: {info['phone']}"
    return f"No warehouse found for {city}. We have facilities in Chennai, Delhi, Bangalore, and Mumbai."

def get_pricing_quote(weight_kg):
    try:
        w = float(weight_kg)
        lines = ["Pricing Quote:"]
        for info in PRICING.values():
            lines.append(f"- {info['label']}: Rs. {info['base'] + info['per_kg']*w:.0f}")
        return "\n".join(lines)
    except:
        return "Please provide weight in kg (e.g. 2kg)."

def extract_tracking_id(text):
    m = re.search(r'\bLGX\d{10}\b', text, re.IGNORECASE)
    return m.group(0).upper() if m else None

def extract_pincode(text):
    m = re.search(r'\b\d{6}\b', text)
    return m.group(0) if m else None

def extract_weight(text):
    m = re.search(r'(\d+\.?\d*)\s*(?:kg|kgs|kilogram)', text, re.IGNORECASE)
    return m.group(1) if m else None

def detect_city(text):
    for city in WAREHOUSES:
        if city in text.lower():
            return city
    return None

def build_system_prompt(faq_context):
    return f"""You are LogiSupport, a friendly AI customer support assistant for a logistics company.
You help with: shipment tracking, delivery updates, pricing, service availability, warehouse info, claims, and escalations.
Rules:
- Be polite, concise, and empathetic
- Use any [SYSTEM DATA] provided directly in your response
- Never make up shipment data
- After 2 failed attempts, offer human escalation
- End responses with a helpful follow-up question
Current date: {datetime.datetime.now().strftime("%d %B %Y")}
---
{faq_context}"""

def get_bot_response(user_message, conversation_history, faq_context, api_key):
    lower = user_message.lower()
    tid = extract_tracking_id(user_message)
    pc  = extract_pincode(user_message)
    wt  = extract_weight(user_message)
    ct  = detect_city(user_message)
    tool_result = None

    if tid and any(w in lower for w in ["track","where","status","shipment","package","delivery","when"]):
        tool_result = track_shipment(tid)
    elif pc and any(w in lower for w in ["deliver","service","area","available","pincode"]):
        tool_result = check_serviceability(pc)
    elif ct and any(w in lower for w in ["warehouse","facility","pickup","drop","address","hub"]):
        tool_result = get_warehouse_info(ct)
    elif wt and any(w in lower for w in ["price","cost","charge","rate","quote","how much"]):
        tool_result = get_pricing_quote(wt)

    full_message = user_message
    if tool_result:
        full_message += f"\n\n[SYSTEM DATA - use this in your response]:\n{tool_result}"

    messages = [{"role": "system", "content": build_system_prompt(faq_context)}]
    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": full_message})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.7
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon="📦", layout="centered")
    st.markdown("""
    <style>
    .chat-header{background:linear-gradient(135deg,#1B3A6B,#2E5EAA);color:white;
                 padding:18px 24px;border-radius:12px;margin-bottom:20px;text-align:center;}
    .chat-header h2{margin:0;font-size:1.4rem;}
    .chat-header p{margin:4px 0 0;font-size:0.85rem;opacity:0.85;}
    </style>
    <div class='chat-header'>
      <h2>📦 LogiSupport AI Assistant</h2>
      <p>Shipment Tracking · Delivery Updates · Pricing · Warehouse Info · Claims</p>
    </div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### LogiSupport AI")
        api_key = st.text_input("🔑 Groq API Key", type="password",
                                help="Get free key at console.groq.com")
        st.caption("Free key at [console.groq.com](https://console.groq.com)\nKey starts with: **gsk_**")
        st.markdown("---")
        st.markdown("**Quick Topics**")
        for t in ["🚚 Track Shipment","📅 Delivery ETA","💰 Pricing",
                  "📍 Service Availability","🏭 Warehouse Info","⚠️ File a Claim","👤 Talk to Agent"]:
            st.markdown(f"- {t}")
        st.markdown("---")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        st.caption("LogiSupport AI · Groq Llama 3 · Darthi A")

    faqs = load_faq()
    faq_context = build_faq_context(faqs)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        greeting = ("Hello! 👋 Welcome to **LogiSupport**. I'm your AI assistant.\n\n"
                    "I can help you with:\n"
                    "- 📦 **Track a shipment** (e.g. LGX2025061201)\n"
                    "- 🚚 **Delivery status & ETA**\n"
                    "- 💰 **Pricing & charges**\n"
                    "- 📍 **Service availability** by pincode\n"
                    "- 🏭 **Warehouse & pickup** info\n"
                    "- ⚠️ **Claims** for damaged/lost shipments\n"
                    "- 👤 **Talk to a human agent**\n\n"
                    "How can I assist you today?")
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="📦" if msg["role"] == "assistant" else "🙂"):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your message here...")
    if user_input:
        if not api_key:
            st.warning("⚠️ Please enter your Groq API Key in the sidebar. Key starts with gsk_...")
            return
        if not api_key.startswith("gsk_"):
            st.error("❌ Invalid key. Groq API keys start with 'gsk_'. Get yours free at console.groq.com")
            return

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🙂"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="📦"):
            with st.spinner("LogiSupport is thinking..."):
                try:
                    reply = get_bot_response(user_input, st.session_state.messages[:-1], faq_context, api_key)
                except Exception as e:
                    reply = f"⚠️ Error: {str(e)}\nPlease check your API key and try again."
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
