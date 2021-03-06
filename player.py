import random
import numpy as np

class DefaultPlayer:
    def __init__(self, index, name=None):
        self.index = index # should be int > 0
        self.name = name if name is not None else str(self.index)
        self.purchases = []

    def take_action(self, board, cur_money):
        if any([cur_money >= v for v in board.obj_cost.values()]):
            acts = self.buy_objects(board, cur_money)
            if not acts or acts[0][1] is None: # couldn't find empty pos
                return "draw", self.choose_curse_tile(board)
            return "buy", acts
        else:
            return "draw", self.choose_curse_tile(board)

    def choose_curse_amount(self, board, r, c):
        return max(1, board.tiles[r,c]-1)        

    def choose_curse_tile(self, board):
        options = board.valid_curse_inds()
        max_score = 0
        (r,c) = (0,0)
        for rc,cc,nts in options:
            inds = board.grids_touching_tile(rc,cc)
            v = len([1 for ro,co in inds if self.index == board.grid[ro,co]])
            if v > 0 and v*nts > max_score:
                r = rc
                c = cc
                max_score = v*nts
        if max_score == 0:
            top_opts = [(r,c,nts) for r,c,nts in options if nts > 1]
            if top_opts:
                r,c,nts = random.choice(top_opts)
            else:
                r,c,nts = random.choice(options)
        n = self.choose_curse_amount(board, r,c)
        return r,c,n

    def get_most_valuable_empty_inds(self, board, recent_acts):
        """
        should also account for whether a tile already has a hut nearby
        """
        vals = []
        max_val = 0
        max_ind = (0,0)
        backup_ind = []
        inds = board.valid_object_inds()
        recent_inds = [pos for nm,pos in recent_acts]
        for (i,j) in inds:
            if (i,j) in recent_inds:
                continue
            inds_t = board.tiles_touching_grid(i,j)
            v = np.sum([board.tiles[x,y] for (x,y) in inds_t])
            vals.append((i,j,v))
            if v > max_val:
                max_ind = (i,j)
                max_val = v
            else:
                backup_ind = (i,j)
        if max_val == 0:
            max_ind = backup_ind
            if len(backup_ind) == 0:
                return None
        return max_ind

    def choose_hut_pos(self, board, recent_acts):
        return self.get_most_valuable_empty_inds(board, recent_acts)

    def choose_station_pos(self, board, recent_acts):
        return self.get_most_valuable_empty_inds(board, recent_acts)

    def buy_object(self, board, money, cost_of_hut, cost_of_log, recent_acts):
        assert money >= min(cost_of_hut, cost_of_log)
        if money >= cost_of_log and money >= cost_of_hut:
            if not self.purchases: # buy a hut first
                name = "hut"
            elif "hut" == self.purchases[-1][0]:
                # if you bought a hut last, buy a station
                name = "station"
            else:
                name = "hut"
        else: # wait til you can choose
            return "hut", None

        pos = self.choose_station_pos(board, recent_acts)
        return name, pos

    def buy_objects(self, board, cur_money):
        cost_of_hut = board.obj_cost["hut"]
        cost_of_log = board.obj_cost["station"]
        objs = [] # (nm,(i,j)), ...
        while cur_money >= min(cost_of_hut, cost_of_log):
            name, pos = self.buy_object(board, cur_money, cost_of_hut, cost_of_log, objs)
            assert name in ["hut", "station"]
            if pos is None:
                return objs
            objs.append((name, pos))
            if name == "hut":
                cur_money -= cost_of_hut
            elif name == "station":
                cur_money -= cost_of_log
            self.purchases.append((name, pos))
        return objs

class SelfishPlayer(DefaultPlayer):
    def buy_object(self, board, money, cost_of_hut, cost_of_log, recent_acts):
        assert money >= min(cost_of_hut, cost_of_log)
        name = "station"
        if money >= cost_of_log:
            pos = self.choose_station_pos(board, recent_acts)
        else:
            # give up; wait another turn
            pos = None
        return name, pos

class SuperSelfishPlayer(SelfishPlayer):
    def choose_curse_amount(self, board, r, c):
        if board.tiles[r,c] == 2:
            # always choose the bonus
            return 2
        else:
            return max(1, board.tiles[r,c]-1)

class ReasonablePlayer(DefaultPlayer):
    def choose_curse_amount(self, board, r, c):
        if board.tiles[r,c] == 2:
            # always choose the bonus
            return 2
        else:
            return max(1, board.tiles[r,c]-1)

class CautiousPlayer(DefaultPlayer):
    def buy_object(self, board, money, cost_of_hut, cost_of_log, recent_acts):
        assert money >= min(cost_of_hut, cost_of_log)
        if money >= cost_of_log and money >= cost_of_hut:
            if not self.purchases: # buy a hut first
                name = "hut"
            elif "hut" == self.purchases[-1][0]:
                # if you bought a hut last, buy a station
                name = "station"
            else:
                name = "hut"
        elif money >= cost_of_log:
            # if you can only buy a station, buy a station
            name = "station"
        elif money >= cost_of_hut:
            # if you can only buy a hut, buy a hut
            name = "hut"

        pos = self.choose_station_pos(board, recent_acts)
        return name, pos

class GenerousPlayer(DefaultPlayer):
    def buy_object(self, board, money, cost_of_hut, cost_of_log, recent_acts):
        assert money >= min(cost_of_hut, cost_of_log)
        name = "hut"
        if money >= cost_of_hut:
            pos = self.choose_station_pos(board, recent_acts)
        else:
            # give up; wait another turn
            pos = None
        return name, pos
