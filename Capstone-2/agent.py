import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class VoiceToImageAgent:
    def __init__(self):
        self.client = OpenAI()

    def transcribe(self, audio_path):
        logging.info("Audio received")
        logging.info(f"Transcribing audio from {audio_path}")
        with open(audio_path, "rb") as f:
            text = self.client.audio.transcriptions.create(
                file=f,
                model="whisper-1"
            )
        logging.info(f"Transcription: \"{text.text}\"")
        return text.text

    def text_to_prompt(self, transcript):
        logging.info("Generating image prompt")
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Convert user intent into a detailed image description. Keep it descriptive and visual."},
                {"role": "user", "content": transcript}
            ]
        )
        prompt = response.choices[0].message.content
        logging.info(f"Image prompt generated: \"{prompt}\"")
        return prompt

    def generate_image(self, prompt):
        logging.info("Generating image")
        try:
             # Using dall-e-3 as it's the current standard. 
             # Note: dall-e-3 requires 1024x1024.
            result = self.client.images.generate(
                model="dall-e-3", 
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = result.data[0].url
            logging.info("Image generation completed")
            return image_url
        except Exception as e:
            logging.error(f"Error generating image: {e}")
            raise e
