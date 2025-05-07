"""Additional views for the relational database"""

import sqlalchemy as sa


def make_muscle_actions_query() -> sa.sql.expression.Selectable:
    """Creates a view query for MIDAS-related Muscle actions

    Returns
    -------
    view : sa.sql.expression.Selectable
        An SQLalchemy selectable---i.e., a query---that will create the view.
    """
    pass


def create_midas_views(session):
    """Creates all MIDAS-related specialized views."""
    session.execute(make_muscle_actions_query())
