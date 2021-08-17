import chess
from chess import Board
import numpy as np
import pandas as pd
import itertools
import loggers
import logging
order = ['K','Q','R','B','N','P','k','q','r','b','n','p']


def array_to_board(helper):
    rows = []
    for s in helper:
        strng = []
        temp = 0
        for ind, char in enumerate(s):
            if char.isdigit():
                temp += 1
                if ind == len(s) - 1:
                    strng.append(str(temp))
            else:
                if temp:
                    strng.append(str(temp))
                    strng.append(char)
                    temp = 0
                else:
                    strng.append(char)

        rows.append(''.join(strng))

    state_in_string = '/'.join(rows)
    return chess.Board(state_in_string)


def tensor_to_board(tensor: np.ndarray):
    helper = np.ones((8, 8), dtype=np.str)
    tensor = tensor.reshape(12,8,8)
    for i in range(12):
        for x in range(8):
            for y in range(8):
                if tensor[i, x, y]:
                    helper[x, y] = order[i]

    helper = helper[::-1]
    print(helper)
    rows = []
    for s in helper:
        strng = []
        temp = 0
        for ind, char in enumerate(s):
            if char.isdigit():
                temp += 1
                if ind == len(s) - 1:
                    strng.append(str(temp))
            else:
                if temp:
                    strng.append(str(temp))
                    strng.append(char)
                    temp = 0
                else:
                    strng.append(char)

        rows.append(''.join(strng))

    state_in_string = '/'.join(rows)
    return chess.Board(state_in_string)


class Game:
    def __init__(self):
        self.currentPlayer = 1
        self.gameState = GameState(chess.Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'), 1)
        self.actionSpace = self.gameState.movelist
        self.pieceOrder = ['K','Q','R','B','N','P','k','q','r','b','n','p']
        self.input_shape = (2,6,8,8)
        self.grid_shape =
        self.name = 'chess'
        self.state_size = self.gameState.binary.shape
        self.action_size = len(self.actionSpace)

    def reset(self):
        self.gameState = GameState(chess.Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'), 1)
        self.currentPlayer = 1
        return self.gameState

    def step(self, action):

        next_state, value, done = self.gameState.takeAction(action)
        self.gameState = next_state
        self.currentPlayer = -self.currentPlayer
        info = None
        return ((next_state, value, done, info))

    def identities(self, state, actionValues):

        identities  = [(state, actionValues), (state, actionValues)]
        return identities


class GameState:

    def __init__(self, board: chess.Board, playerTurn):
        self.board = board
        self.pieceOrder = ['K','Q','R','B','N','P','k','q','r','b','n','p']
        self.playerTurn = playerTurn
        self.board.turn = playerTurn
        self.allowedActions = self._allowedActions()
        self.movelist = self._read_movelist()
        self.binary = self._binary()
        self.value = self._getValue()
        self.score = self._getScore()
        self.isEndGame = self._checkForEndGame()
        self.id = self._convertStateToId()

    def board_to_tensor(self):
        order_piecenames = [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]
        tensor = np.zeros((12, 8, 8))
        for ind, piece in enumerate(order_piecenames):
            tensor[ind, :, :] = np.array(self.board.pieces(piece, chess.WHITE).tolist(), dtype=np.int).reshape(8, 8)
            tensor[ind + 6, :, :] = np.array(self.board.pieces(piece, chess.BLACK).tolist(), dtype=np.int).reshape(8, 8)
        return tensor

    def _allowedActions(self) -> list:
        actions = list(self.board.legal_moves)
        movelist = self._read_movelist()
        indexes = [(np.where(movelist == str(action))[0]) for action in actions]
        chain = list(itertools.chain.from_iterable(indexes))
        return chain

    def _read_movelist(self) -> np.ndarray:
        return np.squeeze(pd.read_csv('movelist.txt', delimiter='\n', header=None).values)

    def _binary(self) -> np.ndarray:
        order_piecenames = [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]
        tensor = np.zeros((2, 6, 8, 8))
        for ind, piece in enumerate(order_piecenames):
            tensor[0, ind, :, :] = np.array(self.board.pieces(piece, chess.WHITE).tolist(), dtype=np.int).reshape(8, 8)
            tensor[1, ind, :, :] = np.array(self.board.pieces(piece, chess.BLACK).tolist(), dtype=np.int).reshape(8, 8)
        return tensor

    def _convertStateToId(self):
        return self.board.epd()[:-6]

    def _checkForEndGame(self) -> bool:
        if self.board.is_checkmate() or self.board.is_stalemate():
            return 1
        else:
            return 0

    def _getValue(self) -> tuple:
        if self.board.is_checkmate() or self.board.is_stalemate():
            return (-1, -1, -1)
        else:
            return (0, 0, 0)

    def _getScore(self) -> tuple:
        tmp = self.value
        return(tmp[1],tmp[2])

    def takeAction(self,action):
        newBoard = self.board.copy()
        newBoard.push(chess.Move.from_uci(self.movelist[action]))
        newState = GameState(newBoard,-self.playerTurn)
        value=0
        done=0
        if newState.isEndGame:
            value = newState.value[0]
            done=1
        return (newState,value,done)

    def render(self,logger):
        logger.info("\n" + str(self.board))
        logger.info('-----------------')

