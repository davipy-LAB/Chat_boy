import yaml

# Caminho do arquivo YAML
yaml_file_path = "F:/Chat_boy/AI_Chatboy/data/English/greetings (1).yml"

# Carrega o arquivo YAML
with open(yaml_file_path, 'r', encoding='utf-8') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

# Verifica se o arquivo YAML está vazio
if not data:
    print("O arquivo YAML está vazio.")
else:
    print("O arquivo YAML contém os seguintes dados:")
    print(data)