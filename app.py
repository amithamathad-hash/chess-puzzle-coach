import chess
import chess.engine
import streamlit as st


st.set_page_config(page_title="Chess Puzzle Coach", layout="centered")
st.title("♟️ Chess Puzzle Coach")
st.write("Paste a FEN position and solve the puzzle using Stockfish.")

fen = st.text_area(
    "FEN",
    value="8/8/8/8/8/8/8/8 w - - 0 1",
    height=80,
)

depth = st.slider("Engine Depth", 6, 22, 14)
move_uci = st.text_input("Your move (UCI format, e.g., e2e4, g1f3)")


@st.cache_resource
def get_engine():
    return chess.engine.SimpleEngine.popen_uci("stockfish")


def solve_position(fen_str: str, depth: int):
    board = chess.Board(fen_str)
    engine = get_engine()
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    pv = info.get("pv", [])
    best = pv[0] if pv else None
    score = info["score"].pov(board.turn)
    mate_in = score.mate() if score.is_mate() else None
    return board, best, pv[:6], score, mate_in


def explain(board_before: chess.Board, move: chess.Move, mate_in_best=None):
    board = board_before.copy()
    piece = board.piece_at(move.from_square)
    board.push(move)

    messages = []

    if board.is_checkmate():
        messages.append("✅ This move delivers CHECKMATE.")
    elif board.is_check():
        messages.append("⚡ This move gives check (forcing move).")

    if piece and piece.piece_type == chess.KNIGHT and board.is_check():
        messages.append(
            "♞ Knight checks cannot be blocked — only king move or capture."
        )

    if mate_in_best is not None:
        if mate_in_best > 0:
            messages.append(f"Engine sees forced mate in {abs(mate_in_best)}.")
        else:
            messages.append(
                f"Opponent has forced mate in {abs(mate_in_best)}."
            )

    if not messages:
        messages.append(
            "Tip: In puzzles, consider checks, captures, and threats first."
        )

    return " ".join(messages)


col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Solve (Best Move)"):
        try:
            board, best, pv, score, mate_in = solve_position(
                fen.strip(), depth
            )

            if best:
                st.success(
                    f"Best move: {board.san(best)} ({best.uci()})"
                )
                if mate_in is not None:
                    st.info(f"Mate in {mate_in}")
                st.write("Evaluation:", score)

                # Show principal variation
                pv_moves = []
                temp_board = board.copy()
                for move in pv:
                    pv_moves.append(temp_board.san(move))
                    temp_board.push(move)

                st.write("Line:", " ".join(pv_moves))
            else:
                st.error("No best move found. Check FEN.")

        except Exception as e:
            st.error(str(e))


with col2:
    if st.button("🧠 Check My Move"):
        try:
            board = chess.Board(fen.strip())

            if not move_uci.strip():
                st.warning("Enter a move first.")
                st.stop()

            move = chess.Move.from_uci(move_uci.strip())

            if move not in board.legal_moves:
                st.error("Illegal move in this position.")
                st.stop()

            board_sol, best, pv, score, mate_in = solve_position(
                fen.strip(), depth
            )

            if best and move.uci() == best.uci():
                st.success(f"🎯 Correct! {board.san(move)} is best.")
            else:
                st.error(
                    f"❌ Not best. Best move was {board_sol.san(best)} ({best.uci()})"
                )

            explanation = explain(
                chess.Board(fen.strip()), move, mate_in
            )
            st.write(explanation)

        except Exception as e:
            st.error(str(e))
