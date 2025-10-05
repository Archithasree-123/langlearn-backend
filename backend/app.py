from flask import Flask, jsonify
import speech_recognition as sr
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


app = Flask(__name__)

# ---------------- SETTINGS ----------------
AUDIO_FOLDER = "audio_samples"
DURATION = 5  # seconds
FS = 16000    # sample rate
TEMP_FILE = os.path.join(AUDIO_FOLDER, "temp_live.wav")
# ------------------------------------------

# Ensure audio folder exists
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# ---------------- MONGODB CONNECTION ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["Speech_recognition"]
collection = db["Transcription"]

@app.route("/", strict_slashes=False)
def home():
    return "✅ Live Speech Recognition API is running!"

@app.route("/live-speech-to-text", methods=["GET"], strict_slashes=False)
def live_speech_to_text():
    try:
        # Step 1: Record live audio
        print("🎤 Recording live audio...")
        audio_data = sd.rec(int(DURATION * FS), samplerate=FS, channels=1)
        sd.wait()

        # Step 1b: Convert to 16-bit PCM and save
        audio_int16 = np.int16(audio_data * 32767)
        write(TEMP_FILE, FS, audio_int16)
        print(f"✅ Recording saved at {TEMP_FILE}")

    except Exception as e:
        return jsonify({"error": f"Failed to record audio: {e}"}), 500

    try:
        # Step 2: Initialize recognizer
        recognizer = sr.Recognizer()

        # Step 3: Convert live audio to text
        with sr.AudioFile(TEMP_FILE) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print(f"📝 Recognized Text: {text}")

            # ---------------- STORE IN MONGODB ----------------
            doc = {
                "audio_file": TEMP_FILE,
                "transcript": text
            }
            collection.insert_one(doc)
            print("💾 Transcript saved to MongoDB")

            return jsonify({"transcript": text})

    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"API error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    app.run(debug=True)
