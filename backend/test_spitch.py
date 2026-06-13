import os
from dotenv import load_dotenv

# Load .env file from the current directory (backend/)
load_dotenv()

from spitch import Spitch

print("Checking environment variables...")
api_key = os.environ.get("SPITCH_API_KEY")
if not api_key:
    print("❌ Error: SPITCH_API_KEY is not set in your .env file!")
    exit(1)
else:
    print(f"✅ SPITCH_API_KEY found (Starts with: {api_key[:8]}...)")

# Initialize client
client = Spitch(api_key=api_key)

print("\n--- Testing Text-to-Speech (TTS) ---")
try:
    print("Sending synthesis request for text: 'Welcome to YARN'...")
    response = client.speech.generate(
        text="Welcome to YARN",
        language="en",
        voice="lina"
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.headers.get('content-type')}")
    
    # Read the raw response body
    body = response.read()
    print(f"Response Body Length: {len(body)} bytes")
    
    if response.status_code == 200:
        # Check if the content is actually audio or text/JSON error
        if len(body) < 100:
            print("❌ Warning: Response is too short to be audio! Content:")
            print(body.decode("utf-8", errors="ignore"))
        else:
            print("✅ Success! TTS returned valid audio data.")
    else:
        print("❌ Error from Spitch server:")
        print(body.decode("utf-8", errors="ignore"))

except Exception as e:
    print("❌ Request failed with exception:")
    import traceback
    traceback.print_exc()

print("\n--- Testing Speech-to-Text (STT/Transcribe) ---")
try:
    print("Sending dummy audio transcription request...")
    # Create 1 second of dummy silent 16kHz mono 16-bit WAV bytes
    import io
    import wave
    
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"\x00" * 32000)
    wav_bytes = wav_io.getvalue()

    response = client.speech.transcribe(
        language="en",
        content=wav_bytes
    )
    print("✅ Success! STT returned transcript:", response.text)
except Exception as e:
    print("❌ STT Request failed with exception:")
    import traceback
    traceback.print_exc()
