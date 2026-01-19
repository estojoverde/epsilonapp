import os
import re
import traceback
from src.core.models import ImageRef, ContextPack
from src.core.utils import sanitize_text
from src.agents.manager import SlideCrewManager
from src.services.image_gen import ImageGeneratorService
from src.engine.layout import compute_layout
from src.engine.renderer import render_pptx

def run_pipeline(prompt: str, context_text: str, output_file: str, groq_key: str, hf_token: str = None):
    print(f"🌟 Iniciando Pipeline Debug: '{prompt}'")
    
    match = re.search(r'(\d+)\s+slides', prompt.lower())
    num_slides = int(match.group(1)) if match else 5
    print(f"   🔢 Alvo Detectado: {num_slides} slides.")

    ctx = ContextPack(
        prompt=prompt, 
        source_text=context_text, 
        cleaned_text=sanitize_text(context_text)
    )
    ctx.meta['num_slides'] = num_slides

    # 1. CrewAI
    try:
        print("\n🤖 1. Gerando Conteúdo Textual...")
        manager = SlideCrewManager(api_key=groq_key)
        deck = manager.run_crew(ctx)
    except Exception as e:
        print(f"\n❌ [FATAL] Erro no CrewAI ou Parsing:")
        print(f"   Mensagem: {e}")
        print("-" * 30)
        traceback.print_exc()
        print("-" * 30)
        return None

    # 2. Imagens
    print("\n🖼️ 2. Gerando Imagens Contextuais...")
    try:
        img_gen = ImageGeneratorService(hf_token=hf_token)
        for i, s in enumerate(deck.slides):
            if not s.image: s.image = ImageRef(status="missing")
            
            if not s.image.prompt:
                # Fallback seguro se não houver bullets
                context_preview = ". ".join(s.bullets[:2]) if s.bullets else s.title
                s.image.prompt = (
                    f"Professional illustration, cinematic lighting, 8k. "
                    f"Subject: {s.title}. Context: {context_preview}. "
                    f"Style: Futuristic Minimalism."
                )
            
            if s.image.status != "ready":
                print(f"   🎨 Processando Slide {i+1}...")
                path = img_gen.generate(s.image.prompt, s.id)
                s.image.local_path = path
                s.image.status = "ready"
    except Exception as e:
        print(f"⚠️ Erro não-fatal nas imagens: {e}")
        traceback.print_exc()

    # 3. Render
    print("\n🎨 3. Renderizando...")
    try:
        layout = compute_layout(deck)
        final_path = render_pptx(layout, output_file)
        print(f"🏆 Concluído: {os.path.abspath(final_path)}")
        return final_path
    except Exception as e:
        print(f"❌ [FATAL] Erro no Renderizador:")
        traceback.print_exc()
        return None