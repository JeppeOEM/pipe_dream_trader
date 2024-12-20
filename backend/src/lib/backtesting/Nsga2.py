import random
import typing
import copy
from main_app.models.BacktestResult import BacktestResult
from main_app.trading_engine.process_conds import create_conds
from main_app.trading_engine.optimize_backtest import optimize_backtest

from main_app.functions.utilities.backtesting_utils import STRAT_PARAMS, CONDITIONS, resample_timeframe
# import strategies.obv
# import strategies.ichimoku
# import strategies.support_resistance
from main_app.database.db import get_db
from main_app.data_download.Hdf5 import Hdf5Client


def set_contraints(bool: bool, params: typing.Dict) -> bool:
    print(params)
    if bool == True:
        return bool
    if bool == False:
        params['volume_BUY'] = max(params["volume_BUY"], params["RSI_15_BUY"])
        return bool



class Nsga2:
    """
    Non-Sorted genetic algorithm
    """
    def __init__(self, data, population_size: int, strategy_id: int, params_data):
        # self.exchange = exchange
        self.strategy_id = strategy_id
        # self.strategy = strategy
        # self.tf = tf
        # self.from_time = from_time
        # self.to_time = to_time
        self.population_size = population_size

        self.params_data = params_data

        self.population_params = []
        self.data = data
        self.db = get_db()

    def create_initial_population(self) -> typing.List[BacktestResult]:

        population = []

        while len(population) < self.population_size:
            backtest = BacktestResult()
            for p_code, p in self.params_data.items():
                if p["type"] == int:
                    backtest.parameters[p_code] = random.randint(
                        p["min"], p["max"])
                elif p["type"] == float:
                    backtest.parameters[p_code] = round(
                        random.uniform(p["min"], p["max"]), p["decimals"])

            if backtest not in population:
                population.append(backtest)
                self.population_params.append(backtest.parameters)

        return population

    def create_new_population(self, fronts: typing.List[typing.List[BacktestResult]]) -> typing.List[BacktestResult]:

        new_pop = []

        for front in fronts:
            if len(new_pop) + len(front) > self.population_size:
                max_individuals = self.population_size - len(new_pop)
                if max_individuals > 0:
                    new_pop += sorted(front, key=lambda x: getattr(x,
                                      "crowding_distance"))[-max_individuals:]
            else:
                new_pop += front

        return new_pop

    def create_offspring_population(self, population: typing.List[BacktestResult]) -> typing.List[BacktestResult]:

        offspring_pop = []

        while len(offspring_pop) != self.population_size:

            parents: typing.List[BacktestResult] = []

            for i in range(2):
                random_parents = random.sample(population, k=2)
                if random_parents[0].rank != random_parents[1].rank:
                    best_parent = min(
                        random_parents, key=lambda x: getattr(x, "rank"))
                else:
                    best_parent = max(
                        random_parents, key=lambda x: getattr(x, "crowding_distance"))

                parents.append(best_parent)

            new_child = BacktestResult()
            new_child.parameters = copy.copy(parents[0].parameters)

            # Crossover

            number_of_crossovers = random.randint(1, len(self.params_data))
            params_to_cross = random.sample(
                list(self.params_data.keys()), k=number_of_crossovers)

            for p in params_to_cross:
                new_child.parameters[p] = copy.copy(parents[1].parameters[p])

            # Mutation

            number_of_mutations = random.randint(0, len(self.params_data))
            params_to_change = random.sample(
                list(self.params_data.keys()), k=number_of_mutations)

            for p in params_to_change:
                mutations_strength = random.uniform(-2, 2)
                new_child.parameters[p] = self.params_data[p]["type"](
                    new_child.parameters[p] * (1 + mutations_strength))
                new_child.parameters[p] = max(
                    new_child.parameters[p], self.params_data[p]["min"])
                new_child.parameters[p] = min(
                    new_child.parameters[p], self.params_data[p]["max"])

                if self.params_data[p]["type"] == float:
                    new_child.parameters[p] = round(
                        new_child.parameters[p], self.params_data[p]["decimals"])

            new_child.parameters = self._params_constraints(
                new_child.parameters, self.strategy_id)

            if new_child.parameters not in self.population_params:
                offspring_pop.append(new_child)
                self.population_params.append(new_child.parameters)

        return offspring_pop

    def _params_constraints(self, params: typing.Dict, id: int) -> typing.Dict:

        bool = set_contraints(True, params)
        if bool == True:
            pass

        # elif self.strategy == "ichimoku":
        #     # makes sures KIJUN is largest
        #     params["kijun"] = max(params["kijun"], params["tenkan"])

        # elif self.strategy == "sma":
        #     params["slow_ma"] = max(params["slow_ma"], params["fast_ma"])

        # elif self.strategy == "psar":
        #     params["initial_acc"] = min(
        #         params["initial_acc"], params["max_acc"])
        #     params["acc_increment"] = min(
        #         params["acc_increment"], params["max_acc"] - params["initial_acc"])

        return params

    def crowding_distance(self, population: typing.List[BacktestResult]) -> typing.List[BacktestResult]:

        for objective in ["pnl", "drawdown"]:

            population = sorted(
                population, key=lambda x: getattr(x, objective))
            min_value = getattr(
                min(population, key=lambda x: getattr(x, objective)), objective)
            max_value = getattr(
                max(population, key=lambda x: getattr(x, objective)), objective)

            population[0].crowding_distance = float("inf")
            population[-1].crowding_distance = float("inf")

            for i in range(1, len(population) - 1):
                distance = getattr(
                    population[i + 1], objective) - getattr(population[i - 1], objective)
                if max_value - min_value != 0:
                    distance = distance / (max_value - min_value)
                population[i].crowding_distance += distance

        return population

    def non_dominated_sorting(self, population: typing.Dict[int, BacktestResult]) -> typing.List[typing.List[BacktestResult]]:

        fronts = []

        for id_1, indiv_1 in population.items():
            for id_2, indiv_2 in population.items():
                if indiv_1.pnl >= indiv_2.pnl and indiv_1.max_dd <= indiv_2.max_dd \
                        and (indiv_1.pnl > indiv_2.pnl or indiv_1.max_dd < indiv_2.max_dd):
                    indiv_1.dominates.append(id_2)
                elif indiv_2.pnl >= indiv_1.pnl and indiv_2.max_dd <= indiv_1.max_dd \
                        and (indiv_2.pnl > indiv_1.pnl or indiv_2.max_dd < indiv_1.max_dd):
                    indiv_1.dominated_by += 1

            if indiv_1.dominated_by == 0:
                if len(fronts) == 0:
                    fronts.append([])
                fronts[0].append(indiv_1)
                indiv_1.rank = 0

        i = 0

        while True:
            fronts.append([])

            for indiv_1 in fronts[i]:
                for indiv_2_id in indiv_1.dominates:
                    population[indiv_2_id].dominated_by -= 1
                    if population[indiv_2_id].dominated_by == 0:
                        fronts[i + 1].append(population[indiv_2_id])
                        population[indiv_2_id].rank = i + 1

            if len(fronts[i + 1]) > 0:
                i += 1
            else:
                del fronts[-1]
                break

        return fronts

    def evaluate_population(self, population: typing.List[BacktestResult], conditions: typing.List) -> typing.List[BacktestResult]:
        for bt in population:
            all_params = bt.parameters
            bt.pnl, bt.max_dd = optimize_backtest(
                self.data, all_params, conditions)

            if bt.pnl == 0:
                bt.pnl = -float("inf")
                bt.max_dd = float("inf")

        return population
