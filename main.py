
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from stockfish import Stockfish
import os
import subprocess
import requests
import zipfile
import chess
import chess.pgn
import io

app = FastAPI()


class PGNInput(BaseModel):
    pgn: str


class AnalyzeInput(BaseModel):
    fen: str
    depth: int = 18
    multiPV: int = 10


class OpeningInput(BaseModel):
    moves: list[str]


class TablebaseInput(BaseModel):
    fen: str


class SearchGamesInput(BaseModel):
    fen: str
    pattern: str


class AnalyzePositionRequest(BaseModel):
    fen: str


class MoveEvaluation(BaseModel):
    move: str
    centipawn: int | None = None
    mate: int | None = None


class AnalyzePositionResponse(BaseModel):
    best_moves: list[MoveEvaluation]


def ensure_stockfish():
    os.makedirs("engine", exist_ok=True)
    stockfish_path = "./engine/stockfish"

    if not os.path.isfile(stockfish_path):
        print("🔽 Baixando Stockfish...")
        url = "https://stockfishchess.org/files/stockfish-ubuntu-x86-64-avx2.zip"
        zip_path = "./engine/stockfish.zip"
        extract_path = "./engine"

        response = requests.get(url)
        with open(zip_path, "wb") as f:
            f.write(response.content)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.startswith("stockfish") and not file.endswith(".zip"):
                    os.rename(os.path.join(root, file), stockfish_path)
                    break

        os.chmod(stockfish_path, 0o755)

    return stockfish_path


@app.post("/analyzePositionV2", response_model=AnalyzePositionResponse)
def analyze_position_v2(request: AnalyzePositionRequest):
    try:
        stockfish_path = ensure_stockfish()
        stockfish = Stockfish(path=stockfish_path)

        if not stockfish.is_fen_valid(request.fen):
            raise HTTPException(status_code=400, detail="FEN inválido")

        stockfish.set_fen_position(request.fen)
        stockfish.set_depth(15)
        stockfish.update_engine_parameters({
            "Threads": 2,
            "Hash": 128,
            "MultiPV": 3
        })

        top_moves = stockfish.get_top_moves(3)
        response = [
            MoveEvaluation(
                move=mv["Move"],
                centipawn=mv.get("Centipawn"),
                mate=mv.get("Mate")
            ) for mv in top_moves
        ]

        return AnalyzePositionResponse(best_moves=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/obter_estado_do_tabuleiro")
def obter_estado_do_tabuleiro(data: PGNInput):
    try:
        game = chess.pgn.read_game(io.StringIO(data.pgn))
        board = game.end().board()
        return {"fen": board.fen()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar PGN: {str(e)}")


@app.post("/analyze")
def analyze(data: AnalyzeInput):
    try:
        stockfish_path = ensure_stockfish()
        stockfish = Stockfish(path=stockfish_path, depth=data.depth, parameters={"MultiPV": data.multiPV})
        stockfish.set_fen_position(data.fen)
        return {"analysis": stockfish.get_top_moves(data.multiPV)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/opening")
def get_opening_stats(data: OpeningInput):
    try:
        opening_db = {
            "e4": {"eco": "C20", "name": "King's Pawn Game"},
            "d4": {"eco": "D00", "name": "Queen's Pawn Game"},
            "e4 e5": {"eco": "C20", "name": "Open Game"},
            "d4 d5": {"eco": "D00", "name": "Closed Game"},
        }
        key = " ".join(data.moves[:2]).lower()
        return opening_db.get(key, {"eco": "?", "name": "Unknown Opening"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tablebase")
def query_tablebase(data: TablebaseInput):
    try:
        board = chess.Board(data.fen)
        if board.is_game_over():
            return {"result": board.result()}
        elif len(board.piece_map()) <= 6:
            return {"status": "Tablebase: Assume Draw (6 or fewer pieces)"}
        else:
            return {"status": "Tablebase not applicable: too many pieces"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search_games")
def search_model_games(data: SearchGamesInput):
    return {
        "message": f"Busca simulada por partidas com estrutura semelhante ao FEN: {data.fen} e padrão: {data.pattern}."
    }
