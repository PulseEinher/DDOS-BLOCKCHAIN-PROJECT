# 🚨 DDoS Detection & Tamper-Proof Security Logging System

A production-structured Machine Learning + API + Dashboard system for detecting DDoS attacks using flow-based traffic features, with blockchain-style integrity logging for security event auditing.

This project demonstrates applied machine learning in cybersecurity, secure API design, defensive engineering, and tamper-evident logging.

---

## 📌 Project Overview

This system performs:

- Flow-based DDoS classification using a trained RandomForest model  
- Real-time inference via FastAPI  
- Interactive monitoring dashboard using Streamlit  
- Blockchain-style immutable ledger logging for detected DDoS events  
- Integrity verification of logged security events  

The system simulates a security monitoring pipeline where malicious network activity is detected and securely recorded.

---

## 🏗 Architecture

```text
                +----------------------+
                |  CIC-DDoS2019 Data   |
                +----------+-----------+
                           |
                           v
                  +----------------+
                  |  ML Training   |
                  | RandomForest   |
                  +--------+-------+
                           |
                     model.joblib
                           |
                           v
+----------------+   REST API   +------------------+
| Streamlit      | <----------> |  FastAPI Service |
| Dashboard      |              |  /predict        |
+----------------+              |  /ledger         |
                                |  /verify         |
                                +--------+---------+
                                         |
                                         v
                               +-------------------+
                               |  Blockchain Ledger|
                               |  (ledger.json)    |
                               +-------------------+
```

---

## 🔬 Machine Learning Component

- Algorithm: RandomForestClassifier  
- Problem Type: Binary Classification (Benign vs DDoS)  
- Dataset: CIC-DDoS2019  
- Preprocessing:
  - Removal of non-numeric columns
  - NaN and infinite value cleaning
  - Feature alignment to trained model size

The model is trained using `ml/train.py` and saved as:

```text
ml/model.joblib
```

The API loads this model at runtime with defensive error handling.

---

## 🚀 API Endpoints

### `GET /`
Returns service status message.

---

### `GET /health`

Health check endpoint.

Response:

```json
{
  "status": "ok",
  "model_loaded": true,
  "service": "ddos-detection-api"
}
```

---

### `POST /predict`

Performs flow classification.

Request:

```json
{
  "features": [0.0, 10.2, 5.6]
}
```

Response:

```json
{
  "prediction": "DDoS",
  "confidence": 0.9821,
  "features_used": 78,
  "model_decision": "statistical flow-based classification"
}
```

If a DDoS attack is detected, the event is written to the blockchain ledger.

---

### `GET /ledger`

Returns all logged DDoS events.

---

### `GET /ledger/verify`

Verifies blockchain integrity.

Ensures:

- No block tampering  
- No broken hash chain  
- Valid recalculated SHA256 hashes  

---

## 🔐 Blockchain-Style Ledger

Each detected DDoS event is stored as a block:

```json
{
  "index": 3,
  "timestamp": "2026-02-16T12:00:00",
  "prediction": "DDoS",
  "confidence": 0.98,
  "previous_hash": "abc123",
  "hash": "def456"
}
```

Each block includes:

- SHA256 hash of its contents  
- Reference to previous block  
- Immutable chaining  

This ensures tamper-evident logging for security audit scenarios.

---

## 📊 Streamlit Dashboard

Features:

- Single flow detection  
- CSV batch detection  
- Real-time DDoS event metrics  
- Ledger visualization  
- Integrity verification display  

Run dashboard:

```bash
streamlit run dashboard/app.py
```

---

## 🛠 Installation

Clone repository:

```bash
git clone https://github.com/PulseEinher/DDOS-BLOCKCHAIN-PROJECT.git
cd DDOS-BLOCKCHAIN-PROJECT
```

Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🧠 Train Model

Place dataset at:

```text
data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
```

Then run:

```bash
python ml/train.py
```

This generates:

```text
ml/model.joblib
```

---

## ▶ Run API

```bash
uvicorn api.main:app --reload
```

API runs at:

```text
http://127.0.0.1:8000
```

Interactive docs available at:

```text
http://127.0.0.1:8000/docs
```

---

## 🧪 Offline Replay Simulation

Simulates near real-time flow ingestion:

```bash
python offline_replay.py
```

Each detected DDoS event is automatically logged in the ledger.

---

## 📁 Project Structure

```text
DDOS-BLOCKCHAIN-PROJECT/
│
├── api/
│   └── main.py
│
├── dashboard/
│   └── app.py
│
├── ml/
│   └── train.py
│
├── blockchain/
│
├── data/
│   └── raw/   (ignored in git)
│
├── offline_replay.py
├── requirements.txt
├── README.md
├── .gitignore
```

---

## 🛡 Defensive Engineering Features

- Safe model loading (no startup crash)  
- Ledger auto-recovery if missing  
- Global exception handler  
- Feature length validation  
- Clean separation of concerns  
- Runtime integrity verification  

---

## 📈 Skills Demonstrated

- Machine Learning for Network Security  
- FastAPI REST API Development  
- Streamlit Dashboard Engineering  
- Data Preprocessing & Feature Engineering  
- Blockchain-style Hash Chaining  
- Secure Logging Design  
- Defensive Backend Architecture  
- Structured Project Organization  

---

## ⚠ Legal Disclaimer

This tool is developed strictly for:

- Educational purposes  
- Ethical security testing  
- Authorized environments only  

It simulates detection using offline dataset features and is not a live packet capture IDS.

---

## 👨‍💻 Author

Prateek Yadav  
Built as part of a professional cybersecurity portfolio project.
