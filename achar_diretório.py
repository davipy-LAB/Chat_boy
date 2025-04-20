from datasets import load_dataset

# URL do arquivo raw no GitHub
corpus_url = "https://raw.githubusercontent.com/gunthercox/chatterbot-corpus/master/chatterbot_corpus/data/english/english.json"

# Carregar o dataset diretamente do GitHub
dataset = load_dataset("json", data_files={"train": corpus_url}, split="train")

# Exibir as primeiras linhas do dataset
print(dataset[0])
