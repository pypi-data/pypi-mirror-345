"""A description of a bet in the dataframe."""


class Bet:
    """A way to define a bet."""

    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        odds_column: str,
        bookie_id_column: str,
        dt_column: str | None = None,
    ):
        self.odds_column = odds_column
        self.bookie_id_column = bookie_id_column
        self.dt_column = dt_column
