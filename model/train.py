import json
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Load training data
with open("data/training_data.json") as f:
    data = json.load(f)

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

inputs = [f"translate English to SQL: {d['input']}" for d in data]
targets = [d["output"] for d in data]

input_enc = tokenizer(inputs, padding=True, truncation=True, return_tensors="pt")
target_enc = tokenizer(targets, padding=True, truncation=True, return_tensors="pt")

optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)

model.train()

for epoch in range(3):
    optimizer.zero_grad()
    outputs = model(
        input_ids=input_enc["input_ids"],
        attention_mask=input_enc["attention_mask"],
        labels=target_enc["input_ids"]
    )
    loss = outputs.loss
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch+1} Loss: {loss.item()}")

# SAVE MODEL + TOKENIZER (THIS IS THE KEY)
model.save_pretrained("model/nl2sql_model")
tokenizer.save_pretrained("model/nl2sql_model")

print("✅ Model and tokenizer saved successfully")
