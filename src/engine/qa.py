from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field
from src.core.models import DeckIR

# --- Modelos de QA ---
class TicketTarget(BaseModel):
    slide_id: Optional[str] = None

class FeedbackTicket(BaseModel):
    issue_code: str # Ex: 'NARRATIVE_GAP', 'WEAK_TITLES'
    target: TicketTarget
    suggested_fix: str

class Scorecard(BaseModel):
    passed: bool
    tickets: List[FeedbackTicket] = []

class EvaluationEnvelope(BaseModel):
    scorecard: Scorecard
    tickets: List[FeedbackTicket]

# --- Lógica de Auditoria (Simulada) ---
def editorial_qa_simulation(deck: DeckIR) -> EvaluationEnvelope:
    tickets = []
    
    # Regra 1: Deck muito curto
    if len(deck.slides) < 2:
        tickets.append(FeedbackTicket(
            issue_code="NARRATIVE_GAP",
            target=TicketTarget(),
            suggested_fix="Adicionar mais slides de conteúdo."
        ))

    # Regra 2: Títulos muito longos ou texto excessivo
    for s in deck.slides:
        # Verifica tamanho do título
        if len(s.title.split()) > 12:
            tickets.append(FeedbackTicket(
                issue_code="WEAK_TITLE",
                target=TicketTarget(slide_id=s.id),
                suggested_fix="Encurtar título."
            ))
            
    passed = (len(tickets) == 0)
    return EvaluationEnvelope(
        scorecard=Scorecard(passed=passed, tickets=tickets),
        tickets=tickets
    )

def apply_tickets_simulation(deck: DeckIR, tickets: List[FeedbackTicket]) -> DeckIR:
    """Aplica correções simples baseadas nos tickets."""
    import copy
    new_deck = copy.deepcopy(deck)
    
    for ticket in tickets:
        if ticket.issue_code == "WEAK_TITLE" and ticket.target.slide_id:
            for s in new_deck.slides:
                if s.id == ticket.target.slide_id:
                    # Correção heurística simples: corta o título
                    words = s.title.split()
                    s.title = " ".join(words[:8]) + "..."
                    
    return new_deck