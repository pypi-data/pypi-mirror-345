from logging import getLogger

import requests
from django.conf import settings

logger = getLogger(__file__)

api_key = settings.AI_SERVICE_API_KEY
base_url = settings.AI_SERVICE_DEMO_URL
headers = {"api-key": api_key}


class AIProcessing:
    """
    This class handles the AI processing for submissions

    For this to work, you must specify the AI_SERVICE_DEMO_URL
    and LEARNGUAL_AI_API_KEY in your settings.py file.
    """

    @staticmethod
    def analyze_audio(
        audio,
        reference_text,
        scripted: bool = False,
        prompt: str = None,
        language: str = None,
        query_string: str = None,
    ):
        """
        this communicates with the AI model and returns the analysis results
        for the given audio
        """
        base_url = settings.AI_SERVICE_DEMO_URL
        if not str(base_url).endswith("/"):
            base_url += "/"

        files = {"audio_data": ("audio.mp3", audio)}
        payload = {"reference_text": reference_text, "scripted": scripted}

        if prompt:
            payload["prompt"] = prompt

        if language:
            payload["language"] = language

        if query_string:
            base_url += "?" + query_string

        response = requests.post(
            url=base_url,
            headers=headers,
            files=files,
            data=payload,
        )
        if response.status_code == 200:
            return {"status": True, "response": response}

        else:
            return {"status": False, "response": response}

    @staticmethod
    def relevance(topic: str, essay: str, query_string: str = None):
        base_url = settings.AI_SERVICE_DEMO_URL

        if not str(base_url).endswith("/"):
            base_url += "/"

        base_url = base_url.rstrip("process/") + "/relevance/"

        if query_string:
            base_url += "?" + query_string

        response = requests.post(
            url=base_url,
            headers=headers,
            data={"topic": topic, "essay": essay},
        )

        if response.status_code == 200:
            return {"status": True, "response": response}

        else:
            return {"status": False, "response": response}

    def grammar(text_body: str, query_string: str = None):
        base_url: str = settings.AI_SERVICE_DEMO_URL

        if not str(base_url).endswith("/"):
            base_url += "/"

        base_url = base_url.rstrip("process/") + "/gammar/"
        if query_string:
            base_url += "?" + query_string

        response = requests.post(
            url=base_url,
            headers=headers,
            data={"speech": text_body},
        )

        if response.status_code == 200:
            return {"status": True, "response": response}

        else:
            return {"status": False, "response": response}
