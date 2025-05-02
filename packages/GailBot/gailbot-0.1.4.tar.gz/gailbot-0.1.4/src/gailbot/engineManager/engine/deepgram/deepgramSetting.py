from pydantic import BaseModel
from typing import List
from gailbot.setting_interface.formItem import FormItem, FormType

class DeepgramSetting(BaseModel):
    engine: str = "deepgram"
    deepgram_api_key: str
    language: str = "en-US"
    punctuate: bool = True
    diarize: bool = False
    profanity_filter: bool = False
    model: str = "general"
    tier: str = "standard"

    @staticmethod
    def get_setting_config() -> List[FormItem]:
        return [
            FormItem(type=FormType.Selection, name="engine", selection_items=["deepgram"], default_value="deepgram"),
            FormItem(type=FormType.Text, name="deepgram_api_key"),
            FormItem(type=FormType.Selection, name="language", selection_items=["en-US", "es-ES", "fr-FR", "de-DE"], default_value="en-US"),
            FormItem(type=FormType.OnOff, name="punctuate", default_value=True),
            FormItem(type=FormType.OnOff, name="diarize", default_value=False),
            FormItem(type=FormType.OnOff, name="profanity_filter", default_value=False),
            FormItem(type=FormType.Selection, name="model", selection_items=[
                "nova-3",
                "nova-3-general",
                "nova-3-medical",
                "nova-2",
                "nova-2-general",
                "nova-2-meeting",
                "nova-2-phonecall",
                "nova-2-voicemail",
                "nova-2-finance",
                "nova-2-conversationalai",
                "nova-2-video",
                "nova-2-medical",
                "nova-2-drivethru",
                "nova-2-automotive",
                "enhanced-general",
                "base-general"
            ], default_value="base-general"),
        ]