from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset

# model (eng yengil boshlanish uchun)
model_name = "distilgpt2"

print("Model yuklanmoqda...")

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_name)

print("Dataset yuklanmoqda...")

dataset = load_dataset("json", data_files="data.jsonl")

# textni birlashtiramiz
def format_data(example):
    text = "Savol: " + example["instruction"] + "\nJavob: " + example["response"]
    return {"text": text}

dataset = dataset.map(format_data)

# token qilish
def tokenize(example):
    tokens = tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

tokenized = dataset.map(tokenize, batched=True)

from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./model",
    per_device_train_batch_size=2,
    num_train_epochs=30,
    save_steps=100,
    logging_steps=10
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"]
)

print("Training boshlandi...")

trainer.train()

print("Model saqlanmoqda...")

trainer.save_model("./model")
tokenizer.save_pretrained("./model")

print("TAYYOR 🚀")