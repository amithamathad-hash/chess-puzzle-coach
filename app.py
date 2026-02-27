import chess
import chess.engine
import streamlit as st
from streamlit_chessboard import chessboard

st.set_page_config(page_title="Chess Puzzle Coach", layout="centered")
st.title("♟️ Chess Puzzle Coach")

# Initialize session board
if "board" not in st.session_state:
    st.session_state.board = chess.Board()

@st.cache_resource
def get_engine():
    return chess.engine.SimpleEngine.popen_uci("stockfish")

def solve_position(board, depth):
    engine = get_engine()
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    pv = info.get("pv", [])
    best = pv[0] if pv else None
    score = info["score"].pov(board.turn)
    mate_in = score.mate() if score.is_mate() else None
    return best, pv[:6], score, mate_in

# Sidebar controls
st.sidebar.header("Puzzle Settings")

fen_input = st.sidebar.text_input(
    "Load FEN",
    value=st.session_state.board.fen()
)

if st.sidebar.button("Load Position"):
    try:
        st.session_state.board = chess.Board(fen_input)
    except:
        st.sidebar.error("Invalid FEN")

depth = st.sidebar.slider("Engine Depth", 6, 22, 14)

# Display interactive board
move = chessboard(st.session_state.board.fen())

# If user made a move
if move:
    try:
        chess_move = chess.Move.from_uci(move)
        if chess_move in st.session_state.board.legal_moves:
            st.session_state.board.push(chess_move)
        else:
            st.warning("Illegal move")
    except:
        pass

col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Solve (Best Move)"):
        best, pv, score, mate_in = solve_position(
            st.session_state.board, depth
        )
        if best:
            st.success(
                f"Best move: {st.session_state.board.san(best)} ({best.uci()})"
            )
            if mate_in:
                st.info(f"Mate in {mate_in}")
            st.write("Evaluation:", score)

with col2:
    if st.button("↩️ Undo Move"):
        if st.session_state.board.move_stack:
            st.session_state.board.pop()

if st.button("🔄 Reset Board"):
    st.session_state.board = chess.Board()
