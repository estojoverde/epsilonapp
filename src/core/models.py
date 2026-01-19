from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SlideType(str, Enum):
    TITLE = "TITLE"
    TITLE_BULLETS = "TITLE_BULLETS"
    TWO_COLUMNS = "TWO_COLUMNS"
    IMAGE_CAPTION = "IMAGE_CAPTION"
    SECTION = "SECTION"

class AudienceType(str, Enum):
    EXECUTIVE = "executivo"
    TECHNICAL = "técnico"
    MIXED = "misto"
    BEGINNER = "iniciante"

class ImageRef(BaseModel):
    """Referência para ativos de imagem, incluindo status e caminho local."""
    status: str = Field(..., description="'missing', 'generating', 'ready', 'error'")
    prompt: Optional[str] = None
    uri: Optional[str] = None
    local_path: Optional[str] = None
    aspect_ratio: str = "16:9"

class TwoColumnsData(BaseModel):
    left: List[str] = []
    right: List[str] = []

class SlideIR(BaseModel):
    """Representação Intermediária (IR) de um único slide."""
    id: str
    type: SlideType
    title: str = ""
    subtitle: Optional[str] = None
    bullets: Optional[List[str]] = Field(default_factory=list)
    columns: Optional[TwoColumnsData] = None
    image: Optional[ImageRef] = None
    caption: Optional[str] = None
    notes: Optional[str] = None

class DeckMeta(BaseModel):
    title: str
    language: str = "pt-BR"
    audience: AudienceType = AudienceType.MIXED
    theme_id: str = "default"

class DeckIR(BaseModel):
    """Representação completa da apresentação."""
    meta: DeckMeta
    slides: List[SlideIR]

class Constraints(BaseModel):
    max_bullets: int = 6
    max_words_bullet: int = 12
    max_title_words: int = 8

class ContextPack(BaseModel):
    """Pacote de contexto para ingestão e processamento."""
    prompt: str
    source_text: str
    cleaned_text: Optional[str] = None
    constraints: Constraints = Field(default_factory=Constraints)
    meta: Dict[str, Any] = {}