from .json_model_decoder import JSONModelDecoder
from .json_model_encoder import JSONModelEncoder, collect_data
from .types import JSONClassWrapper, JSONModelDict

dumps = JSONModelEncoder().encode
loads = JSONModelDecoder().decode
