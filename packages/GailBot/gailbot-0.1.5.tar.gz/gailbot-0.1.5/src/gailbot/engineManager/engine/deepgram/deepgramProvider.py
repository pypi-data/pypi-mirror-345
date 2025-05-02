import os
from typing import Dict, Optional
from gailbot.engineManager.engine.engine import Engine
from gailbot.engineManager.engine.engineProvider import EngineProvider
from .deepgram import Deepgram
from .deepgramSetting import DeepgramSetting
from gailbot.shared.utils.general import make_dir, copy
from gailbot.shared.utils.logger import makelogger
from gailbot.workspace import WorkspaceManager

logger = makelogger("deepgram provider")

class DeepgramProvider(EngineProvider):
    workspace = os.path.join(WorkspaceManager.engine_src, "deepgram/api")

    def is_cpu_intensive(self) -> bool:
        return False

    @staticmethod
    def load(name: str, data: Dict[str, str]) -> Optional['DeepgramProvider']:
        try:
            prov = DeepgramProvider(name, data)
            assert prov.data.engine.lower() == "deepgram"
            return prov
        except Exception as e:
            logger.warning(e)
            return None

    def __init__(self, name: str, data: Dict[str, str]):
        if not os.path.isdir(self.workspace):
            make_dir(self.workspace)
        self.name = name
        self.data: DeepgramSetting = DeepgramSetting(**data)
        assert Deepgram.is_valid_deepgram_api(self.data.deepgram_api_key)

    def make_engine(self) -> Engine:
        return Deepgram(self.data)
