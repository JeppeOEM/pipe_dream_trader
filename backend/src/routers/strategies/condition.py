import json
import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from ...dependencies import db_dependency, user_dependency
from ...lib.backtesting.Backtester import Backtester
from ...models import Strategies, StrategyConditions, StrategyIndicators
from ...schemas import (
    CreateBacktestRequest,
    CreateStrategyRequest,
    StrategySchema,
    UpdateStrategyRequest,
)
from ...utils.debugging.print_db_object import print_db_object
from ...utils.exceptions import handle_db_error, handle_not_found_error
from ..files.FileLoader import FileLoader
from .IndicatorLoader import IndicatorLoader

router = APIRouter(prefix="/strategy", tags=["strategy"])


@router.post("/{strategy_id}/condition", status_code=status.HTTP_201_CREATED)
async def add_strategy_condition(
    strategy_id: int,
    condition_data: dict,
    db: db_dependency,
    user: user_dependency,
):
    try:
        print(
            f"Request received to add strategy condition for strategy_id={strategy_id}"
        )
        print(f"Condition data: {condition_data}")

        fk_strategy_indicator_id_1 = condition_data.get("fk_strategy_indicator_id_1")
        fk_strategy_indicator_id_2 = condition_data.get("fk_strategy_indicator_id_2")
        settings = condition_data.get("settings", {})
        side = condition_data.get("side")

        print(
            f"Extracted values: fk_strategy_indicator_id_1={fk_strategy_indicator_id_1}, "
            f"fk_strategy_indicator_id_2={fk_strategy_indicator_id_2}, settings={settings}, side={side}"
        )

        strategy = (
            db.query(Strategies)
            .filter(Strategies.id == strategy_id)
            .filter(Strategies.fk_user_id == user["id"])
            .first()
        )
        print(f"Queried strategy: {strategy}")

        if not strategy:
            print(
                f"Strategy with id={strategy_id} not found or does not belong to user id={user['id']}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found or does not belong to user",
            )

        if side not in ["buy", "sell"]:
            print(f"Invalid 'side' value: {side}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid value for 'side'. Must be 'buy' or 'sell'.",
            )

        strategy_condition = StrategyConditions(
            fk_strategy_id=strategy_id,
            fk_strategy_indicator_id_1=fk_strategy_indicator_id_1,
            fk_strategy_indicator_id_2=fk_strategy_indicator_id_2,
            settings=settings,
            side=side,
        )
        print(f"Created StrategyCondition object: {strategy_condition}")

        db.add(strategy_condition)
        db.commit()
        db.refresh(strategy_condition)
        print(f"StrategyCondition successfully added with id={strategy_condition.id}")

        return {
            "message": "StrategyCondition successfully added",
            "strategy_condition": {
                "id": strategy_condition.id,
                "fk_strategy_id": strategy_condition.fk_strategy_id,
                "fk_strategy_indicator_id_1": strategy_condition.fk_strategy_indicator_id_1,
                "fk_strategy_indicator_id_2": strategy_condition.fk_strategy_indicator_id_2,
                "settings": strategy_condition.settings,
                "side": strategy_condition.side,
            },
        }

    except SQLAlchemyError as e:
        db.rollback()
        print(f"SQLAlchemy error while adding strategy condition: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )

    except Exception as e:
        db.rollback()
        print(f"Unexpected error while adding strategy condition: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


# TODO fix column
@router.put("/{strategy_id}/condition/{condition_id}", status_code=status.HTTP_200_OK)
async def update_strategy_condition(
    strategy_id: int,
    condition_id: int,
    condition_data: dict,
    db: db_dependency,
    user: user_dependency,
):
    """
    Update a strategy condition by condition_id.
    """
    try:
        print(
            f"Updating strategy condition with id={condition_id} for strategy_id={strategy_id}"
        )
        print(f"Condition data: {condition_data}")

        # Fetch the strategy condition
        strategy_condition = (
            db.query(StrategyConditions)
            .join(Strategies, StrategyConditions.fk_strategy_id == Strategies.id)
            .filter(
                StrategyConditions.id == condition_id,
                StrategyConditions.fk_strategy_id == strategy_id,
                Strategies.fk_user_id == user["id"],
            )
            .first()
        )
        if not strategy_condition:
            print(
                f"StrategyCondition with id={condition_id} not found for strategy_id={strategy_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy condition not found or does not belong to user",
            )

        for key, value in condition_data.items():
            if key == "settings" and isinstance(value, list):
                current_settings = strategy_condition.settings or []
                print(f"Current settings: {current_settings}")

                updated_settings = []

                for index, new_item in enumerate(value):
                    if isinstance(new_item, dict):
                        if index < len(current_settings):
                            # Update existing settings
                            old_item = current_settings[index]
                            updated_item = old_item.copy()

                            for sub_key, sub_value in new_item.items():
                                if sub_value is not None and sub_value != old_item.get(
                                    sub_key
                                ):
                                    updated_item[sub_key] = sub_value

                            updated_settings.append(updated_item)
                        else:
                            # Add new item if valid
                            if any(
                                sub_value is not None for sub_value in new_item.values()
                            ):
                                updated_settings.append(new_item)
                    else:
                        print(f"Invalid item at index {index}: {new_item}")

                strategy_condition.settings = updated_settings

            elif value is not None:
                setattr(strategy_condition, key, value)

        db.commit()
        db.refresh(strategy_condition)
        print(f"Updated StrategyCondition: {strategy_condition}")

        return {
            "message": "StrategyCondition successfully updated",
            "strategy_condition": {
                "id": strategy_condition.id,
                "fk_strategy_id": strategy_condition.fk_strategy_id,
                "fk_strategy_indicator_id_1": strategy_condition.fk_strategy_indicator_id_1,
                "fk_strategy_indicator_id_2": strategy_condition.fk_strategy_indicator_id_2,
                "settings": strategy_condition.settings,
                "side": strategy_condition.side,
            },
        }

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update strategy condition",
        )

    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred",
        )


@router.delete(
    "/{strategy_id}/condition/{condition_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_strategy_condition(
    strategy_id: int,
    condition_id: int,
    db: db_dependency,
    user: user_dependency,
):
    """
    Delete a strategy condition by condition_id.
    """
    try:
        print(
            f"Deleting strategy condition with id={condition_id} for strategy_id={strategy_id}"
        )

        # Fetch and validate the strategy condition
        strategy_condition = (
            db.query(StrategyConditions)
            .join(Strategies, StrategyConditions.fk_strategy_id == Strategies.id)
            .filter(
                StrategyConditions.id == condition_id,
                StrategyConditions.fk_strategy_id == strategy_id,
                Strategies.fk_user_id == user["id"],
            )
            .first()
        )
        if not strategy_condition:
            print(
                f"StrategyCondition with id={condition_id} not found for strategy_id={strategy_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy condition not found or does not belong to user",
            )

        db.delete(strategy_condition)
        db.commit()
        print(f"Deleted StrategyCondition with id={condition_id}")

        return {"message": "StrategyCondition successfully deleted"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete strategy condition",
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred",
        )


@router.get("/{strategy_id}/condition/{condition_id}")
async def get_strategy_conditions(
    strategy_id: int,
    condition_id: int,
    db: db_dependency,
    user: user_dependency,
):
    try:
        # Query the database for the specific StrategyCondition
        strategy_condition = (
            db.query(StrategyConditions)
            .filter(
                StrategyConditions.strategy_id == strategy_id,
                StrategyConditions.condition_id == condition_id,
            )
            .first()
        )

        if strategy_condition is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"StrategyCondition with strategy_id={strategy_id} and condition_id={condition_id} not found",
            )

        # If found, return the StrategyCondition object
        return strategy_condition

    except SQLAlchemyError as e:
        # Handle any database-related errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch strategy conditions from the database",
        )

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred",
        )


# TODO: fix errors codes
@router.get("/{strategy_id}/condition", status_code=status.HTTP_200_OK)
async def get_all_strategy_conditions(
    strategy_id: int,
    db: db_dependency,
    user: user_dependency,
):
    """
    Retrieve all strategy conditions for a given strategy_id.
    """
    try:
        print(f"Fetching all strategy conditions for strategy_id={strategy_id}")

        strategy = (
            db.query(Strategies)
            .filter(Strategies.id == strategy_id, Strategies.fk_user_id == user["id"])
            .first()
        )
        if not strategy:
            print(
                f"Strategy with id={strategy_id} not found or does not belong to user"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found or does not belong to user",
            )

        strategy_conditions = (
            db.query(StrategyConditions)
            .filter(StrategyConditions.fk_strategy_id == strategy_id)
            .all()
        )
        print(f"Fetched {len(strategy_conditions)} StrategyConditions")

        return [
            {
                "id": sc.id,
                "fk_strategy_id": sc.fk_strategy_id,
                "fk_strategy_indicator_id_1": sc.fk_strategy_indicator_id_1,
                "fk_strategy_indicator_id_2": sc.fk_strategy_indicator_id_2,
                "settings": sc.settings,
                "side": sc.side,
            }
            for sc in strategy_conditions
        ]

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch strategy conditions",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred",
        )


@router.post("/{strategy_id}/backtest", status_code=status.HTTP_200_OK)
async def backtest(
    strategy_id: int,
    db: db_dependency,
    user: user_dependency,
    backtest_request: CreateBacktestRequest,
):
    try:
        # Fetch the strategy model
        strategyModel = (
            db.query(Strategies).filter(Strategies.id == strategy_id).first()
        )

        if not strategyModel:
            raise HTTPException(status_code=404, detail="Strategy not found")

        if strategyModel.file:
            # Process the file data
            path = strategyModel.file.path
            file_loader = FileLoader(path)
            file_loader.load_data()

            all_indicator_settings = [
                ind.settings
                for ind in strategyModel.strategy_indicators
                if ind.settings is not None
            ]

            indicator_loader = IndicatorLoader(file_loader.df, all_indicator_settings)
            indicator_loader.load_indicators()

        # Parse the stringified arrays
        buy_conditions = json.loads(backtest_request.buy_conditions)
        sell_conditions = json.loads(backtest_request.sell_conditions)
        print(buy_conditions)
        print(sell_conditions)

        # buy = {"buy": [["df.SMA_10 < 1"]]}
        # sell = {"sell": [["df.SMA_10 > 1.1"]]}

        buy = {"buy": [["SMA_10 < 1"]]}
        sell = {"sell": [["SMA_10 > 1.1"]]}

        # Loop over buy and sell conditions
        buy_results = [f"Processed buy condition: {cond}" for cond in buy_conditions]
        sell_results = [f"Processed sell condition: {cond}" for cond in sell_conditions]

        # Run the backtest
        backtest = Backtester(indicator_loader.df)
        buy_eval_string = backtest.build_conditions("buy", buy_conditions)
        sell_eval_string = backtest.build_conditions("sell", sell_conditions)

        # buy_eval_string = backtest.build_conditions("buy", buy['buy'])
        # sell_eval_string = backtest.build_conditions("sell", sell['sell'])
        result = backtest.run()
        print(result)

        return {
            "buy_results": buy_results,
            "sell_results": sell_results,
            "strategy_id": strategy_id,
            "user": user,
            "backtest_result": result,
        }

    except Exception as e:
        handle_db_error(e, "Unexpected error occurred while processing the backtest")