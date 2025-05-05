from pathlib import Path

import polars as pl


class PeriodicTable:
    def __init__(self) -> None:
        self.pse: pl.DataFrame = pl.read_json(
            Path(__file__).parent / "periodic_table.json"
        )

    def get_element(self, symbol: str) -> dict:
        element_df = self.pse.filter(pl.col("symbol") == symbol)
        if element_df.is_empty():
            raise ValueError(f"No element with symbol '{symbol}' found!")
        return element_df.to_dict(as_series=False)

    def get_symbol_by_id(self, atomic_number: int) -> str:
        element_df = self.pse.filter(pl.col("atomic_number") == atomic_number)
        if element_df.is_empty():
            raise ValueError(f"No element with atomic number '{atomic_number}' found!")
        return element_df["symbol"].item()


PERIODIC_TABLE = PeriodicTable()
