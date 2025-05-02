# -*- coding: utf-8 -*-
# @Author: Vivian Li
# @Date:   2024-04-09 17:02:48
# @Last Modified by:   Vivian Li
# @Last Modified time: 2024-04-24 19:08:53
from typing import List
from pydantic import BaseModel

from gailbot.configs import whisper_config_loader
from gailbot.setting_interface.formItem import FormItem, FormType


class WhisperSetting(BaseModel):
    engine: str
    language: str
    detect_speakers: bool = False

    @staticmethod
    def predefined_config():
        config = whisper_config_loader()
        return config

    @staticmethod
    def get_setting_config() -> List[FormItem]:
        return [
            FormItem(type=FormType.OnOff, name="detect_speakers", default_value= False),
            FormItem(type=FormType.Selection, name="language", selection_items=["af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs", 
            "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu", 
            "ha", "haw", "he", "hi", "hr", "hu", "hy", "id", "is", "it", "ja", "jw", "ka", 
            "kk", "km", "kn", "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", 
            "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "no", "nn", "oc", "pa", "pl", 
            "ps", "pt", "ro", "ru", "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", 
            "sv", "sw", "ta", "te", "tg", "th", "tl", "tr", "tt", "uk", "ur", "uz", "vi", 
            "yi", "yo", "yue", "zh"], default_value= "en"),
        ]  # TODO: get the list of selectable language
