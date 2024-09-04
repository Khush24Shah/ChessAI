import random
from Engine import Move

pawnScores = ((8, 8, 8, 8, 8, 8, 8, 8),
              (8, 8, 8, 8, 8, 8, 8, 8),
              (5, 6, 6, 7, 7, 6, 6, 5),
              (2, 3, 3, 5, 5, 3, 3, 2),
              (1, 2, 2, 4, 4, 2, 2, 1),
              (1, 1, 2, 3, 3, 2, 1, 1),
              (1, 1, 1, 0, 0, 1, 1, 1),
              (0, 0, 0, 0, 0, 0, 0, 0))

knightScores = ((1, 1, 1, 1, 1, 1, 1, 1),
                (1, 2, 2, 2, 2, 2, 2, 1),
                (1, 2, 3, 3, 3, 3, 2, 1),
                (1, 2, 3, 4, 4, 3, 2, 1),
                (1, 2, 3, 4, 4, 3, 2, 1),
                (1, 2, 3, 3, 3, 3, 2, 1),
                (1, 2, 2, 2, 2, 2, 2, 1),
                (1, 1, 1, 1, 1, 1, 1, 1))

bishopScores = ((4, 3, 2, 1, 1, 2, 3, 4),
                (3, 4, 3, 2, 2, 3, 4, 3),
                (2, 3, 4, 3, 3, 4, 3, 2),
                (1, 2, 3, 4, 4, 3, 2, 1),
                (1, 2, 3, 4, 4, 3, 2, 1),
                (2, 3, 4, 3, 3, 4, 3, 2),
                (3, 4, 3, 2, 2, 3, 4, 3),
                (4, 3, 2, 1, 1, 2, 3, 4))

rookScores = ((4, 3, 4, 4, 4, 4, 3, 4),
              (4, 4, 4, 4, 4, 4, 4, 4),
              (1, 1, 2, 3, 3, 2, 1, 1),
              (1, 2, 3, 4, 4, 3, 1, 1),
              (1, 2, 3, 4, 4, 3, 1, 1),
              (1, 1, 2, 3, 3, 2, 1, 1),
              (4, 4, 4, 4, 4, 4, 4, 4),
              (4, 3, 4, 4, 4, 4, 3, 4))

queenScores = ((1, 1, 1, 3, 1, 1, 1, 1),
               (1, 2, 3, 3, 3, 1, 1, 1),
               (1, 4, 3, 3, 3, 4, 2, 1),
               (1, 2, 3, 3, 3, 2, 2, 1),
               (1, 2, 3, 3, 3, 2, 2, 1),
               (1, 4, 3, 3, 3, 4, 2, 1),
               (1, 2, 3, 3, 3, 1, 1, 1),
               (1, 1, 1, 3, 1, 1, 1, 1))

kingScores = ((1, 1, 1, 1, 1, 1, 1, 1),
              (1, 1, 1, 1, 1, 1, 1, 1),
              (1, 1, 1, 1, 1, 1, 1, 1),
              (1, 1, 1, 1, 1, 1, 1, 1),
              (2, 1, 1, 1, 1, 1, 1, 2),
              (2, 2, 1, 1, 1, 1, 2, 2),
              (2, 2, 1, 1, 1, 1, 2, 2),
              (3, 4, 3, 2, 2, 3, 4, 3))

pieceValue = {"K": (0, kingScores), "Q": (9, queenScores), "R": (5, rookScores), "B": (3, bishopScores), "N": (3, knightScores), "P": (1, pawnScores)}

CHECKMATE = 10000
STALEMATE = 0

MAX_DEPTH = 4

global count


def scoreMaterial(game_state, white=False, black=False):
    whiteScore = blackScore = 0

    for position in game_state.whitePieces:
        whiteScore += pieceValue[game_state.board[position[0]][position[1]][1]]

    if white:
        return whiteScore

    for position in game_state.blackPieces:
        blackScore += pieceValue[game_state.board[position[0]][position[1]][1]]

    if black:
        return blackScore

    if game_state.checkmate:
        return -CHECKMATE if game_state.whiteToMove else CHECKMATE
    elif game_state.stalemate:
        return STALEMATE

    return whiteScore - blackScore


def scoreBoard(game_state):
    if game_state.checkmate:
        return -CHECKMATE if game_state.whiteToMove else CHECKMATE
    elif game_state.stalemate:
        return STALEMATE

    score = 0
    for position in game_state.whitePieces:
        piece = game_state.board[position[0]][position[1]][1]
        score += pieceValue[piece][0] + pieceValue[piece][1][position[0]][position[1]] / 10

    for position in game_state.blackPieces:
        piece = game_state.board[position[0]][position[1]][1]
        score -= pieceValue[piece][0] + pieceValue[piece][1][::-1][position[0]][position[1]] / 10

    return score


def findAIMove(game_state):
    global count

    count = 1

    move = minMaxMove(game_state, depth=MAX_DEPTH)

    if move is None:
        move = randomMove(game_state.getValidMoves())

    return move


def randomMove(validMoves):
    start = tuple(validMoves.keys())

    start = start[0] if len(start) == 1 else start[random.randint(0, len(start) - 1)]

    return start, random.choice(validMoves[start])


def greedyMove(game_state):
    turnMultiplier = 1 if game_state.whiteToMove else -1

    oppMinMaxScore = CHECKMATE
    bestMove = None

    moves = game_state.getValidMoves()

    startingMoves = list(moves.keys())
    random.shuffle(startingMoves)

    for playerStart in startingMoves:
        for playerEnd in moves[playerStart]:
            game_state.makeMove(Move(playerStart, playerEnd, game_state.board))
            oppValidMoves = game_state.getValidMoves()

            if game_state.checkmate:
                oppMaxScore = -CHECKMATE
            elif game_state.stalemate:
                oppMaxScore = STALEMATE
            else:
                oppMaxScore = -CHECKMATE

                for oppStart in oppValidMoves.keys():
                    for oppEnd in oppValidMoves[oppStart]:
                        game_state.makeMove(Move(oppStart, oppEnd, game_state.board))
                        game_state.getValidMoves()

                        if game_state.checkmate:
                            score = CHECKMATE
                        elif game_state.stalemate:
                            score = STALEMATE
                        else:
                            score = -turnMultiplier * scoreMaterial(game_state)

                        if score > oppMaxScore:
                            oppMaxScore = score

                        game_state.undoMove()

            if oppMaxScore < oppMinMaxScore:
                oppMinMaxScore = oppMaxScore
                bestMove = (playerStart, playerEnd)

            game_state.undoMove()

    return bestMove


def minMaxMove(game_state, depth=MAX_DEPTH):
    global bestMove
    bestMove = None

    # minMax(game_state, depth, game_state.whiteToMove)
    # negaMax(game_state, depth, 1 if game_state.whiteToMove else -1)
    negaMaxAlphaBeta(game_state, depth, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1)

    return bestMove


def minMax(game_state, depth, whiteToMove):
    if depth == 0 or game_state.checkmate or game_state.stalemate:
        return scoreBoard(game_state) if game_state.whiteToMove else -1 * scoreBoard(game_state)

    global bestMove

    moves = game_state.getValidMoves()

    startingMoves = list(moves.keys())
    random.shuffle(startingMoves)

    if whiteToMove:
        maxScore = -CHECKMATE
        for playerStart in startingMoves:
            for playerEnd in moves[playerStart]:
                game_state.makeMove(Move(playerStart, playerEnd, game_state.board))

                score = minMax(game_state, depth - 1, False)

                if score > maxScore:
                    maxScore = score

                    if depth == MAX_DEPTH:
                        bestMove = (playerStart, playerEnd)

                game_state.undoMove()

        return maxScore

    else:
        minScore = CHECKMATE
        for playerStart in startingMoves:
            for playerEnd in moves[playerStart]:
                game_state.makeMove(Move(playerStart, playerEnd, game_state.board))

                score = minMax(game_state, depth - 1, True)

                if score < minScore:
                    minScore = score

                    if depth == MAX_DEPTH:
                        bestMove = (playerStart, playerEnd)

                game_state.undoMove()

        return minScore


def negaMax(game_state, depth, turnMultiplier):
    if depth == 0 or game_state.checkmate or game_state.stalemate:
        return turnMultiplier * scoreBoard(game_state)

    global bestMove

    maxScore = -CHECKMATE

    moves = game_state.getValidMoves()

    startingMoves = list(moves.keys())
    random.shuffle(startingMoves)

    for playerStart in startingMoves:
        for playerEnd in moves[playerStart]:
            game_state.makeMove(Move(playerStart, playerEnd, game_state.board))

            score = -negaMax(game_state, depth - 1, -1 * turnMultiplier)

            if score > maxScore:
                maxScore = score

                if depth == MAX_DEPTH:
                    bestMove = (playerStart, playerEnd)

            game_state.undoMove()

    return maxScore


def negaMaxAlphaBeta(game_state, depth, alpha, beta, turnMultiplier):
    global count
    count += 1

    if depth == 0 or game_state.checkmate or game_state.stalemate:
        return turnMultiplier * scoreBoard(game_state)

    global bestMove

    maxScore = -CHECKMATE

    moves = game_state.getValidMoves()

    for playerStart in moves.keys():
        for playerEnd in moves[playerStart]:
            game_state.makeMove(Move(playerStart, playerEnd, game_state.board))

            score = -negaMaxAlphaBeta(game_state, depth - 1, -beta, -alpha, -1 * turnMultiplier)

            if score > maxScore:
                maxScore = score

                if depth == MAX_DEPTH:
                    bestMove = (playerStart, playerEnd)

            game_state.undoMove()

            if maxScore > alpha:
                alpha = maxScore
            if alpha >= beta:
                break
        if alpha >= beta:
            break

    return maxScore
