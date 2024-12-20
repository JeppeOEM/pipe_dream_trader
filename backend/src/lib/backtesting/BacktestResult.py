# All the code is from an old project

import typing
import json

class BacktestResult:
    def __init__(self):
        self.pnl: float = 0.0
        self.max_dd: float = 0.0
        self.parameters: typing.Dict = dict()
        self.dominated_by: int = 0
        self.dominates: typing.List[int] = []
        self.rank: int = 0
        self.crowding_distance: float = 0.0

    # call class name to print repr
    def __repr__(self):
        return f"PNL = {round(self.pnl, 2)} Max. Drawdown = {round(self.max_dd, 2)} Parameters = {self.parameters} " \
               f"Rank = {self.rank} Crowding Distance = {self.crowding_distance}"

    def reset_results(self):
        self.dominated_by = 0
        self.dominates.clear()
        self.rank = 0
        self.crowding_distance = 0.0

    def return_result(self):
        pnl = round(self.pnl, 2)
        max_drawdown = round(self.max_dd, 2)
        params = self.parameters
        rank = self.rank
        crowding = self.crowding_distance
        data = {
            "pnl": pnl,
            "max_drawdown": max_drawdown,
            "params": params,
            "rank": rank,
            "crowding": crowding
        }
        return json.dumps(data)


# Unused


class StrategyModel:
    def __init__(self):
        self.pnl: float = 0.0
        self.max_dd: float = 0.0
        self.parameters: typing.Dict = dict()
        self.dominated_by: int = 0
        self.dominates: typing.List[int] = []
        self.rank: int = 0
        self.crowding_distance: float = 0.0

    def reset_results(self):
        self.dominated_by = 0
        self.dominates.clear()
        self.rank = 0
        self.crowding_distance = 0.0
