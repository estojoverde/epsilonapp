import os
from pathlib import Path

class ImageValidatorService:
    def __init__(self):
        # Aqui você poderia inicializar um cliente Groq para visão no futuro
        # self.vision_client = ...
        pass

    def validate(self, image_path: str, context_prompt: str) -> bool:
        """
        Valida se a imagem gerada é aceitável.
        
        Args:
            image_path: Caminho local do arquivo de imagem.
            context_prompt: O prompt que gerou a imagem (para validação semântica futura).
            
        Returns:
            bool: True se a imagem passou no teste, False caso contrário.
        """
        # 1. Validação Física (Básica)
        if not image_path:
            print("      ❌ Caminho da imagem vazio.")
            return False
            
        path = Path(image_path)
        
        if not path.exists():
            print(f"      ❌ Arquivo não encontrado: {image_path}")
            return False
            
        # Verifica se o arquivo tem tamanho > 1KB (evita arquivos corrompidos/vazios)
        if path.stat().st_size < 1024:
            print(f"      ❌ Imagem muito pequena ou corrompida ({path.stat().st_size} bytes).")
            return False

        # 2. Validação Semântica (Futuro / Placeholder)
        # Aqui entra a lógica de "Vision AI":
        # - Enviar a imagem para o Llama 3.2 Vision
        # - Perguntar: "Esta imagem representa bem o conceito '{context_prompt}'?"
        # - Se a resposta for "Não", retornar False para forçar regeneração.
        
        # Por enquanto, assumimos que se o arquivo existe, está válido.
        return True