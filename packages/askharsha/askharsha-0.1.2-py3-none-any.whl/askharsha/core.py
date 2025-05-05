import requests
import re

class Chatbot:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": "AIzaSyB2CSaU-1T6i6EcJylA7u3Dkfd_flrsRKc"
        }

    def ask(self, question: str) -> str:
        payload = {
            "contents": [
                {
                    "parts": [{"text": question}]
                }
            ]
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()

            reply = data.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "")
            return self._sanitize(reply)
        except Exception as e:
            return f"Error: {str(e)}"

    def _sanitize(self, text: str) -> str:
        # Remove markdown-style bold/italic, preserve ** for exponentiation or inline code
        # Remove surrounding stars unless used in math/code
        text = re.sub(r'(?<!\w)\*{1,2}(?!\w)', '', text)  # Remove * or ** not between words
        return text
