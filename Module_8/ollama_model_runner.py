import argparse
import json
from pathlib import Path
from typing import List

import requests


def parse_models(models_arg: str) -> List[str]:
    return [m.strip() for m in models_arg.split(",") if m.strip()]


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        p = Path(args.prompt_file)
        if not p.exists():
            raise FileNotFoundError(f"Prompt file not found: {p}")
        return p.read_text(encoding="utf-8")
    if args.prompt:
        return args.prompt
    raise ValueError("Provide --prompt or --prompt-file")


def call_ollama(host: str, model: str, prompt: str, temperature: float, max_tokens: int) -> dict:
    url = f"{host.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }
    resp = requests.post(url, json=payload, timeout=240)
    resp.raise_for_status()
    data = resp.json()
    return {
        "model": model,
        "response": data.get("response", "").strip(),
        "done": data.get("done", False),
        "total_duration": data.get("total_duration"),
        "eval_count": data.get("eval_count"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Call one or many Ollama models with a prepared prompt.")
    parser.add_argument("--host", default="http://localhost:11434")
    parser.add_argument("--models", required=True, help="Comma-separated models, e.g. llama3.1:8b,mistral:7b")
    parser.add_argument("--prompt", default="", help="Direct prompt text")
    parser.add_argument("--prompt-file", default="", help="Path to UTF-8 text file containing prompt")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=320)
    args = parser.parse_args()

    models = parse_models(args.models)
    if not models:
        raise ValueError("No valid model provided.")

    prompt = read_prompt(args)

    outputs = []
    for model in models:
        try:
            out = call_ollama(args.host, model, prompt, args.temperature, args.max_tokens)
            out["status"] = "ok"
            outputs.append(out)
        except Exception as e:
            outputs.append({"model": model, "status": f"error: {e}", "response": ""})

    print(
        json.dumps(
            {
                "host": args.host,
                "models": models,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "prompt_chars": len(prompt),
                "outputs": outputs,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
