
# Imagem base: Python com sistema Linux
FROM python:3.11-slim

# Instalar dependências do sistema e o Stockfish via apt
RUN apt-get update && apt-get install -y \
    stockfish \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar os arquivos da API
COPY . /app

# Instalar dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar a API FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
