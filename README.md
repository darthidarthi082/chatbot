# 📦 Logistics Customer Support Chatbot (GenAI)
**Developer:** Darthi A | Internship Project | June 2026

---

## Project Structure

```
logistics_chatbot/
├── chatbot.py                        ← Main chatbot (Streamlit + Claude API)
├── 02_FAQ_Knowledge_Base.csv         ← 50 FAQ entries (auto-loaded by chatbot)
├── 01_Requirements_Document.docx     ← Week 1: Requirements doc
├── 03_Conversation_Flow_Document.docx ← Week 2: Conversation flows
├── 04_Testing_Report.docx            ← Week 3: Test results
├── 05_Analytics_Dashboard.html       ← Week 4: Open in any browser
└── README.md                         ← This file
```

---

## How to Run the Chatbot

### 1. Install Dependencies
```bash
pip install streamlit anthropic
```

### 2. Run the App
```bash
streamlit run chatbot.py
```

### 3. Enter API Key
- Open the sidebar in the Streamlit app
- Paste your **Anthropic API Key**
- Start chatting!

---

## Test Tracking IDs (Mock Data)

| Tracking ID     | Status            |
|-----------------|-------------------|
| LGX2025061201   | In Transit        |
| LGX2025061202   | Out for Delivery  |
| LGX2025061203   | Delivered         |
| LGX2025061204   | Delayed           |

---

## Test Pincodes

| Pincode | Location               |
|---------|------------------------|
| 607001  | Cuddalore, Tamil Nadu  |
| 600001  | Chennai, Tamil Nadu    |
| 110001  | Delhi                  |
| 400001  | Mumbai, Maharashtra    |
| 560001  | Bangalore, Karnataka   |

---

## Sample Queries to Test

- "Track my shipment LGX2025061201"
- "Is pincode 607001 serviceable?"
- "What are your delivery charges for 3kg?"
- "Warehouse in Chennai?"
- "My package is damaged"
- "I want to talk to a human agent"
- "When will my order be delivered?"

---

## Week-wise Deliverables

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1 | Requirements | `01_Requirements_Document.docx` + `02_FAQ_Knowledge_Base.csv` |
| 2 | Knowledge Base | `03_Conversation_Flow_Document.docx` |
| 3 | Development | `chatbot.py` + `04_Testing_Report.docx` |
| 4 | Dashboard | `05_Analytics_Dashboard.html` |

---

*Built with Python, Streamlit, and Anthropic Claude API*
