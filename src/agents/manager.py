import os
import json
import traceback
from pathlib import Path
from crewai import Agent, Task, Crew, Process, LLM
from src.core.models import DeckIR, ContextPack

class SlideCrewManager:
    def __init__(self, api_key: str):
        self.llm = LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=0.0
        )
        self.prompts_dir = Path(__file__).parent / "prompts"

    def _load_prompt(self, filename: str, **kwargs) -> str:
        try:
            with open(self.prompts_dir / filename, "r", encoding="utf-8") as f:
                content = f.read()
            return content.format(**kwargs)
        except Exception as e:
            print(f"⚠️ Erro ao carregar prompt {filename}: {e}")
            return ""

    def _heal_json_structure(self, data: dict) -> dict:
        """
        Tenta consertar JSONs mal formados pelo LLM.
        Cenário comum: O LLM retorna um dict de slides em vez de {meta:..., slides:[...]}
        """
        # Se já estiver correto, retorna
        if "meta" in data and "slides" in data:
            return data

        print("   🚑 [AUTO-HEALING] Detectada estrutura incorreta. Tentando consertar...")
        
        new_data = {
            "meta": {
                "title": "Apresentação Gerada",
                "audience": "misto",
                "theme_id": "default"
            },
            "slides": []
        }

        # Tenta iterar sobre as chaves para achar os slides
        # Ex: {"Slide 1": {...}, "Slide 2": {...}}
        for key, value in data.items():
            if isinstance(value, dict):
                # Tenta extrair título e bullets
                title = key
                # Se o value tiver 'título' ou 'title', usa
                if "title" in value: title = value["title"]
                elif "Título" in value: title = value["Título"]
                
                # Tenta achar os bullets/conteúdo
                bullets = []
                for k, v in value.items():
                    if isinstance(v, list): # Geralmente os bullets são a única lista
                        bullets = [str(item) for item in v]
                        break
                    elif k.lower() in ["texto", "text", "conteudo", "content"]:
                        bullets = [str(v)]
                
                # Se não achou bullets, usa os valores do dict como texto
                if not bullets:
                    bullets = [f"{k}: {v}" for k,v in value.items() if isinstance(v, (str, int, float))]

                new_data["slides"].append({
                    "id": f"s_{len(new_data['slides'])+1}",
                    "type": "TITLE_BULLETS",
                    "title": title,
                    "bullets": bullets,
                    "image": {"status": "missing"}
                })
        
        print(f"   🚑 Recuperados {len(new_data['slides'])} slides da estrutura quebrada.")
        return new_data

    def run_crew(self, context: ContextPack) -> DeckIR:
        # Agentes (Definição igual)
        strategist = Agent(role='Planejador', goal='Estrutura.', backstory="Estrategista.", llm=self.llm, allow_delegation=False)
        writer = Agent(role='Redator', goal='Conteúdo denso.', backstory="Escritor técnico.", llm=self.llm, allow_delegation=False)
        formatter = Agent(role='Formatador', goal='JSON.', backstory="Dev.", llm=self.llm, allow_delegation=False)
        reviewer = Agent(role='Editor Visual', goal='Concisão.', backstory="Editor.", llm=self.llm, allow_delegation=False)

        num_slides = context.meta.get('num_slides', 5)
        clean_source = context.cleaned_text[:2000]

        # Tasks
        plan_task = Task(description=self._load_prompt("strategist.md", num_slides=num_slides, user_prompt=context.prompt, source_text=clean_source), expected_output="Lista.", agent=strategist)
        write_task = Task(description=self._load_prompt("writer.md", num_slides=num_slides), expected_output="Texto.", agent=writer, context=[plan_task])
        review_task = Task(description=self._load_prompt("reviewer.md", num_slides=num_slides), expected_output="Texto revisado.", agent=reviewer, context=[write_task])
        format_task = Task(description=self._load_prompt("formatter.md"), expected_output="JSON.", agent=formatter, context=[review_task])

        crew = Crew(agents=[strategist, writer, reviewer, formatter], tasks=[plan_task, write_task, review_task, format_task], verbose=True)
        result = crew.kickoff()
        
        try:
            if hasattr(result, 'raw'): json_str = result.raw
            else: json_str = str(result)
            
            # Limpeza básica
            json_str = json_str.replace("```json", "").replace("```", "").strip()
            start = json_str.find("{"); end = json_str.rfind("}")
            if start != -1 and end != -1: json_str = json_str[start:end+1]
            
            raw_data = json.loads(json_str)
            
            # --- AQUI ENTRA A CURA ---
            healed_data = self._heal_json_structure(raw_data)
            
            return DeckIR(**healed_data)

        except Exception as e:
            print(f"❌ [ERRO MANAGER]: {e}")
            # Se falhar muito feio, retorna um deck vazio para não crashar o pipeline inteiro
            # return DeckIR(meta={"title": "Error", "audience": "misto", "theme_id": "default"}, slides=[])
            raise e