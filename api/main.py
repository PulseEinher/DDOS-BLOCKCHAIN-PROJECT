############################################################
######################## IMPORTS ###########################
############################################################

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from pydantic import BaseModel

import joblib
import numpy as np
import json
import hashlib
import os

from datetime import datetime


############################################################
###################### APP INIT ############################
############################################################

app = FastAPI(title="DDoS Detection API")


############################################################
###################### MODEL LOADING #######################
############################################################

MODEL_PATH = "ml/model.joblib"
model = None

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None
else:
    print("Model file not found. API started without model.")


############################################################
###################### LEDGER SETUP ########################
############################################################

LEDGER_FILE = "blockchain/ledger.json"


def load_ledger():
    """
    Load ledger safely.
    If file missing or corrupted, return empty chain.
    """
    if not os.path.exists(LEDGER_FILE):
        return {"chain": []}

    try:
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"chain": []}


def save_ledger(data):
    """
    Save ledger to file.
    """
    with open(LEDGER_FILE, "w") as f:
        json.dump(data, f, indent=4)


def hash_block(block):
    """
    Generate SHA256 hash of a block.
    """
    encoded = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def add_block(prediction, confidence):
    """
    Add new block to blockchain ledger.
    """
    ledger = load_ledger()
    chain = ledger["chain"]

    previous_hash = chain[-1]["hash"] if chain else "0"

    block = {
        "index": len(chain) + 1,
        "timestamp": datetime.utcnow().isoformat(),
        "prediction": prediction,
        "confidence": confidence,
        "previous_hash": previous_hash
    }

    block["hash"] = hash_block(block)
    chain.append(block)
    save_ledger(ledger)


############################################################
###################### REQUEST MODEL #######################
############################################################

class FlowFeatures(BaseModel):
    features: list


############################################################
###################### GLOBAL HANDLER ######################
############################################################

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Prevent stack traces from leaking in production.
    """
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


############################################################
######################## ENDPOINTS #########################
############################################################


@app.post("/predict")
def predict(data: FlowFeatures):

    # Ensure model is loaded
    if model is None:
        return {
            "error": "Model not loaded. Please train model first."
        }

    if not isinstance(data.features, list):
        return {"error": "Features must be a list of numbers"}

    expected_features = model.n_features_in_

    cleaned_features = []

    for x in data.features:
        try:
            cleaned_features.append(float(x))
        except Exception:
            continue

    if len(cleaned_features) == 0:
        return {"error": "No valid numeric features provided"}

    # Pad or trim to expected size
    if len(cleaned_features) < expected_features:
        cleaned_features += [0.0] * (expected_features - len(cleaned_features))
    else:
        cleaned_features = cleaned_features[:expected_features]

    X = np.array(cleaned_features).reshape(1, -1)

    prediction = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]
    confidence = float(probabilities[prediction])

    label = "DDoS" if prediction == 1 else "Benign"

    # Log only malicious events
    if label == "DDoS":
        add_block(label, confidence)

    return {
        "prediction": label,
        "confidence": round(confidence, 4),
        "features_used": expected_features,
        "model_decision": "statistical flow-based classification"
    }


@app.get("/")
def root():
    return {"message": "DDoS Detection API is running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "service": "ddos-detection-api"
    }


@app.get("/model")
def model_info():

    if model is None:
        return {
            "error": "Model not loaded"
        }

    return {
        "model_type": "RandomForestClassifier",
        "problem_type": "Binary Classification (Benign vs DDoS)",
        "features_expected": model.n_features_in_,
        "training_dataset": "CIC-DDoS2019",
        "classes": {
            "0": "Benign",
            "1": "DDoS"
        }
    }


@app.get("/ledger")
def view_ledger():
    ledger = load_ledger()
    return {
        "total_events": len(ledger["chain"]),
        "events": ledger["chain"]
    }


@app.get("/ledger/verify")
def verify_ledger():
    ledger = load_ledger()
    chain = ledger["chain"]

    if not chain:
        return {
            "valid": True,
            "message": "Ledger is empty but valid"
        }

    for i in range(len(chain)):
        block = chain[i]

        recalculated_hash = hash_block({
            "index": block["index"],
            "timestamp": block["timestamp"],
            "prediction": block["prediction"],
            "confidence": block["confidence"],
            "previous_hash": block["previous_hash"]
        })

        if block["hash"] != recalculated_hash:
            return {
                "valid": False,
                "error": f"Tampering detected at block {block['index']}"
            }

        if i > 0 and block["previous_hash"] != chain[i - 1]["hash"]:
            return {
                "valid": False,
                "error": f"Broken chain at block {block['index']}"
            }

    return {
        "valid": True,
        "message": "Ledger integrity verified successfully"
    }
