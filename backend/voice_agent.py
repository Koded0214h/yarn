import os
import asyncio
import logging
from dotenv import load_dotenv

# Load env variables from root or backend
load_dotenv()

# Map the project's GEMINI_API_KEY to the Google plugin's expected GOOGLE_API_KEY
if "GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from livekit.agents import JobContext, WorkerOptions, cli, LanguageCode, AutoSubscribe
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import spitch, silero, google, elevenlabs

logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)

# Default system prompt instructing Gemini how to act for callers
SYSTEM_PROMPT = """You are YARN, a friendly voice assistant for everyday Nigerians.
Greet users naturally.
You must speak in the language chosen by the caller (English, Pidgin, Yoruba, Hausa, or Igbo).
If the caller speaks to you in English, you must respond only in English. If the caller speaks to you in Pidgin, you must respond only in Pidgin. Do not speak Pidgin to an English speaker, and do not speak English to a Pidgin speaker.
Keep all responses extremely short, friendly, and conversational — ideally 1 to 2 sentences max, as it is being read over a voice call.
Sprinkle simple local terms naturally where appropriate.
If they want to perform an action (like transfer money or ask for price), explain what we can do.
"""

class YarnAssistant(Agent):
    def __init__(self):
        super().__init__(instructions=SYSTEM_PROMPT)

    async def on_enter(self) -> None:
        # Save original options
        orig_lang = self.session.tts._opts.language
        orig_voice = self.session.tts._opts.voice

        try:
            # 1. English
            self.session.tts._opts.language = LanguageCode("en")
            self.session.tts._opts.voice = "lina"
            handle_en = self.session.say("Welcome to YARN. Press 1 for English,", allow_interruptions=False)
            await handle_en

            # 2. Yoruba
            self.session.tts._opts.language = LanguageCode("yo")
            self.session.tts._opts.voice = "femi"
            handle_yo = self.session.say("tẹ eji fun Yoruba,", allow_interruptions=False)
            await handle_yo

            # 3. Igbo
            self.session.tts._opts.language = LanguageCode("ig")
            self.session.tts._opts.voice = "lina"
            handle_ig = self.session.say("pia atọ maka Igbo,", allow_interruptions=False)
            await handle_ig

            # 4. Hausa
            self.session.tts._opts.language = LanguageCode("ha")
            self.session.tts._opts.voice = "lina"
            handle_ha = self.session.say("danna huɗu don Hausa.", allow_interruptions=False)
            await handle_ha

        finally:
            # Restore original options
            self.session.tts._opts.language = orig_lang
            self.session.tts._opts.voice = orig_voice

async def entrypoint(ctx: JobContext):
    logger.info("Connecting to LiveKit room %s", ctx.room.name)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Initialize STT and TTS with default settings (ElevenLabs STT for English, Spitch for TTS)
    eleven_stt = elevenlabs.STT(model_id="scribe_v2_realtime")
    spitch_stt = spitch.STT(language="en")
    spitch_tts = spitch.TTS(language="en", voice="lina")
    vad = silero.VAD.load()
    llm = google.LLM(model="gemini-2.5-flash")
 
    # Set up the AgentSession
    session = AgentSession(
        stt=eleven_stt,
        vad=vad,
        llm=llm,
        tts=spitch_tts,
        allow_interruptions=True,
    )

    assistant = YarnAssistant()

    # Listen for DTMF (keypad press) events to switch languages
    @ctx.room.on("sip_dtmf_received")
    def on_sip_dtmf(dtmf):
        digit = dtmf.digit
        logger.info("Received DTMF digit: %s", digit)

        lang_map = {
            "1": ("en", "lina", "English and Pidgin"),
            "2": ("yo", "femi", "Yoruba"),
            "3": ("ig", "lina", "Igbo"),
            "4": ("ha", "lina", "Hausa"),
        }

        if digit in lang_map:
            lang_code, voice, lang_name = lang_map[digit]
            logger.info("Switching language to %s (%s) with voice %s", lang_name, lang_code, voice)

            # Update STT options on the fly depending on selected language
            if lang_code == "en":
                session._stt = eleven_stt
            else:
                session._stt = spitch_stt
                spitch_stt.update_options(language=lang_code)

            # Update active recognition loop STT node
            if session._activity and session._activity._audio_recognition:
                session._activity._audio_recognition.update_stt(
                    session._agent.stt_node if session.stt else None
                )
 
            # Update Spitch TTS options on the fly
            spitch_tts._opts.language = LanguageCode(lang_code)
            spitch_tts._opts.voice = voice

            # Define the async operations to run inside a task
            async def update_agent_state():
                new_instructions = SYSTEM_PROMPT + f"\nThe caller has chosen {lang_name}. You MUST now speak, reply, and interact ONLY in {lang_name}. Keep all responses short and conversational."
                await assistant.update_instructions(new_instructions)
                session.generate_reply(
                    instructions=f"Greet the user warmly in {lang_name} and ask how you can help them today. Remember to keep it very short."
                )

            # Schedule the async updates on the running event loop
            asyncio.create_task(update_agent_state())

    # Start the session
    await session.start(room=ctx.room, agent=assistant)
    logger.info("Agent session started in room %s", ctx.room.name)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="yarn"))
