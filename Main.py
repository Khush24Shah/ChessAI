# Main driver file. Handling user-input and displaying the current game-state.

import pygame as p
from Engine import *
from AI import *

HEIGHT = WIDTH = 512
DIMENSIONS = 8
SQUARE_SIZE = HEIGHT // DIMENSIONS

MAX_FPS = 20

IMAGES = {}


def loadImages():
    pieces = ("wK", "wQ", "wR", "wB", "wN", "wP", "bK", "bQ", "bR", "bB", "bN", "bP")
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"Images/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))
    # An image can be accessed by using IMAGES[<name of the piece>]


def draw_game_state(screen, game_state, squareSelected, validMoves, last):
    """Responsible for all the graphics within the current game state."""

    draw_board(screen)  # Draw the boxes of the board

    highlightSquares(screen, squareSelected, validMoves, game_state.checks, game_state.whiteKing if game_state.whiteToMove else game_state.blackKing, last)  # Add piece highlighting and/or legal-move suggestions

    draw_pieces(screen, game_state.board, game_state.whitePieces + game_state.blackPieces)  # Draw the pieces of the board


def draw_board(screen):
    """Draw the squares on the board."""

    colors = (p.Color("light gray"), p.Color("dark grey"))

    for row in range(DIMENSIONS):
        for col in range(DIMENSIONS):
            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board, pieces):
    """Draw the pieces on the board using the current game-state board."""

    for row, col in pieces:
        screen.blit(IMAGES[board[row][col]], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlightSquares(screen, squareSelected, validMoves, checks, king, last):
    s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
    s.set_alpha(127)

    if last:
        s.fill(p.Color("green"))
        for r, c in last:
            screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))

    if squareSelected is not None:
        r, c = squareSelected

        s.fill(p.Color("purple"))

        screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))

        s.fill(p.Color("blue"))
        for move in validMoves:
            screen.blit(s, (move[1] * SQUARE_SIZE, move[0] * SQUARE_SIZE))

    if checks:
        s.fill(p.Color("red"))
        screen.blit(s, (king[1] * SQUARE_SIZE, king[0] * SQUARE_SIZE))

        for direction, piece in checks.items():
            s.fill(p.Color("yellow"))
            row, col = king[0] + direction[0], king[1] + direction[1]

            while (row, col) != piece:
                screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                row += direction[0]
                col += direction[1]

            s.set_alpha(255)
            s.fill(p.Color("orange"))
            screen.blit(s, (piece[1] * SQUARE_SIZE, piece[0] * SQUARE_SIZE))


def drawText(screen, text):
    font = p.font.SysFont("inkfree", 32, False, False)
    textObject = font.render(text, 0, p.Color("Red"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


if __name__ == "__main__":
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    game_state = Game()
    game_state.getValidMoves()

    loadImages()

    prevSquareSelected = None  # Keeps the track of the last click of the user: (row, col)
    squareSelected = None

    moveMade = False

    playerWhite = True
    playerBlack = False

    human = (game_state.whiteToMove and playerWhite) or (not game_state.whiteToMove and playerBlack)

    gameOver = False

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                break

            elif e.type == p.MOUSEBUTTONDOWN:
                if human and not gameOver:
                    location = p.mouse.get_pos()  # (x, y) location of the mouse

                    squareSelected = (location[1] // SQUARE_SIZE, location[0] // SQUARE_SIZE)  # Determine which box of the board is selected
                    print(squareSelected)

                    if prevSquareSelected is not None and prevSquareSelected == squareSelected:  # If the player clicked the same square twice
                        prevSquareSelected = None  # deselect

                    else:
                        if prevSquareSelected is None:
                            print(tuple(game_state.validMoves.keys()))
                            if squareSelected in tuple(game_state.validMoves.keys()):
                                prevSquareSelected = squareSelected

                        else:
                            if squareSelected in game_state.validMoves.get(prevSquareSelected, []):
                                move = Move(prevSquareSelected, squareSelected, game_state.board)
                                game_state.makeMove(move)
                                moveMade = True
                                prevSquareSelected = None
                            elif squareSelected in tuple(game_state.validMoves.keys()):
                                prevSquareSelected = squareSelected
                            else:
                                prevSquareSelected = None

            elif e.type == p.KEYDOWN:
                if e.key == p.K_BACKSPACE:
                    game_state.undoMove()
                    if not (playerWhite and playerBlack):
                        game_state.undoMove()
                    moveMade = True
                    gameOver = False

                elif e.key == p.K_ESCAPE:
                    running = False
                    break

        if not human and not gameOver:
            start, end = findAIMove(game_state)
            game_state.makeMove(Move(start, end, game_state.board))
            moveMade = True

        if moveMade:
            game_state.getValidMoves()
            moveMade = False

            human = (game_state.whiteToMove and playerWhite) or (not game_state.whiteToMove and playerBlack)

        last = () if not game_state.moveLog else game_state.moveLog[-1]

        if last:
            last = ((last.startRow, last.startCol), (last.endRow, last.endCol))

        draw_game_state(screen, game_state, prevSquareSelected, game_state.validMoves.get(squareSelected, []), last)

        if game_state.checkmate:
            gameOver = True
            text = "Black wins by CHECKMATE" if game_state.whiteToMove else "White wins by CHECKMATE"
            drawText(screen, text)
        elif game_state.stalemate:
            gameOver = True
            drawText(screen, "Draw by STALEMATE")

        clock.tick(MAX_FPS)
        p.display.flip()