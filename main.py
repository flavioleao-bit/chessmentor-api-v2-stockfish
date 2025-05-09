from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Chess Mentor API",
        version="2.0.0",
        description="API para suporte ao GPT Chess Mentor 2.1",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {"url": "https://chessmentor-api-v2.onrender.com"}
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 🔹 Endpoint 1: reconstrução do tabuleiro a partir de PGN
class PGNInput(BaseModel):
    pgn: str

@app.post("/obter_estado_do_tabuleiro", operation_id="obterEstadoDoTabuleiro")
def obter_estado(req: PGNInput):
    return {
        "message": "Reconstrução simulada com base no PGN",
        "fen": "FEN gerada fictícia a partir do PGN recebido",
        "pgn": req.pgn
    }

# 🔹 Endpoint 2: análise simulada
class AnalyzeInput(BaseModel):
    fen: str
    depth: int = 18
    multiPV: int = 10

@app.post("/analyze", operation_id="analyzePosition")
def analyze_position(req: AnalyzeInput):
    return {
        "message": "Análise simulada da FEN",
        "fen": req.fen,
        "depth": req.depth,
        "multiPV": req.multiPV,
        "bestMoves": ["Nf3", "d4", "Bc4"]
    }

# 🔹 Endpoint 3: estatísticas de abertura
class OpeningInput(BaseModel):
    moves: list[str]

@app.post("/opening", operation_id="getOpeningStats")
def opening_stats(req: OpeningInput):
    return {
        "eco": "C20",
        "name": "King's Pawn Game",
        "moves": req.moves,
        "stats": {"white": 42, "draw": 28, "black": 30}
    }

# 🔹 Endpoint 4: finais com tablebase
class TablebaseInput(BaseModel):
    fen: str

@app.post("/tablebase", operation_id="queryTablebase")
def tablebase_lookup(req: TablebaseInput):
    return {
        "fen": req.fen,
        "result": "draw",
        "dtm": 0,
        "winningLine": ["Kd6", "Rc7", "Ra8"]
    }

# 🔹 Endpoint 5: busca de partidas modelo
class SearchGamesInput(BaseModel):
    fen: str
    pattern: str

@app.post("/search_games", operation_id="searchModelGames")
def search_games(req: SearchGamesInput):
    return {
        "matches": [
            {
                "white": "Kasparov",
                "black": "Karpov",
                "event": "Moscou 1985",
                "year": 1985,
                "moves": "1.e4 c5 2.Nf3 d6..."
            },
            {
                "white": "Fischer",
                "black": "Spassky",
                "event": "Reykjavik 1972",
                "year": 1972,
                "moves": "1.e4 e5 2.Nf3 Nc6..."
            }
        ]
    }
