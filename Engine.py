from copy import deepcopy


class Game:
    """Storing information about the current game-state. Check valid moves at the current-state. Keep move-log."""

    def __init__(self):
        # 8x8 board made of 2D list
        # If None, then there's no piece at that position
        # The first character represents the color of the piece, "b"-Black, "w"-White
        # The second character represents the type of the piece, "K"-King, "Q"-Queen, "R"-Rook, "N"-Knight, "B"-Bishop, "P"-pawn
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                      ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.whiteToMove = True
        self.whiteKing = (7, 4)
        self.blackKing = (0, 4)

        self.whitePieces = [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
        self.blackPieces = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]

        self.whitePieces.sort()
        self.blackPieces.sort(reverse=True)

        self.moveFunctions = {"P": self.getPawnMoves, "N": self.getKnightMoves, "B": self.getBishopMoves, "R": self.getRookMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}

        self.inCheck = False
        self.checkmate = False
        self.stalemate = False

        self.checks = {}
        self.xRayChecks = {}

        self.validMoves = {}

        self.moveLog = []

        self.castlePossible = {"w": [(7, 0), (7, 7)], "b": [(0, 0), (0, 7)]}

    def getValidMoves(self):
        moves = {}
        ally, enemy, king, pieces = ("w", "b", self.whiteKing, self.whitePieces) if self.whiteToMove else ("b", "w", self.blackKing, self.blackPieces)

        self.checks, self.xRayChecks = ({}, {})
        self.inCheck = self.checkChecks(ally, enemy, king)

        if self.inCheck:
            if len(self.checks) == 2:
                moves[king] = []
                self.getKingMoves(king[0], king[1], moves, ally, enemy)

                if not moves[king]:
                    del moves[king]
            else:
                direction = tuple(self.checks.keys())[0]
                check = self.checks[direction]
                piece = self.board[check[0]][check[1]]

                validSquares = [check]

                if piece[1] != "N":
                    row, col = (king[0] + direction[0], king[1] + direction[1])
                    while (row, col) != check:
                        validSquares.append((row, col))

                        row += direction[0]
                        col += direction[1]

                moves = self.getAllPossibleMoves(ally, enemy, pieces, validSquares)

        else:
            moves = self.getAllPossibleMoves(ally, enemy, pieces)

        l = len(moves)

        self.checkmate = l == 0 and self.inCheck
        self.stalemate = l == 0 and not self.inCheck

        self.validMoves = moves

        return moves

    def checkChecks(self, ally, enemy, king, check=False):
        for direction in ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)):  # Knight moves
            checkRow, checkCol = king[0] + direction[0], king[1] + direction[1]

            if (0 <= checkRow <= 7) and (0 <= checkCol <= 7):
                piece = self.board[checkRow][checkCol]

                if piece == enemy + "N":
                    if check:
                        return True
                    self.checks[direction] = (checkRow, checkCol)
                    break

        for direction in ((1, 0), (0, 1), (-1, 0), (0, -1)):  # Rook moves
            checkRow, checkCol = king[0] + direction[0], king[1] + direction[1]

            if (0 <= checkRow <= 7) and (0 <= checkCol <= 7):
                piece = self.board[checkRow][checkCol]

                if piece[0] is enemy and piece[1] in ("R", "Q", "K"):
                    if check:
                        return True
                    self.checks[direction] = (checkRow, checkCol)
                    continue

                pin = None

                while (0 <= checkRow <= 7) and (0 <= checkCol <= 7):
                    piece = self.board[checkRow][checkCol]

                    if piece[0] is enemy and piece[1] not in ("R", "Q"):
                        break
                    elif piece[0] is ally and not pin:
                        if check:
                            break
                        pin = (checkRow, checkCol)
                    elif pin and piece[0] is ally:
                        break
                    elif pin and piece[0] is enemy and piece[1] in ("R", "Q"):
                        self.xRayChecks[pin] = (direction, (-direction[0], -direction[1]), piece[1], king)
                        break
                    elif piece[0] is enemy and piece[1] in ("R", "Q"):
                        if check:
                            return True
                        self.checks[direction] = (checkRow, checkCol)
                        break

                    checkRow += direction[0]
                    checkCol += direction[1]

        for direction in ((-1, -1), (-1, 1)):  # Bishop moves upwards
            checkRow, checkCol = king[0] + direction[0], king[1] + direction[1]

            if (0 <= checkRow <= 7) and (0 <= checkCol <= 7):
                piece = self.board[checkRow][checkCol]

                if piece[0] is enemy and (piece[1] in ("B", "Q", "K") or piece == "bP"):
                    if check:
                        return True
                    self.checks[direction] = (checkRow, checkCol)
                    continue

                pin = None

                while (0 <= checkRow <= 7) and (0 <= checkCol <= 7):
                    piece = self.board[checkRow][checkCol]

                    if piece[0] is enemy and piece[1] not in ("B", "Q"):
                        break
                    elif piece[0] is ally and not pin:
                        if check:
                            break
                        pin = (checkRow, checkCol)
                    elif pin and piece[0] is ally:
                        break
                    elif pin and piece[0] is enemy and piece[1] in ("B", "Q"):
                        self.xRayChecks[pin] = (direction, (-direction[0], -direction[1]), piece[1], king)
                        break
                    elif piece[0] is enemy and piece[1] in ("B", "Q"):
                        if check:
                            return True
                        self.checks[direction] = (checkRow, checkCol)
                        break

                    checkRow += direction[0]
                    checkCol += direction[1]

        for direction in ((1, -1), (1, 1)):  # Bishop moves downwards
            checkRow, checkCol = king[0] + direction[0], king[1] + direction[1]

            if (0 <= checkRow <= 7) and (0 <= checkCol <= 7):
                piece = self.board[checkRow][checkCol]

                if piece[0] is enemy and (piece[1] in ("B", "Q", "K") or piece == "wP"):
                    if check:
                        return True
                    self.checks[direction] = (checkRow, checkCol)
                    continue

                pin = None

                while (0 <= checkRow <= 7) and (0 <= checkCol <= 7):
                    piece = self.board[checkRow][checkCol]

                    if piece[0] is enemy and piece[1] not in ("B", "Q"):
                        break
                    elif piece[0] is ally and not pin:
                        if check:
                            break
                        pin = (checkRow, checkCol)
                    elif pin and piece[0] is ally:
                        break
                    elif pin and piece[0] is enemy and piece[1] in ("B", "Q"):
                        self.xRayChecks[pin] = (direction, (-direction[0], -direction[1]), piece[1], king)
                        break
                    elif piece[0] is enemy and piece[1] in ("B", "Q"):
                        if check:
                            return True
                        self.checks[direction] = (checkRow, checkCol)
                        break

                    checkRow += direction[0]
                    checkCol += direction[1]

        if check:
            return False

        return True if self.checks else False

    def getAllPossibleMoves(self, ally, enemy, pieces, valid=False):
        moves = {}

        for r, c in pieces:
            moves[(r, c)] = []

            piece = self.board[r][c][1]
            pin = self.xRayChecks.get((r, c), None)

            self.moveFunctions[piece](r, c, moves, ally, enemy, pin, valid)

            if not moves[(r, c)]:
                del moves[(r, c)]

        return moves

    def getPawnMoves(self, r, c, moves, ally, enemy, pin, valid):
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enPassantRow = 3
            enemyStart = 1
            king = self.whiteKing
        else:
            moveAmount = 1
            startRow = 1
            enPassantRow = 4
            enemyStart = 6
            king = self.blackKing

        if self.board[r + moveAmount][c] == "--" and (not pin or (moveAmount, 0) in pin):
            if not valid or (r + moveAmount, c) in valid:
                moves[(r, c)].append((r + moveAmount, c))

            if r == startRow and self.board[r + 2 * moveAmount][c] == "--" and (not valid or (r + 2 * moveAmount, c) in valid):
                moves[(r, c)].append((r + 2 * moveAmount, c))

        if c - 1 >= 0:
            if self.board[r + moveAmount][c - 1][0] == enemy and (not pin or (moveAmount, -1) in pin) and (not valid or (r + moveAmount, c - 1) in valid):
                moves[(r, c)].append((r + moveAmount, c - 1))

            elif r == enPassantRow and self.board[enPassantRow][c - 1] == enemy + "P" and (not valid or (r + moveAmount, c - 1) in valid):
                prevMove = self.moveLog[-1]

                if prevMove.pieceMoved == enemy + "P" and prevMove.startRow == enemyStart and prevMove.endRow == enPassantRow and prevMove.endCol == c - 1:
                    if king[0] != r:
                        moves[(r, c)].append((r + moveAmount, c - 1))
                    else:
                        d = int((c - king[1]) / abs(c - king[1]))

                        checkCol = c + 2 * d if prevMove.endCol == c + d else c + d

                        while 0 <= checkCol <= 7:
                            piece = self.board[r][checkCol]

                            if piece[0] is ally or (piece[0] is enemy and piece[1] not in ("R", "Q")):
                                moves[(r, c)].append((r + moveAmount, c - 1))
                            elif piece[0] is enemy and piece[1] in ("R", "Q"):
                                break

                            checkCol += d

        if c + 1 <= 7:
            if self.board[r + moveAmount][c + 1][0] == enemy and (not pin or (moveAmount, 1) in pin) and (not valid or (r + moveAmount, c + 1) in valid):
                moves[(r, c)].append((r + moveAmount, c + 1))

            elif r == enPassantRow and self.board[enPassantRow][c + 1] == enemy + "P" and (not valid or (r + moveAmount, c + 1) in valid):
                prevMove = self.moveLog[-1]

                if prevMove.pieceMoved == enemy + "P" and prevMove.startRow == enemyStart and prevMove.endRow == enPassantRow and prevMove.endCol == c + 1:
                    if king[0] != r:
                        moves[(r, c)].append((r + moveAmount, c + 1))
                    else:
                        d = int((c - king[1]) / abs(c - king[1]))

                        checkCol = c + 2 * d if prevMove.endCol == c + d else c + d

                        while 0 <= checkCol <= 7:
                            piece = self.board[r][checkCol]

                            if piece[0] is ally or (piece[0] is enemy and piece[1] not in ("R", "Q")):
                                moves[(r, c)].append((r + moveAmount, c + 1))
                            elif piece[0] is enemy and piece[1] in ("R", "Q"):
                                break

                            checkCol += d

    def getKnightMoves(self, r, c, moves, ally, enemy, pin, valid):
        if pin:
            return

        for direction in ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)):
            endRow = r + direction[0]
            endCol = c + direction[1]

            if 0 <= endRow <= 7 and 0 <= endCol <= 7 and (not valid or (endRow, endCol) in valid):
                piece = self.board[endRow][endCol]
                if piece[0] in (enemy, "-"):
                    moves[(r, c)].append((endRow, endCol))

    def getBishopMoves(self, r, c, moves, ally, enemy, pin, valid):
        for direction in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            if not pin or direction in pin:
                endRow, endCol = r + direction[0], c + direction[1]

                while (0 <= endRow <= 7) and (0 <= endCol <= 7):
                    piece = self.board[endRow][endCol]

                    if piece[0] == ally:
                        break
                    elif piece[0] == enemy:
                        if not valid or (endRow, endCol) in valid:
                            moves[(r, c)].append((endRow, endCol))
                        break
                    else:
                        if not valid or (endRow, endCol) in valid:
                            moves[(r, c)].append((endRow, endCol))

                        endRow += direction[0]
                        endCol += direction[1]

    def getRookMoves(self, r, c, moves, ally, enemy, pin, valid):
        for direction in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            if not pin or direction in pin:
                endRow, endCol = r + direction[0], c + direction[1]

                while (0 <= endRow <= 7) and (0 <= endCol <= 7):
                    piece = self.board[endRow][endCol]

                    if piece[0] == ally:
                        break
                    elif piece[0] == enemy:
                        if not valid or (endRow, endCol) in valid:
                            moves[(r, c)].append((endRow, endCol))
                        break
                    else:
                        if not valid or (endRow, endCol) in valid:
                            moves[(r, c)].append((endRow, endCol))

                        endRow += direction[0]
                        endCol += direction[1]

    def getQueenMoves(self, r, c, moves, ally, enemy, pin, valid):
        self.getRookMoves(r, c, moves, ally, enemy, pin, valid)
        self.getBishopMoves(r, c, moves, ally, enemy, pin, valid)

    def getKingMoves(self, r, c, moves, ally, enemy, pin=None, valid=None):
        for direction in ((1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            endRow, endCol = r + direction[0], c + direction[1]

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                piece = self.board[endRow][endCol]
                if piece[0] != ally:
                    self.board[r][c] = "--"
                    self.board[endRow][endCol] = ally+"K"

                    if not self.checkChecks(ally, enemy, (endRow, endCol), True):
                        moves[(r, c)].append((endRow, endCol))

                    self.board[r][c] = ally + "K"
                    self.board[endRow][endCol] = piece

        # ((0, 1), (0, -1))

        if c + 1 <= 7:  # (0, 1)
            piece = self.board[r][c + 1]
            if piece[0] != ally:
                self.board[r][c] = "--"
                self.board[r][c + 1] = ally + "K"

                if not self.checkChecks(ally, enemy, (r, c + 1), True):
                    moves[(r, c)].append((r, c + 1))

                    if not self.inCheck and piece == "--" and c == 4 and self.board[r][c + 2] == "--" and (r, 7) in self.castlePossible[ally]:
                        self.board[r][c + 1] = "--"
                        self.board[r][c + 2] = ally + "K"

                        if not self.checkChecks(ally, enemy, (r, c + 2), True):
                            moves[(r, c)].append((r, c + 2))
                            moves[(r, c)].append((r, c + 3))

                        self.board[r][c + 1] = ally + "K"
                        self.board[r][c + 2] = "--"

                self.board[r][c] = ally + "K"
                self.board[r][c + 1] = piece

        if 0 <= c - 1:  # (0, -1)
            piece = self.board[r][c - 1]
            if piece[0] != ally:
                self.board[r][c] = "--"
                self.board[r][c - 1] = ally + "K"

                if not self.checkChecks(ally, enemy, (r, c - 1), True):
                    moves[(r, c)].append((r, c - 1))

                    if not self.inCheck and piece == "--" and c == 4 and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--" and (r, 0) in self.castlePossible[ally]:
                        self.board[r][c - 1] = "--"
                        self.board[r][c - 2] = ally + "K"

                        if not self.checkChecks(ally, enemy, (r, c - 2), True):
                            moves[(r, c)].append((r, c - 2))
                            moves[(r, c)].append((r, c - 4))

                        self.board[r][c - 1] = ally + "K"
                        self.board[r][c - 2] = "--"

                self.board[r][c] = ally + "K"
                self.board[r][c - 1] = piece

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved

        allyPieces, enemyPieces, ally, enemy, castle, row = (self.whitePieces, self.blackPieces, "w", "b", True, 7) if self.whiteToMove else (self.blackPieces, self.whitePieces, "b", "w", False, 0)

        if move.promotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        elif move.pieceMoved == "wP" and move.startRow == 3 and move.startCol != move.endCol and move.pieceCaptured == "--" and self.board[3][move.endCol] == "bP" and self.moveLog:
            prevMove = self.moveLog[-1]

            if prevMove.pieceMoved == "bP" and prevMove.startRow == 1 and prevMove.startCol == move.endCol:
                move.enPassant = True
                self.board[3][move.endCol] = "--"
                self.blackPieces.remove((3, move.endCol))
        elif move.pieceMoved == "bP" and move.startRow == 4 and move.startCol != move.endCol and move.pieceCaptured == "--" and self.board[4][move.endCol] == "wP" and self.moveLog:
            prevMove = self.moveLog[-1]

            if prevMove.pieceMoved == "wP" and prevMove.startRow == 6 and prevMove.startCol == move.endCol:
                move.enPassant = True
                self.board[4][move.endCol] = "--"
                self.whitePieces.remove((4, move.endCol))

        if move.pieceMoved[1] == "R" and (move.startRow, move.startCol) in self.castlePossible[ally]:
            move.castlePossible = deepcopy(self.castlePossible)
            self.castlePossible[ally].remove((move.startRow, move.startCol))

        if move.pieceCaptured[1] == "R" and (move.endRow, move.endCol) in self.castlePossible[enemy]:
            move.castlePossible = deepcopy(self.castlePossible)
            self.castlePossible[enemy].remove((move.endRow, move.endCol))

        if move.pieceMoved[1] == "K":
            if move.castle:
                self.board[row][4] = "--"
                self.board[row][move.endCol] = ally+"K"
                if move.endCol == 6:
                    self.board[row][7] = "--"
                    self.board[row][5] = ally+"R"
                    allyPieces.append((row, 5))
                    allyPieces.remove((row, 7))
                else:
                    self.board[row][0] = "--"
                    self.board[row][3] = ally+"R"
                    allyPieces.append((row, 3))
                    allyPieces.remove((row, 0))

            if self.whiteToMove:
                self.whiteKing = (move.endRow, move.endCol)
            else:
                self.blackKing = (move.endRow, move.endCol)

            if self.castlePossible[ally]:
                move.castlePossible = deepcopy(self.castlePossible)
            self.castlePossible[ally] = []

        allyPieces.append((move.endRow, move.endCol))
        allyPieces.remove((move.startRow, move.startCol))
        if move.pieceCaptured[0] == enemy:
            enemyPieces.remove((move.endRow, move.endCol))

        self.moveLog.append(move)

        self.inCheck = False
        self.checks = {}
        self.xRayChecks = {}

        self.whiteToMove = not self.whiteToMove

        self.whitePieces.sort()
        self.blackPieces.sort(reverse=True)

    def undoMove(self):
        if not self.moveLog:
            return

        move = self.moveLog.pop()

        allyPieces, enemyPieces, ally, enemy, castle, row = (self.whitePieces, self.blackPieces, "w", "b", True, 3) if not self.whiteToMove else (self.blackPieces, self.whitePieces, "b", "w", False, 4)

        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = move.pieceCaptured

        if move.pieceMoved[1] == "K":
            if not self.whiteToMove:
                self.whiteKing = (move.startRow, move.startCol)
            else:
                self.blackKing = (move.startRow, move.startCol)

            if move.castle:
                if move.endCol == 6:
                    self.board[move.endRow][5], self.board[move.endRow][7] = "--", ally + "R"
                    allyPieces.remove((move.endRow, 5))
                    allyPieces.append((move.endRow, 7))
                else:
                    self.board[move.endRow][3], self.board[move.endRow][0] = "--", move.pieceMoved[0] + "R"
                    allyPieces.remove((move.endRow, 3))
                    allyPieces.append((move.endRow, 0))
            if move.castlePossible and move.castlePossible[ally]:
                self.castlePossible = deepcopy(move.castlePossible)
        elif move.enPassant:
            self.board[row][move.endCol] = enemy+"P"
            enemyPieces.append((row, move.endCol))
        elif move.castlePossible and move.pieceMoved[1] == "R" and move.castlePossible[ally]:
            self.castlePossible = deepcopy(move.castlePossible)

        if move.pieceCaptured[0] == enemy:
            enemyPieces.append((move.endRow, move.endCol))
            if move.castlePossible and move.pieceCaptured[1] == "R" and move.castlePossible[enemy]:
                self.castlePossible = deepcopy(move.castlePossible)

        allyPieces.append((move.startRow, move.startCol))
        allyPieces.remove((move.endRow, move.endCol))

        self.whiteToMove = not self.whiteToMove

        self.whitePieces.sort()
        self.blackPieces.sort(reverse=True)

        self.checkmate = False
        self.stalemate = False


class Move:
    def __init__(self, start, end, board):
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        if self.pieceCaptured == self.pieceMoved[0] + "R":
            self.pieceCaptured = "--"

        self.promotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)

        self.castle = self.pieceMoved[1] == "K" and abs(self.startCol - self.endCol) > 1

        if self.castle:
            self.endCol = 6 if self.endCol in (6, 7) else 2

        self.castlePossible = False

        self.enPassant = False

        self.check = False
