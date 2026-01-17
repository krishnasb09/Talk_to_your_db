from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("model/nl2sql_model")
model = T5ForConditionalGeneration.from_pretrained("model/nl2sql_model")

query = "Show all customers"

input_text = f"translate English to SQL: {query}"
tokens = tokenizer(input_text, return_tensors="pt")

output = model.generate(**tokens)
sql = tokenizer.decode(output[0], skip_special_tokens=True)

print("Generated SQL:", sql)
