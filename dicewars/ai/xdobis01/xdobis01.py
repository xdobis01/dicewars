import random
import logging

from dicewars.ai.utils import possible_attacks, attack_succcess_probability, save_state
from dicewars.client.game.area import Area

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class AI:
    """Naive player agent

    This agent performs all possible moves in random order
    """

    def __init__(self, player_name, board, players_order):
        """
        Parameters
        ----------
        game : Game
        """
        self.player_name = player_name
        self.logger = logging.getLogger('xdobisAI')
        self.bestMoveStack = []

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):

        self.board = board
        # print("KEKET1")
        attacks = list(possible_attacks(board, self.player_name))
        if attacks and nb_moves_this_turn == 0:
              self.bestMoveStack = []
              self.UniformCostSearch(attacks)
        #     self.UCS(attacks)
        #
        # if self.bestMoves and not self.bestMoveStack:
        #     self.bestMoveStack = self.bestMoves[-1]
        # print("KEKET2")
        if self.bestMoveStack:
            # print("KEKET3")
            # print(self.bestMoveStack)
            source, target = self.bestMoveStack.pop()
            # print("KEKET4")
            # print(str(source) + "  xaxa " + str(target))
            return BattleCommand(source, target)
        else:
            self.logger.debug("No more possible turns.")
            # print(self.player_name)
            # print("KEKET5")
            return EndTurnCommand()

    def UniformCostSearch(self, attacks):

        sources = list(set([source for source, target in attacks]))

        OPEN = [[[source.get_name()], source.dice, 0] for source in sources]

        for i in range(5):
            path_values = [p[2] for p in OPEN]
            path = OPEN.pop(path_values.index(min(path_values)))
            path_nodes = path[0]
            path_dice = path[1]

            if path_dice == 1:
               continue

            path_cost = path[2]
            path_head = self.board.get_area(path_nodes[-1])
            for neighboor_id in path_head.get_adjacent_areas():

                neighboor = self.board.get_area(neighboor_id)
                if neighboor.get_owner_name() == self.player_name:
                    continue

                cost = self.NodeCost(neighboor, path_dice)
                new_path_nodes = path_nodes.copy()
                new_path_nodes.append(neighboor_id)

                OPEN.append([new_path_nodes, path_dice - 1, path_cost + cost])

        for i in range(round(len(OPEN)/2)):
            # print("HURU1")
            best_path = self.getPath(OPEN)
            # print("HURU2")
            # print(best_path)
            if best_path:
                path_of_attack = [(best_path[0][i], best_path[0][i + 1]) for i in range(len(best_path[0]) - 1)]
                path_of_attack.reverse()
                self.bestMoveStack.extend(path_of_attack)
            # print("HURU3")

    def getPath(self, OPEN):

        reject = True

        while(reject):

            set = True

            if not OPEN:
                return []
            path_values = [p[2] for p in OPEN]
            best_path = OPEN.pop(path_values.index(min(path_values)))
            if min(path_values) == 0 or best_path[2] > 35:
               continue

            sources = [source for source, target in self.bestMoveStack]
            targets = [target for source, target in self.bestMoveStack]

            for node in best_path[0]:
                if node in sources or node in targets:
                   set = False
                   break
            if set:
                reject = False

        return best_path



    def NodeCost(self, node, dice):

        # print("Here1")
        parent_cost = attack_succcess_probability(dice, node.dice) / 2
        # print("Here2")
        children_prob = []
        for neighboor_id in node.get_adjacent_areas():
            # print("A1")
            neighboor = self.board.get_area(neighboor_id)
            # print("A2")
            if neighboor.get_owner_name() == self.player_name:
                # print("Special1")
                continue


            child_dice = dice - 1
            if child_dice == 1:
               # print("Special2")
               break

            children_prob.append(attack_succcess_probability(dice - 1, neighboor.dice))
            # print("A3")
        # print("Here3")
        if len(children_prob) == 0:
            # print("B1")
            children_cost = 0.5
            # print("B2")
        else:
            # print("C1")
            children_cost = sum(children_prob)/len(children_prob) / 2
            # print("C2")
        # print("Here4")
        cost = 100 - 100 * (parent_cost + children_cost)
        # print("Here5")
        return cost

    def MySearch(self, attacks):

        self.bestMoveStack = []

        for source, target in attacks:
            prob = attack_succcess_probability(source.dice, target.dice)
            if prob < 0.7:
               continue
            else:
               for neighboor_id in target.neighbours:
                   neighboor = self.board.get_area(neighboor_id)
                   prob2 = []
                   for neighboor2_id in neighboor.neighbours:
                       neighboor2 = self.board.get_area(neighboor2_id)
                       prob2.append(attack_succcess_probability(source.dice - 1, neighboor2.dice + 1))
                       if prob2[-1] > 0.7:
                          break
                   if prob2[-1] > 0.7:
                      break
               if prob2[-1] > 0.7:
                   break
               self.bestMoveStack.append((source, target))







