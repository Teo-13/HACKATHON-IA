"""
Fine-tuning LoRA du dataset medical TechCorp.

Ce script sert de point de depart reproductible pour la partie IA du brief.
Il entraine un adapter LoRA sur les fichiers JSONL deja prepares par la
pipeline data.

Exemple :
    python 01_finetune_lora_medical.py ^
      --model-name Qwen/Qwen2.5-3B-Instruct ^
      --output-dir runs/qwen25-medical-lora
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _missing_dependency(message: str) -> None:
    raise SystemExit(
        message
        + "\nInstallez d'abord : pip install transformers datasets peft trl accelerate bitsandbytes"
    )


try:
    import torch
except ImportError as exc:  # pragma: no cover - depends on local env
    _missing_dependency(str(exc))

try:
    from datasets import Dataset
except ImportError as exc:  # pragma: no cover - depends on local env
    _missing_dependency(str(exc))

try:
    from peft import LoraConfig
except ImportError as exc:  # pragma: no cover - depends on local env
    _missing_dependency(str(exc))

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
    )
except ImportError as exc:  # pragma: no cover - depends on local env
    _missing_dependency(str(exc))

try:
    from trl import SFTConfig, SFTTrainer
except ImportError as exc:  # pragma: no cover - depends on local env
    _missing_dependency(str(exc))


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TRAIN = BASE_DIR.parent / "data" / "dataset" / "export_lora" / "train_lora.jsonl"
DEFAULT_EVAL = BASE_DIR.parent / "data" / "dataset" / "export_lora" / "validation_lora.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="Qwen/Qwen2.5-3B-Instruct")
    parser.add_argument("--train-file", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument("--eval-file", type=Path, default=DEFAULT_EVAL)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--num-train-epochs", type=float, default=1.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--per-device-train-batch-size", type=int, default=2)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=2)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--warmup-ratio", type=float, default=0.03)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--logging-steps", type=int, default=20)
    parser.add_argument("--save-steps", type=int, default=200)
    parser.add_argument("--eval-steps", type=int, default=200)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-4bit", action="store_true")
    parser.add_argument("--max-train-samples", type=int)
    parser.add_argument("--max-eval-samples", type=int)
    parser.add_argument("--packing", action="store_true")
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def build_prompt(row: dict) -> str:
    instruction = row.get("instruction", "").strip()
    patient = row.get("input", "").strip()
    answer = row.get("output", "").strip()
    return (
        "### Instruction\n"
        f"{instruction}\n\n"
        "### Question patient\n"
        f"{patient}\n\n"
        "### Reponse medicale\n"
        f"{answer}"
    )


def build_dataset(path: Path, max_samples: int | None = None) -> Dataset:
    rows = load_jsonl(path)
    if max_samples is not None:
        rows = rows[:max_samples]
    formatted = [{"text": build_prompt(row)} for row in rows]
    return Dataset.from_list(formatted)


def detect_target_modules(model: torch.nn.Module) -> list[str]:
    wanted = {
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
        "qkv_proj",
        "dense",
        "fc1",
        "fc2",
        "c_attn",
        "c_proj",
        "c_fc",
    }
    found = set()

    for name, _module in model.named_modules():
        suffix = name.split(".")[-1]
        if suffix in wanted:
            found.add(suffix)

    if not found:
        raise RuntimeError(
            "Impossible de detecter automatiquement les modules LoRA. "
            "Verifiez l architecture du modele choisi."
        )

    ordered = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
        "qkv_proj",
        "dense",
        "fc1",
        "fc2",
        "c_attn",
        "c_proj",
        "c_fc",
    ]
    return [name for name in ordered if name in found]


def load_model_and_tokenizer(model_name: str, use_4bit: bool):
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs = {
        "trust_remote_code": True,
        "device_map": "auto" if torch.cuda.is_available() else None,
    }

    if use_4bit:
        try:
            from transformers import BitsAndBytesConfig
        except ImportError as exc:
            raise RuntimeError(
                "Le mode 4-bit demande bitsandbytes/transformers avec support adequat. "
                "Relancez avec --no-4bit sur CPU ou environnement non compatible."
            ) from exc

        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
        )
        model_kwargs["quantization_config"] = quantization_config
        model_kwargs["torch_dtype"] = torch.float16

    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
    model.config.use_cache = False
    return model, tokenizer


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    use_4bit = (not args.no_4bit) and torch.cuda.is_available()
    if not torch.cuda.is_available() and not args.no_4bit:
        print("CUDA indisponible -> bascule automatique hors 4-bit.")

    train_dataset = build_dataset(args.train_file, max_samples=args.max_train_samples)
    eval_dataset = build_dataset(args.eval_file, max_samples=args.max_eval_samples)

    print(f"Train rows : {len(train_dataset)}")
    print(f"Eval rows  : {len(eval_dataset)}")

    model, tokenizer = load_model_and_tokenizer(
        model_name=args.model_name,
        use_4bit=use_4bit,
    )
    target_modules = detect_target_modules(model)
    print(f"LoRA target modules: {', '.join(target_modules)}")

    peft_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=target_modules,
    )

    training_args = SFTConfig(
        output_dir=str(args.output_dir),
        num_train_epochs=args.num_train_epochs,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_ratio=args.warmup_ratio,
        weight_decay=args.weight_decay,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        eval_steps=args.eval_steps,
        eval_strategy="steps",
        save_strategy="steps",
        bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
        fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
        use_cpu=not torch.cuda.is_available(),
        dataloader_pin_memory=torch.cuda.is_available(),
        report_to="none",
        seed=args.seed,
        dataset_text_field="text",
        max_length=args.max_seq_length,
        packing=args.packing,
    )

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        peft_config=peft_config,
        args=training_args,
    )

    trainer.train()
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))

    print(f"Adapter LoRA sauvegarde dans : {args.output_dir}")


if __name__ == "__main__":
    main()
