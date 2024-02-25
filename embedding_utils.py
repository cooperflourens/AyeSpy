import torch
from transformers import BertModel, BertTokenizer

def generate_embedding(transcribed_text, tokenizer, model):
    inputs = tokenizer(transcribed_text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state[:,0,:].numpy()
    return embedding