import os
from pathlib import Path  
from deepgram import DeepgramClient, PrerecordedOptions    
from gailbot.engineManager.engine.engine import Engine
from .deepgramSetting import DeepgramSetting
from typing import Dict, List
from gailbot.shared.utils.logger import makelogger
import requests

logger = makelogger("deepgram engine")

class Deepgram(Engine):
    def __init__(self, setting: DeepgramSetting):
        self.setting = setting
        self.dg = DeepgramClient(self.setting.deepgram_api_key)
        self.transcribe_success = False

    def __repr__(self):
        return self.setting.engine

    def transcribe(self, audio_path: str, workspace: str):
        dg = DeepgramClient(self.setting.deepgram_api_key)

        with open(audio_path, "rb") as audio:
            source = {"buffer": audio, "mimetype": "audio/wav"} 
            options = PrerecordedOptions(
                model=self.setting.model,
                punctuate=self.setting.punctuate,
                diarize=self.setting.diarize,
                profanity_filter=self.setting.profanity_filter,
                language=self.setting.language,
            )

            response = dg.listen.rest.v("1").transcribe_file(source, options)  # sync


            ws_path = Path(workspace)
            ws_path.mkdir(parents=True, exist_ok=True)       
            out_json = ws_path / f"{Path(audio_path).stem}.deepgram.json"
            out_json.write_text(response.to_json(indent=2))

            utterances = [
                {
                    "start": w.start,
                    "end":   w.end,
                    "text":  w.word,
                    "speaker": w.speaker or "",
                }
                for ch in response.results.channels
                for alt in ch.alternatives
                for w   in alt.words
            ]

            self.transcribe_success = True
            return utterances

    def is_file_supported(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.wav', '.mp3', '.flac', '.m4a', '.ogg']

    def get_supported_formats(self) -> List[str]:
        return ['wav', 'mp3', 'flac', 'm4a', 'ogg']

    def get_engine_name(self) -> str:
        return self.setting.engine

    def was_transcription_successful(self) -> bool:
        return self.transcribe_success

    @staticmethod
    def is_valid_deepgram_api(api_key: str, timeout: float = 5.0) -> bool:
        """
        Validate a Deepgram API key by calling the /v1/auth/token endpoint.
        Returns True if the key is valid (HTTP 200), False otherwise.
        """
        url = "https://api.deepgram.com/v1/auth/token"
        headers = {"Authorization": f"Token {api_key}"}
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            return resp.status_code == 200
        except requests.RequestException:
            # Network error or timeout
            return False
