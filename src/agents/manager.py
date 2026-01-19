import os
import json
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
        with open(self.prompts_dir / filename, "r", encoding="utf-8") as f:
            content = f.read()
        return content.format(**kwargs)

    def run_crew(self, context: ContextPack) -> DeckIR:
        # Agentes
        strategist = Agent(role='Planejador', goal='Estrutura.', backstory="Estrategista.", llm=self.llm, allow_delegation=False)
        writer = Agent(role='Redator', goal='Conteúdo denso.', backstory="Escritor técnico.", llm=self.llm, allow_delegation=False)
        formatter = Agent(role='Formatador', goal='JSON.', backstory="Dev.", llm=self.llm, allow_delegation=False)
        reviewer = Agent(
            role='Editor Visual', 
            goal='Garantir que o texto caiba no design e seja impactante.', 
            backstory="Ex-Diretor de Arte. Odeia slides com muito texto (Wall of Text).",
            llm=self.llm,
            allow_delegation=False
        )

        num_slides = context.meta.get('num_slides', 5)
        clean_source = context.cleaned_text[:2000] # Limite de contexto

        # Tasks com Prompts Externos
        plan_task = Task(
            description=self._load_prompt("strategist.md", num_slides=num_slides, user_prompt=context.prompt, source_text=clean_source),
            expected_output="Lista de tópicos itemizada.", 
            agent=strategist
        )
        
        write_task = Task(
            description=self._load_prompt("writer.md", num_slides=num_slides),
            expected_output="Texto completo dos slides.", 
            agent=writer, 
            context=[plan_task]
        )
        
        review_task = Task(
            description=self._load_prompt("reviewer.md", num_slides=context.meta.get('num_slides', 5)),
            expected_output="Texto refinado e conciso.", 
            agent=reviewer, 
            context=[write_task] # Recebe do Writer
        )
        
        # format_task = Task(
        #     description=self._load_prompt("formatter.md"),
        #     expected_output="JSON válido.", 
        #     agent=formatter, 
        #     context=[write_task]
        # )
        format_task = Task(
            description=self._load_prompt("formatter.md"),
            expected_output="JSON válido.", 
            agent=formatter, 
            context=[review_task] 
        )

        #crew = Crew(agents=[strategist, writer, formatter], tasks=[plan_task, write_task, format_task], verbose=True)
        crew = Crew(
            agents=[strategist, writer, reviewer, formatter], # Adicionar reviewer
            tasks=[plan_task, write_task, review_task, format_task], # Adicionar review_task
            verbose=True
        )
        result = crew.kickoff()
        
        # Parsing Seguro
        try:
            json_str = str(result).replace("```json", "").replace("```", "").strip()
            data = json.loads(json_str)
            # Garantir IDs únicos se o LLM falhar
            for i, slide in enumerate(data.get("slides", [])):
                if not slide.get("id"): slide["id"] = f"s{i+1}"
            return DeckIR(**data)
        except Exception as e:
            print(f"❌ Erro ao parsear JSON: {e}")
            raise e