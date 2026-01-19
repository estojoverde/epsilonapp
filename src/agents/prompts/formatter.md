Converta o texto fornecido em um JSON estrito seguindo o schema DeckIR.
Gere uma entrada na lista 'slides' para CADA slide encontrado no texto.

Schema Obrigatório:
{
  "meta": { ... },
  "slides": [
    {
      "id": "s1",
      "type": "TITLE_BULLETS", # ou TITLE, TWO_COLUMNS, IMAGE_CAPTION
      "title": "...",
      "bullets": ["..."],
      "image": { "status": "missing" } # Se necessário
    }
  ]
}
Retorne APENAS o JSON cru, sem markdown.