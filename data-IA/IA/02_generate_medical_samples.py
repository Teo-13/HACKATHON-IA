"""
Generation de reponses avec un modele de base ou un adapter LoRA medical.

Exemple :
    python 02_generate_medical_samples.py ^
      --model-name Qwen/Qwen2.5-3B-Instruct ^
      --adapter-path runs/qwen25-medical-lora
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _missing_dependency(message: str) -> None:
    raise SystemExit(
        message
        + "\nInstallez d'abord : pip install transformers peft accelerate bitsandbytes"
    )


try:
    import torch
except ImportError as exc:  # pragma: no cover - depends on local env
    _missing_dependency(str(exc))

try:
    from peft import PeftModel
except ImportError as exc:  # pragma: no cover - depends on local env
    _missing_dependency(str(exc))

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError as exc:  # pragma: no cover - depends on local env
    _missing_dependency(str(exc))


DEFAULT_PROMPTS = [
    "I feel exhausted all the time and I have lost interest in the activities I used to enjoy. What should I do?",
    "I have had a sore throat and fever for three days. When should I see a doctor?",
    "I am anxious about chest pain that gets worse when I move. What are the next safe steps?",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="Qwen/Qwen2.5-3B-Instruct")
    parser.add_argument("--adapter-path", type=Path)
    parser.add_argument("--prompt-file", type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    return parser.parse_args()


def build_prompt(question: str) -> str:
    return (
        "### Instruction\n"
        "Tu es un assistant medical. Reponds a la question du patient.\n\n"
        "### Question patient\n"
        f"{question.strip()}\n\n"
        "### Reponse medicale\n"
    )


def load_prompts(path: Path | None) -> list[str]:
    if path is None:
        return DEFAULT_PROMPTS

    if path.suffix.lower() == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Le fichier JSON de prompts doit contenir une liste.")
        return [str(item) for item in data]

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main() -> None:
    args = parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )

    if args.adapter_path:
        model = PeftModel.from_pretrained(model, str(args.adapter_path))

    prompts = load_prompts(args.prompt_file)

    for index, prompt in enumerate(prompts, start=1):
        rendered = build_prompt(prompt)
        inputs = tokenizer(rendered, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=True,
                temperature=args.temperature,
                top_p=args.top_p,
                pad_token_id=tokenizer.eos_token_id,
            )

        generated = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        answer = generated.split("### Reponse medicale", 1)[-1].strip()

        print(f"\n--- Sample {index} ---")
        print(f"Question: {prompt}")
        print(f"Reponse : {answer}")


if __name__ == "__main__":
    main()
