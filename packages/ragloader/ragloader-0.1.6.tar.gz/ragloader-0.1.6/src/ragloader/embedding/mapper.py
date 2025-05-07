from enum import Enum

from .embedders.paraphrase_multilingual_mpnet import ParaphraseMultilingualMpnet
from .embedders.all_mpnet_base import AllMpnetBase
from .embedders.openai_ada import OpenAIAda
from .embedders.legal_bert import LegalBertBaseUncased


class EmbeddingModelsMapper(Enum):
    """Mapper from embedding models' names and embedding models."""
    paraphrase_multilingual_mpnet = ParaphraseMultilingualMpnet
    all_mpnet_base = AllMpnetBase
    openai_ada = OpenAIAda
    legal_bert = LegalBertBaseUncased
