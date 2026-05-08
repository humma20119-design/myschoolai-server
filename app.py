from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print("Model yuklanmoqda...")

model_path = "./model"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

model.eval()

print("AI TAYYOR! (chiqish uchun: exit)\n")

while True:
    user_input = input("Siz: ")

    if user_input.lower() == "exit":
        break

    inputs = tokenizer.encode(user_input, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=100,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print("AI:", response)