import os
import argparse
from dotenv import load_dotenv
from src.pipeline import run_pipeline

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="SlideGen CLI - Gerador de Apresentações com IA")
    parser.add_argument("--prompt", required=True, help="O tema ou instrução da apresentação")
    parser.add_argument("--context", required=False, default="", help="Texto de base ou contexto")
    parser.add_argument("--output", default="output.pptx", help="Nome do arquivo de saída")
    
    args = parser.parse_args()
    
    groq_key = os.getenv("GROQ_API_KEY")
    hf_token = os.getenv("HF_TOKEN")
    
    if not groq_key:
        print("❌ Erro: GROQ_API_KEY não encontrada no .env")
        return

    run_pipeline(args.prompt, args.context, args.output, groq_key, hf_token)

if __name__ == "__main__":
    main()