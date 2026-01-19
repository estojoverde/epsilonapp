from typing import List, Optional
from pydantic import BaseModel
from src.core.models import DeckIR, SlideIR, SlideType, ImageRef

class LayoutBox(BaseModel):
    kind: str # 'text' ou 'image'
    role: str
    x: float
    y: float
    w: float
    h: float
    font_size: int = 18
    text: Optional[str] = None
    image_ref: Optional[ImageRef] = None

class LayoutSlide(BaseModel):
    id: str
    boxes: List[LayoutBox]
    notes: Optional[str] = None

class LayoutDeck(BaseModel):
    slides: List[LayoutSlide]

def compute_layout(deck: DeckIR) -> LayoutDeck:
    layout_slides = []
    
    for s in deck.slides:
        boxes = []
        
        # Título sempre presente
        boxes.append(LayoutBox(kind="text", role="title", x=1, y=0.5, w=11.3, h=1, font_size=40, text=s.title))
        
        # Layout Híbrido (Texto + Imagem)
        if s.image and s.image.status == "ready" and s.image.local_path:
            content = s.caption or ("\n".join(s.bullets) if s.bullets else "")
            # Texto à Esquerda
            boxes.append(LayoutBox(kind="text", role="body", x=1.0, y=1.8, w=6.0, h=5.0, font_size=24, text=content))
            # Imagem à Direita
            boxes.append(LayoutBox(kind="image", role="hero", x=7.5, y=1.8, w=5.0, h=5.0, font_size=0, image_ref=s.image))
            
        # Layout Duas Colunas
        elif s.type == SlideType.TWO_COLUMNS and s.columns:
            boxes.append(LayoutBox(kind="text", role="body", x=1.0, y=1.8, w=5.5, h=5.0, font_size=24, text="\n".join(s.columns.left)))
            boxes.append(LayoutBox(kind="text", role="body", x=7.0, y=1.8, w=5.5, h=5.0, font_size=24, text="\n".join(s.columns.right)))
            
        # Layout Padrão (Bullets)
        else:
            content = "\n".join(s.bullets) if s.bullets else ""
            boxes.append(LayoutBox(kind="text", role="body", x=1.0, y=1.8, w=11.3, h=5.0, font_size=24, text=content))

        layout_slides.append(LayoutSlide(id=s.id, boxes=boxes, notes=s.notes))
        
    return LayoutDeck(slides=layout_slides)