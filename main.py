from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from stockfish import Stockfish

app = FastAPI()


class AnalyzePositionRequest(BaseModel):
    fen: str


class MoveEvaluation(BaseModel):
    move: str
    centipawn: int | None = None
    mate: int | None = None


class AnalyzePositionResponse(BaseModel):
    best_moves: list[MoveEvaluation]


@app.post("/analyzePositionV2", response_model=AnalyzePositionResponse)
def analyze_position_v2(request: AnalyzePositionRequest):
    try:
        stockfish = Stockfish(path="./engine/stockfish")
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
