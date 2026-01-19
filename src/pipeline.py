import os
import re
from src.core.models import ImageRef
from src.core.utils import sanitize_text
from src.core.models import ContextPack
from src.agents.manager import SlideCrewManager
from src.services.image_gen import ImageGeneratorService
from src.engine.layout import compute_layout
from src.engine.renderer import render_pptx
from src.services.image_val import ImageValidatorService
from src.engine.qa import editorial_qa_simulation, apply_tickets_simulation # Importar do novo módulo


def run_pipeline(prompt: str, context_text: str, output_file: str, groq_key: str, hf_token: str = None):
    print(f"🌟 Iniciando Pipeline: '{prompt}'")
    
    # 1. Detectar Quantidade de Slides
    match = re.search(r'(\d+)\s+slides', prompt.lower())
    num_slides = int(match.group(1)) if match else 5
    print(f"   🔢 Alvo Detectado: {num_slides} slides.")

    # 2. Setup Contexto
    ctx = ContextPack(
        prompt=prompt, 
        source_text=context_text, 
        cleaned_text=sanitize_text(context_text)
    )
    ctx.meta['num_slides'] = num_slides

    # 3. Geração de Conteúdo (CrewAI)
    try:
        print("\n🤖 1. Gerando Conteúdo Textual...")
        manager = SlideCrewManager(api_key=groq_key)
        deck = manager.run_crew(ctx)
    except Exception as e:
        print(f"❌ Erro Crítico no CrewAI: {e}")
        return None

    print("\n🔍 Auditando qualidade dos slides...")
    qa_result = editorial_qa_simulation(deck)
    if not qa_result.scorecard.passed:
        print(f"   ⚠️ Problemas detectados: {[t.issue_code for t in qa_result.tickets]}")
        print("   🔧 Aplicando correções automáticas...")
        deck = apply_tickets_simulation(deck, qa_result.tickets)
    else:
        print("   ✅ Conteúdo aprovado na auditoria.")

    # 4. Geração de Imagens (Smart Context)
    print("\n🖼️ 2. Gerando Imagens Contextuais...")
    img_gen = ImageGeneratorService(hf_token=hf_token)
    validator = ImageValidatorService()
    
    for s in deck.slides:
        if not s.image: s.image = ImageRef(status="missing")
        
        # Cria prompt dinâmico se não existir
        if not s.image.prompt:
            context_preview = ". ".join(s.bullets[:2]) if s.bullets else s.title
            s.image.prompt = (
                f"Professional illustration, cinematic lighting, 8k. "
                f"Subject: {s.title}. Context: {context_preview}. "
                f"Style: Futuristic Minimalism."
            )
        
        
        
        # Gera
        if s.image.status != "ready":
            path = img_gen.generate(s.image.prompt, s.id)
            
            
            # Usa o validador
            if validator.validate(path, s.image.prompt):
                s.image.local_path = path
                s.image.status = "ready"
                print(f"      ✅ Imagem: {s.id}")
            else:
                print(f"      ⚠️ Imagem reprovida pelo validador.")
                
            s.image.local_path = path
            s.image.status = "ready"
            print(f"      ✅ Imagem: {s.id}")

    # 5. Renderização
    print("\n🎨 3. Renderizando...")
    layout = compute_layout(deck)
    final_path = render_pptx(layout, output_file)
    
    print(f"🏆 Concluído: {os.path.abspath(final_path)}")
    return final_path