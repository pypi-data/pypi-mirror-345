import toml
import logging
from pathlib import Path
from pydantic import BaseModel, ValidationError

from ragloader.exceptions import InvalidConfigPath, InvalidConfigStructure


class GeneralConfig(BaseModel):
    log_level: str


class ParsingConfig(BaseModel):
    label: str
    cache_step: bool
    use_cache: bool
    parsers: dict[str, str]


class ClassificationConfig(BaseModel):
    label: str
    cache_step: bool
    use_cache: bool
    categories: dict[str, list[str]]


class ExtractionConfig(BaseModel):
    label: str
    cache_step: bool
    use_cache: bool


class SplittingParams(BaseModel):
    chunk_size: int
    chunk_overlap: int


class SplittingConfig(BaseModel):
    label: str
    cache_step: bool
    use_cache: bool
    splitters: dict[str, str]
    splitters_params: dict[str, SplittingParams]


class EmbeddingConfig(BaseModel):
    label: str
    cache_step: bool
    use_cache: bool
    embedding_model: str


class QdrantConfig(BaseModel):
    location: str
    port: int


class DBConfig(BaseModel):
    qdrant: QdrantConfig


class PipelineStagesConfig(BaseModel):
    parsing: ParsingConfig
    classification: ClassificationConfig
    extraction: ExtractionConfig
    splitting: SplittingConfig
    embedding: EmbeddingConfig


class ConfigModel(BaseModel):
    general: GeneralConfig
    pipeline_stages: PipelineStagesConfig
    db: DBConfig


class Config(dict):
    def __init__(self, config_path: Path | str = Path("ragloader/conf/config.toml")):
        try:
            with open(config_path, "r") as f:
                config = toml.load(f)
        except FileNotFoundError:
            raise InvalidConfigPath(f"Invalid path: {config_path}")

        try:
            config_model = ConfigModel(**config)
            super().__init__(config_model.model_dump())
        except ValidationError as e:
            raise InvalidConfigStructure(f"Invalid config structure: {e}")


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': "\033[90m",
        'INFO': "\033[94m",
        'WARNING': "\033[38;5;214m",
        'ERROR': "\033[91m",
        'CRITICAL': "\033[38;5;88m",
        'RESET': "\033[0m"
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        message = super().format(record)
        return f"{log_color}{message}{self.COLORS['RESET']}"


def get_logger(config: Config):
    log_level = config["general"]["log_level"].upper()
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(f"Invalid log level: {log_level}")

    logger = logging.getLogger("logger")
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(module)s:\t %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
