import ollama

def get_embedding(text, model='nomic-embed-text'):    
    return ollama.embeddings(model=model, prompt=text)['embedding']

if __name__ == '__main__':
    text = "Hello, I am learning OpenAI's LLM"
    embedding = get_embedding(text)
    print(embedding)