from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

import dask as dd
import pandas as pd
import sqlalchemy as sa

# if TYPE_CHECKING:
#     import sqlalchemy


def make_muscle_actions_query(
    session: sa.orm.Session = sa.Session(),
    like_dataframe: Optional[Union[pd.DataFrame, dd.DataFrame]] = None,
    experiment_ids: Optional[List[str]] = None,
    experiment_run_uids: Optional[List[str]] = None,
    experiment_run_instance_uids: Optional[List[str]] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    agent_uids: Optional[List[str]] = None,
    predicate=lambda query: query,
) -> sa.sql.expression.Selectable:
    """Creates a query for MIDAS-related Muscle actions

    When using ::`palaestrai.store.query.muscle_actions`, the query does not
    expand the JSON arrays-of-objects that are part of the following fields:

    * ::`palaestrai.store.database_model.MuscleAction.sensor_readings`
    * ::`palaestrai.store.database_model.MuscleAction.actuator_setpoints`
    * ::`palaestrai.store.database_model.MuscleAction.rewards`

    Because they are specialized, the general variant that lives in the
    ::`palaestrai.store.query` module cannot parse the JSON.
    This version expands the JSON fields.
    It is specific to running a simulation with MIDAS and the MIDAS powergrid
    module.

    The rest of the query, and its usage, remain unchanged.

    Parameters
    ----------
    session : sqlalchemy.orm.Session = Session()
        An session object created by ::`~Session()`.
    like_dataframe : Optional[Union[pd.DataFrame, dd.DataFrame]] = None
        Uses the given dataframe to construct a search predicate. Refer to the
        parameter documentation of ::`~experiments_and_runs_configurations`
    experiment_ids : Optional[List[str]]
        An interable containing experiment IDs to filter for
    experiment_run_uids :  Optional[List[str]]
        An interable containing experiment run UIDs to filter for
    experiment_run_instance_uids :  Optional[List[str]]
        An interable containing experiment run instance UIDs to filter for
    experiment_run_phase_uids :  Optional[List[str]]
        An interable containing experiment run phase UIDs to filter for
    agent_uids : Optional[List[str]] = None
        An interable containing agent UIDs to filter for
    predicate : Predicate = lambda query: query
        An additional predicate (cf. ::`sqlalchemy.sql.expression`) applied to
        the database query after all other predicates have been applied
    """
    pass


def muscle_actions(
    session: sa.orm.Session = sa.Session(),
    like_dataframe: Optional[Union[pd.DataFrame, dd.DataFrame]] = None,
    experiment_ids: Optional[List[str]] = None,
    experiment_run_uids: Optional[List[str]] = None,
    experiment_run_instance_uids: Optional[List[str]] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    agent_uids: Optional[List[str]] = None,
    predicate=lambda query: query,
) -> Union[pd.DataFrame, dd.DataFrame]:
    """All action data of a ::`~.Muscle`: readings, setpoints, and rewards

    Queries the store backend for muscle actions
    (cf. ::`palaestrai.store.query.muscle_actions`),
    but expands the resulting dataframe to contain singular colums for
    muscle actions and sensor readings.
    This is a more specific version of the general query in
    ::`palaestrai.store.query.muscle_actions`.

    Parameters
    ----------
    session : sqlalchemy.orm.Session = Session()
        An session object created by ::`palaestrai.store.Session()`.
    like_dataframe : Optional[Union[pd.DataFrame, dd.DataFrame]] = None
        Uses the given dataframe to construct a search predicate. Refer to the
        parameter documentation of ::`~experiments_and_runs_configurations`
    experiment_ids : Optional[List[str]]
        An interable containing experiment IDs to filter for
    experiment_run_uids :  Optional[List[str]]
        An interable containing experiment run UIDs to filter for
    experiment_run_instance_uids :  Optional[List[str]]
        An interable containing experiment run instance UIDs to filter for
    experiment_run_phase_uids :  Optional[List[str]]
        An interable containing experiment run phase UIDs to filter for
    agent_uids : Optional[List[str]] = None
        An interable containing agent UIDs to filter for
    predicate : Predicate = lambda query: query
        An additional predicate (cf. ::`sqlalchemy.sql.expression`) applied to
        the database query after all other predicates have been applied

    Returns
    -------
    Union[pd.DataFrame, dd.DataFrame]:
        This method returns a dask dataframe by default, unless the predicate
        adds a ``LIMIT`` or ``OFFSET`` clause.
        See the base method ::`palaestrai.store.query.muscle_actions` for
        details on the resulting dataframe columns.
        In addition, the sensor readings and actuator setpoints are
        expanded.
    """
    pass
