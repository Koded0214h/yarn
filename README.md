# Product Requirements Document (PRD)
## YARN Prototype – "Voice-First Agent for the Oral Majority"
**Version:** 1.0 (Prototype)
**Goal:** Build a functional frontend chatbot that demonstrates autonomous task execution (search, send message, create doc) to represent the full YARN vision.

---

## 1. Prototype Scope (What we actually build)

| In Scope (For Demo) | Out of Scope (Vision for Later) |
| --- | --- |
| Web-based chat UI (simulates a phone call) | Actual phone number (Twilio/Voice integration) |
| Text + Voice input (browser mic) | Full dialect support (use English + Pidgin snippets) |
| 5 core autonomous actions (see below) | All 20 use cases |
| Simulated "Safeword" (type or say "stop") | Real banking transactions (use mock APIs) |
| Backend that calls real 3rd party APIs | Production-scale security |

---

## 2. Core User Stories (For Prototype)

As a **user** (simulated via chat), I want to:

1. **Send money** by typing/talking: *"Send N5000 to Alhaji Musa"* and see the system confirm before executing.
2. **Check market price** autonomously: *"What is tomato price in Dawanau today?"* → System searches the web or calls a price API.
3. **Send a WhatsApp message** for me: *"Tell Mary I'm coming by 5pm"* (simulate via API or log).
4. **Create an invoice** by voice: *"Write a receipt for tiling work, N80,000"* → System generates a PDF and provides a link.
5. **Emergency trigger** with safeword: When I say *"Safeword: help"* → System confirms it would alert contacts.

---

## 3. Functional Requirements

### 3.1 Frontend (Chatbot Interface)

**UI Components:**
- Chat window displaying conversation history (user messages left, YARN responses right).
- **Microphone button** (browser speech-to-text) + text input field.
- A badge showing: *"Simulated Phone Call | Your Language: English/Pidgin"*
- A visible **"Safeword" status** (green = safe, red = emergency triggered).
- **Action Log panel** (optional but powerful) showing: *"YARN executed: Search | Transfer | WhatsApp"*

**Autonomy Demo Feature:**
- After any user request, show a typing indicator labeled *"YARN is acting autonomously..."* then display the result.

### 3.2 Backend (Orchestrator)

**Tech Stack Suggestion:**
- **Backend:** Python (FastAPI) – easy to integrate APIs.
- **LLM for Intent:** Gemini 2.5 Flash google-genai
- **Speech-to-Text:** Browser's `webkitSpeechRecognition` (frontend) OR AssemblyAI / Groq Whisper (backend for uploaded audio).
- **Database:** PostgreSQL

**Core Backend Services:**

| Service | Purpose | Prototype Implementation |
| --- | --- | --- |
| Intent Router | Understand user request | Send user text to LLM with prompt: *"Classify into: transfer, search, whatsapp, invoice, emergency, other"* |
| Transfer Executor | "Send money" | Mock API that returns `{success: true, tx_ref: "YARN-123"}` |
| Web Search Tool | "What is tomato price" | Call SerpAPI or Google Programmable Search, extract top result text |
| WhatsApp Sender | "Tell Mary I'm coming" | Use Twilio WhatsApp Sandbox OR just log to console and return a mock success message |
| Invoice Generator | "Create receipt for N80k tiling" | Generate HTML → PDF (using pdfkit or browserless) and return a public download URL (mock) |
| Safeword Detector | "Safeword: help" | Check incoming text for keyword "safeword" or "stop". If found, return emergency flag. |

### 3.3 Autonomous "Browser Search" Task (Key Demo)

**User says:** *"What is the current price of tomatoes in Dawanau market, Kano?"*

**Backend flow:**
1. LLM extracts: `{query: "tomato price Dawanau market Kano today", type: "search"}`
2. Backend calls **SerpAPI** (Google Search) or **Bing Web Search API**.
3. Parses first result text.
4. LLM rewrites answer in simple English/Pidgin.
5. Returns: *"As of this morning, tomato price for Dawanau market is between N25,000 and N30,000 per basket. You can check again tomorrow."*

**Fallback if API fails:** Return a realistic mocked response + note *"(simulated data)"*

### 3.4 Data Model (Simplified)

```json
{
  "session_id": "uuid",
  "history": [
    {"role": "user", "text": "send 5000 to Alhaji Musa"},
    {"role": "assistant", "text": "Confirm transfer of N5000 to Alhaji Musa? Reply YES", "action": "pending_transfer"}
  ],
  "pending_action": {
    "type": "transfer",
    "amount": 5000,
    "recipient": "Alhaji Musa",
    "status": "awaiting_confirmation"
  },
  "safeword_triggered": false
}
```

---

## 4. API Endpoints for Prototype

| Endpoint | Method | Request Body | Response | Action |
| --- | --- | --- | --- | --- |
| `/api/chat` | POST | `{message: "send money...", session_id: "abc"}` | `{reply: "...", action_taken: {...}}` | Routes intent, executes tool, returns user-facing reply |
| `/api/confirm` | POST | `{session_id: "abc", confirmed: true}` | `{reply: "Transfer completed. Ref: TX-123"}` | Confirms high-stakes action |
| `/api/emergency` | POST | `{session_id: "abc", safeword: "help"}` | `{reply: "Emergency protocol simulated. Contacts alerted."}` | Triggers emergency |

---

## 5. Non-Functional Requirements (Prototype)

- **Latency:** Every action (including web search) must complete within 5 seconds (show loading state).
- **Mock vs Real:** Clearly label simulated actions: *"[SIMULATED] Would send WhatsApp"* but for **search**, show real results.
- **Demo Reliability:** Pre-cache responses for the exact demo script (so you never get an API failure on stage).

---

## 6. How to Demonstrate "Autonomous Tasks" Effectively

During your OPay Innovation Challenge demo, show this sequence:

**Step 1 (Simple transfer):**  
User: *"Send 2000 naira to Bisi"*  
YARN: *"Confirm sending N2000 to Bisi? Say YES."*  
User: *"YES"*  
YARN: *"Done. Transaction ID: YARN-001."*

**Step 2 (Autonomous search – THE WINNER):**  
User: *"What is the price of yam in Bodija market?"*  
YARN: *[Shows "Searching autonomously..." then replies]* "As of 9am today, a 50kg tuber of yam sells for N15,000 to N18,000 at Bodija market. This is from a market report published 2 hours ago."

**Step 3 (Invoice generation):**  
User: *"Create an invoice for painting job, N45,000, for Mr. Ade"*  
YARN: *[Generates PDF, returns link]* "Here is your invoice. I've sent it to your email (simulated)."

**Step 4 (Safeword kill switch):**  
User: *"Safeword: cancel everything"*  
YARN: *"Safeword recognized. All pending actions cancelled. Session locked."*

---

## 7. Services & APIs to Use (Free/Low Cost for Prototype)

| Service | Purpose | Free Tier | Integration Complexity |
| --- | --- | --- | --- |
| **Groq Cloud** | LLM for intent + response (fastest) | Yes (30 req/min) | Low (REST) |
| **SerpAPI** | Google search results | 100 searches/month free | Low |
| **Twilio SendGrid** | Email invoice link | 100 emails/day free | Low |
| **Twilio WhatsApp Sandbox** | Simulate WhatsApp sending | Free (with registration) | Medium |
| **Browser SpeechRecognition** | Voice input (frontend) | Free | Low |
| **jsPDF or PDFKit** | Generate invoice PDF | Free (library) | Low |

**Fallback Strategy:** If any API fails during demo, hardcode responses for the exact demo script (unethical but accepted for prototypes). Better: use fallback mock data with a note.

---

## 8. Mock UI Wireframe (Text Description)

```
-------------------------------------------------
|  YARN  | Your Voice Agent          [Safe]    |
-------------------------------------------------
|  [Chat History]                               |
|                                               |
|  You: Send 5000 to Alhaji                     |
|  YARN: Confirm N5000 to Alhaji? Say YES.      |
|  You: YES                                     |
|  YARN: ✅ Transfer done. Ref: YARN-456         |
|                                               |
|  You: What is tomato price today?             |
|  YARN: 🔍 Searching autonomously...            |
|  YARN: Tomato price is N28,000 per basket.    |
|                                               |
|  [Type your message...]        [🎤] [Send]    |
-------------------------------------------------
|  Action Log:                                  |
|  - Intent: Transfer (confirmed)               |
|  - Tool: Web Search (SerpAPI)                 |
|  - Status: Success                            |
-------------------------------------------------
```

---

## 9. Development Phases (For a 2-Week Sprint)

| Phase | Days | Deliverable |
| --- | --- | --- |
| 1. Setup | 1-2 | Node.js server, basic chat endpoint, LLM integration (Groq) |
| 2. Intent Router | 1 | LLM prompt that returns JSON intent: `{type, params}` |
| 3. Tool Implement | 3-4 | Web search (SerpAPI), mock transfer, mock WhatsApp, invoice generator |
| 4. Frontend UI | 2-3 | Chat window, mic input, action log, safeword badge |
| 5. Integration + Demo Polish | 2 | Connect frontend to backend, hardcode demo fallbacks, test script |

---

## 10. Success Metrics for the Prototype

- [ ] User can **send a mock transfer** (confirmation flow works).
- [ ] User can ask a **real-time market price** and YARN returns a real web search result.
- [ ] User can **generate an invoice** and receive a PDF link.
- [ ] **Safeword** immediately cancels any pending action.
- [ ] Entire flow works **under 5 seconds** per action.
- [ ] **No typing required** beyond first login (mic works for all inputs).

---