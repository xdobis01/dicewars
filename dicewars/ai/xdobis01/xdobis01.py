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
        print("START OF AI {name} TURN".format(name=self.player_name))
        attacks = list(possible_attacks(board, self.player_name))
        if attacks and nb_moves_this_turn == 0:
              self.bestMoveStack = []
              print("STARTING UCS")
              self.UniformCostSearch(attacks)

        if self.bestMoveStack:
            print("ATTACK MOVE")
            print("BEST MOVE STACK CONTENTS")
            print(self.bestMoveStack)
            source, target = self.bestMoveStack.pop()
            print(str(source) + "  NODE attacks NODE " + str(target))
            return BattleCommand(source, target)
        else:
            self.logger.debug("No more possible turns.")
            print(self.player_name)
            print("END OF AI TURN")
            return EndTurnCommand()

    def UniformCostSearch(self, attacks):

        print("INIT UCS")
        sources = list(set([source for source, target in attacks]))

        print("CREATE OPEN queue AND FILL IT WITH PATHS INIT AS ATTACK SOURCES")
        OPEN = [[[source.get_name()], source.dice, 0] for source in sources]

        print("STARTING PATH EXPANSIONS")
        for i in range(attacks):
            print("POP PATH WITH MIN COST")
            path_values = [p[2] for p in OPEN]
            path = OPEN.pop(path_values.index(min(path_values)))
            path_dice = path[1]

            if path_dice == 1:
               print("IGNORE PATH, END NODE CANT ATTACK WITH 1 DICE")
               continue

            path_nodes = path[0]
            path_cost = path[2]

            print("GET PATH END NODE AREA")
            path_head = self.board.get_area(path_nodes[-1])

            print("STARTING PATH EXPANSION")
            for neighboor_id in path_head.get_adjacent_areas():

                neighboor = self.board.get_area(neighboor_id)
                if neighboor.get_owner_name() == self.player_name:
                    print("IGNORE NEIGHBOORS OWNED BY PLAYER")
                    continue

                print("CALCULATE COST NEIGHBOOR NODE COST")
                cost = self.NodeCost(neighboor, path_dice)

                print("CONCATENATE NEIGHBOOR TO OLD PATH")
                new_path_nodes = path_nodes.copy()
                new_path_nodes.append(neighboor_id)

                print("ADD NEW PATH, GENERATED FROM NEIGHBOOR")
                OPEN.append([new_path_nodes, path_dice - 1, path_cost + cost])

        print("ENDING PATH EXPANSIONS")

        print("PICK BEST PATHS AND TRANSFORM THEM INTO ATTACKS")
        for i in range(round(len(OPEN)/4)):

            print("START GETTING BEST PATH")
            best_path = self.getPath(OPEN)
            print("BEST PATH CONTENTS")
            print(best_path)

            if best_path:
                print("CREATE ATTACKS FROM PATH")
                path_of_attack = [(best_path[0][i], best_path[0][i + 1]) for i in range(len(best_path[0]) - 1)]
                path_of_attack.reverse()
                print("ADDING ATTACKS INTO BESTMOVESTACK")
                self.bestMoveStack.extend(path_of_attack)

    def getPath(self, OPEN):

        print("FIND CORRECT BEST PATH")
        rejectPath = True
        while(rejectPath):

            isPathCorrect = True
            if not OPEN:
                print("NO PATH AVAILABLE")
                return []

            print("POP PATH WITH MINIMUM COST")
            path_values = [p[2] for p in OPEN]
            best_path = OPEN.pop(path_values.index(min(path_values)))

            if min(path_values) == 0 or best_path[2] > 70:
               print("IGNORE PATH OF LENGTH 1 AND WITH HIGH COST")
               continue


            sources = [source for source, target in self.bestMoveStack]
            targets = [target for source, target in self.bestMoveStack]

            for node in best_path[0]:
                if node in sources or node in targets:
                   print("IGNORE BEST PATH, HER NODES ARE ALREADY IN BESTMOVESTACK")
                   isPathCorrect = False
                   break

            if isPathCorrect:
                print("BEST PATH HAS NO CONFLICT WITH STACK - IS CORRECT")
                rejectPath = False

        return best_path



    def NodeCost(self, node, dice):

        parent_cost = attack_succcess_probability(dice, node.dice) / 2
        print("CALCULATED ATTACK SUCCESS PROBABILITY")

        print("CALCULATE DEFENDER NEIGHBOURS ATTACK SUCCESS PROBABILITY")
        children_prob = []
        for neighboor_id in node.get_adjacent_areas():
            neighboor = self.board.get_area(neighboor_id)
            if neighboor.get_owner_name() == self.player_name:
                print("IGNORE NEIGHBOURS OWNED BY PLAYER")
                continue

            child_dice = dice - 1
            if child_dice == 1:
               print("CANT ATTACK WITH 1 DICE")
               break

            children_prob.append(attack_succcess_probability(dice - 1, neighboor.dice))


        if len(children_prob) == 0:
            print("NO NEIGHBOURS => CORNER NODE => SAVE NODE")
            children_cost = 0.5
        else:
            children_cost = sum(children_prob)/len(children_prob) / 2
            print("CALCULATED DEFENDER NEIGHBOURS ATTACK SUCCESS PROBABILITY")

        cost = 100 - 100 * (parent_cost + children_cost)
        print("CALCULATED NODE COST {cost}, RANGE 0-100".format(str(cost)))
        return cost

    def MySearch(self, attacks):
        # Ignore - primitive riesenie
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







