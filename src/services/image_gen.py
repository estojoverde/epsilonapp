import time
import textwrap
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

class ImageGeneratorService:
    def __init__(self, hf_token: Optional[str] = None, output_dir: str = "output/assets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.hf_client = None
        
        if hf_token and InferenceClient:
            try:
                self.hf_client = InferenceClient(token=hf_token)
                print("   🎨 Serviço de IA Generativa (HuggingFace) ATIVO.")
            except Exception as e:
                print(f"   ⚠️ Erro ao iniciar cliente HF: {e}. Usando Fallback.")
        else:
            print("   🎨 Modo Fallback (Imagens Sintéticas) ATIVO.")

    def generate(self, prompt: str, slide_id: str) -> str:
        filename = self.output_dir / f"{slide_id}_{int(time.time())}.png"
        safe_prompt = prompt if prompt else f"Slide {slide_id}"
        
        # 1. Tenta HuggingFace
        if self.hf_client:
            try:
                print(f"   🖌️ Gerando via Flux.1: '{safe_prompt[:40]}...'")
                image = self.hf_client.text_to_image(safe_prompt, model="black-forest-labs/FLUX.1-schnell")
                image.save(filename)
                return str(filename)
            except Exception as e:
                print(f"   ⚠️ Erro na API HF: {e}. Mudando para fallback local.")
                self.hf_client = None 

        # 2. Fallback Local (Pillow)
        img = Image.new('RGB', (1280, 720), color=(50, 50, 80))
        d = ImageDraw.Draw(img)
        d.text((50, 300), f"ID: {slide_id}", fill=(255, 200, 0))
        wrapped = textwrap.fill(safe_prompt, width=60)
        d.text((50, 400), wrapped, fill=(255, 255, 255))
        
        img.save(filename)
        return str(filename)