import json
import argparse


if __name__ == "__main__":
    # Unique point d'entrée: on appelle le modèle pour chaque post via process_with_ollama,
    # mais la logique d'analyse reste dans le fichier séparé.
    from process_with_ollama import process_tweets_with_ollama

    parser = argparse.ArgumentParser(description="Entrée unique: récupère des posts (mock) et appelle un modèle Ollama pour chaque post.")
    parser.add_argument("user_id", help="ID numérique Twitter ou handle (ex: 44196397 ou @elonmusk)")
    parser.add_argument("--limit", type=int, default=10, help="Nombre de posts à récupérer")
    parser.add_argument("--model", type=str, default="qwen3:4b", help="Modèle Ollama")
    parser.add_argument("--system", type=str, default=None, help="Instruction système optionnelle")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    args = parser.parse_args()

    # Toujours mocker la récupération (pas d'appels payants)
    results = process_tweets_with_ollama(args.user_id, args.limit, args.model, system_instruction=args.system, mock=True)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        sep = "\n" + ("=" * 80) + "\n"
        blocks = []
        for i, r in enumerate(results, start=1):
            header = f"[{i}] {r.get('created_at','')} (id: {r.get('id_str','')})"
            blocks.append(f"{header}\nPost:\n{r.get('full_text','')}\n\nAnalysis:\n{r.get('analysis','')}")
        print(sep.join(blocks))
