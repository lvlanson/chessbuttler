import matplotlib.pyplot as plt
import numpy as np
import tempfile

class Poll:

    def __init__(self):
        self.votes = {}
  
    def __is_format_valid(self, move: str):
        print(move)
        pieces  = ["T", "K", "D", "S", "L"]
        letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
        numbers = [str(n) for n in list(range(1,9))]
        is_piece_upper = move[0].isupper()

        i = -1
        if is_piece_upper:
          i = 0

        are_fields = move[1+i] in letters and move[4+i] in letters and move[2+i] in numbers and move[5+i] in numbers 
        is_minus   = move[3+i] == "-"
        is_piece   = (is_piece_upper and move[0] in pieces) or not is_piece_upper

        if is_piece and is_minus and are_fields:
            return True
        return False

    
    def add_vote(self, move, author):
        if self.__is_format_valid(move):
            self.votes[author] = move
            return True
        else: 
            return False

    def __evaluate(self):
        moves = set(self.votes.values())
        vote_counts = {move: 0 for move in moves}
        for move in self.votes.values():
            vote_counts[move] = vote_counts[move]+1
        return vote_counts

    def plot(self) -> str:
        """

        returns: filepath to plot
        """
        vote_counts  = self.__evaluate()
        moves = list()
        count = list()

        for move, c in vote_counts.items():
            moves.append(move)
            count.append(c)
        
        if len(moves) < 1:
          moves_index = []
        else:
          moves_index = np.arange(len(moves))
        plt.figure(figsize=(15,8))
        plt.rcParams.update({'font.size': 22})
        plt.barh(moves_index, count, align='center', alpha=0.5)
        plt.yticks(moves_index, moves)
        plt.xlabel("Anzahl Vorschläge")
        if len(count) > 0:
          plt.xticks(np.arange(max(count)+1))
        plt.title("Umfrage")
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        plt.savefig(tmp_file, dpi=300)
        return tmp_file

