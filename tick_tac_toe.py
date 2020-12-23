from copy import deepcopy
from random import choice

from exceptions import NotEmptySpotException


class Board(object):
    EMPTY = ""

    def __init__(self, board):
        self.values = deepcopy(board)

    def is_finished(self):
        for i in range(3):
            if len(set(self.values[i])) == 1 and self.values[i][0] != self.EMPTY:
                return True, self.values[i][0]

        for i in range(3):
            column = [self.values[0][i], self.values[1][i], self.values[2][i]]
            if len(set(column)) == 1 and column[0] != self.EMPTY:
                return True, column[0]

        diagonal = [self.values[0][0], self.values[1][1], self.values[2][2]]
        if len(set(diagonal)) == 1 and diagonal[0] != self.EMPTY:
            return True, diagonal[0]

        diagonal = [self.values[0][2], self.values[1][1], self.values[2][0]]
        if len(set(diagonal)) == 1 and diagonal[0] != self.EMPTY:
            return True, diagonal[0]

        for i in range(3):
            for j in range(3):
                if self.values[i][j] == self.EMPTY:
                    return False, None

        return True, None

    def update_board(self, move, player):
        if self.values[move[0]][move[1]] == self.EMPTY:
            self.values[move[0]][move[1]] = player.peace
        else:
            raise NotEmptySpotException

    def get_empty_spots(self):
        lst = []
        for i in range(3):
            for j in range(3):
                if self.values[i][j] == self.EMPTY:
                    lst.append([i, j])
        return lst

    def print(self):
        for i in range(3):
            for j in range(3):
                if j != 2:
                    print("\t" + self.values[i][j] + "\t|", end="")
                else:
                    print("\t" + self.values[i][j] + "\t")
            if i != 2:
                print("--------------------------")


class GameNode(object):
    MIN = "min"
    MAX = "max"

    def __init__(self, board_state, min_or_max):
        self.board = board_state
        self.min_or_max = min_or_max
        self.score = None

    def calculate_score(self, player):
        board_result, winner_peace = self.board.is_finished()
        if board_result:
            if winner_peace is None:
                self.score = 0
            elif winner_peace == player.peace:
                self.score = 1
            else:
                self.score = -1
        else:
            self.score = None


class Player(object):
    AI = "AI"
    HUMAN = "Human"
    X = "X"
    O = "O"
    AI_NAMES = ["Alex", "Abbey"]

    def __init__(self, player_type, player_name, player_peace):
        self.type = player_type
        self.name = player_name
        self.peace = player_peace

    def make_move(self, current_board, opponent):
        print("It's " + str(self) + "'s turn: ")
        if self.type == Player.HUMAN:
            move = input("Enter the move in the following format: row number, column number\n").split(',')
            move = list(map(lambda x: int(x) - 1, move))
            return move

        elif self.type == Player.AI:
            print("Thinking...")
            current_board_copy = Board(current_board.values)
            initial_node = GameNode(current_board_copy, GameNode.MAX)
            best_score, best_move = self.think(initial_node, opponent)
            return best_move

    def think(self, current_node, opponent, parent_best=None):
        best_move = []
        if current_node.min_or_max == GameNode.MIN:
            best_score = 2
        else:
            best_score = -2

        possible_moves = current_node.board.get_empty_spots()
        for move in possible_moves:
            new_board = Board(current_node.board.values)
            if current_node.min_or_max == GameNode.MAX:
                new_board.update_board(move, self)
                new_node = GameNode(new_board, GameNode.MIN)
                new_node.calculate_score(self)
                if new_node.score is not None and best_score <= new_node.score:
                    best_score = new_node.score
                    best_move = move

            else:
                new_board.update_board(move, opponent)
                new_node = GameNode(new_board, GameNode.MAX)
                new_node.calculate_score(self)
                if new_node.score is not None and best_score >= new_node.score:
                    best_score = new_node.score
                    best_move = move

            if new_node.score is None:
                possible_best_score, possible_best_move = self.think(new_node, opponent, best_score)

                if current_node.min_or_max == GameNode.MAX:
                    if best_score <= possible_best_score:
                        best_score = possible_best_score
                        best_move = move

                    if parent_best is not None and best_score >= parent_best:
                        break
                else:
                    if best_score >= possible_best_score:
                        best_score = possible_best_score
                        best_move = move

                    if parent_best is not None and best_score <= parent_best:
                        break

        return best_score, best_move

    def __str__(self):
        return self.name


class TicTacToe(object):
    def __init__(self, players):
        self.board = Board([[Board.EMPTY for _ in range(3)] for _ in range(3)])
        self.players = players
        self.winner_peace = None

    def run(self):
        current_player = choice(self.players)
        while not self.is_finished():
            self.board.print()
            move = current_player.make_move(self.board, self.players[1 - self.players.index(current_player)])
            try:
                self.board.update_board(move, current_player)
            except NotEmptySpotException as e:
                print(e.message)
                continue

            current_player = self.players[1 - self.players.index(current_player)]

        self.board.print()
        if self.winner_peace:
            if self.winner_peace == self.players[0].peace:
                print(str(self.players[0]) + " won the game")
            else:
                print(str(self.players[1]) + " won the game")
        else:
            print("Game finished to a draw")

    def is_finished(self):
        is_finished, self.winner_peace = self.board.is_finished()
        return is_finished


if __name__ == "__main__":
    play_again = True
    while play_again:
        o_player_name = input(
            "Enter the player name to play O: (type 'ai' if you want it to be Artificial Intelligence)\n")
        x_player_name = input(
            "Enter the player name to play X: (type 'ai' if you want it to be Artificial Intelligence)\n")

        if o_player_name == "ai":
            o_player = Player(Player.AI, choice(Player.AI_NAMES), Player.O)
        else:
            o_player = Player(Player.HUMAN, o_player_name, Player.O)

        if x_player_name == "ai":
            temp_names = deepcopy(Player.AI_NAMES)
            temp_names.remove(o_player.name)
            x_player = Player(Player.AI, choice(temp_names), Player.X)
        else:
            x_player = Player(Player.HUMAN, x_player_name, Player.X)

        game = TicTacToe([x_player, o_player])
        game.run()

        again = input("Wanna play again? (y/n) \n")
        play_again = again == "y"

    print("Thanks for playing")
