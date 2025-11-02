# type: ignore
"""
Data loader utility for Excel file processing.
Handles extraction and transformation of energy consumption data.
"""

import pandas as pd
from io import BytesIO


class EnergyDataLoader:
    """Utility class to load and process energy consumption data from Excel files."""

    @staticmethod
    def load_from_excel(
        file_content: bytes,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load energy data from Excel file content.

        Args:
            file_content: Bytes content of the Excel file

        Returns:
            Tuple of (generations, actual_consumptions, plant_consumer) DataFrames
        """
        excel_file = BytesIO(file_content)

        generations = pd.read_excel(
            excel_file,
            sheet_name="Generation",
            usecols=["Date", "Time", "Generation", "Gen_Consumption", "GMeter"],
        )

        name_mapping_gen = pd.read_excel(
            excel_file,
            sheet_name="Generation_Register",
            usecols=["GMeter", "Generator_Name"],
        )

        generations = generations.dropna(
            subset=["Date", "Time", "Generation", "Gen_Consumption", "GMeter"]
        ).copy()
        generations["Datetime"] = pd.to_datetime(
            generations["Date"].astype(str) + " " + generations["Time"].astype(str)
        )
        generations = generations.drop(columns=["Date", "Time"]).rename(
            columns={"GMeter": "Plant"}
        )

        plant_name_dict = dict(
            zip(name_mapping_gen["GMeter"], name_mapping_gen["Generator_Name"])
        )
        generations["Plant"] = generations["Plant"].map(plant_name_dict)
        generations = (
            generations.set_index("Datetime")
            .groupby("Plant")
            .resample("h", include_groups=False)["Generation", "Gen_Consumption"]
            .sum()
            .reset_index()
        )

        excel_file.seek(0)
        consumptions = pd.read_excel(
            excel_file,
            sheet_name="Load_Consumption",
            usecols=["Day", "Time", "Consumption", "CMeter"],
        )

        name_mapping_cons = pd.read_excel(
            excel_file,
            sheet_name="Load_Register",
            usecols=["CMeter", "Customer"],
        )

        consumptions = consumptions.dropna(
            subset=["Day", "Time", "Consumption", "CMeter"]
        ).copy()
        consumptions["Datetime"] = pd.to_datetime(
            consumptions["Day"].astype(str) + " " + consumptions["Time"].astype(str)
        )
        consumptions = consumptions.drop(columns=["Day", "Time"]).rename(
            columns={"CMeter": "Consumer"}
        )

        consumer_name_dict = dict(
            zip(name_mapping_cons["CMeter"], name_mapping_cons["Customer"])
        )
        consumptions["Consumer"] = consumptions["Consumer"].map(consumer_name_dict)
        consumptions = (
            consumptions.set_index("Datetime")
            .groupby("Consumer")
            .resample("h", include_groups=False)
            .sum()
            .reset_index()
        )

        excel_file.seek(0)
        plant_consumer = pd.read_excel(
            excel_file,
            sheet_name="Contract_Register",
            usecols=["Wholesale_Supplier", "Load", "EnergyShared%"],
        )
        plant_consumer.rename(
            columns={
                "Wholesale_Supplier": "Plant",
                "Load": "Consumer",
                "EnergyShared%": "Pct",
            },
            inplace=True,
        )

        return generations, consumptions, plant_consumer

    @staticmethod
    def validate_data(
        generations: pd.DataFrame,
        consumptions: pd.DataFrame,
        plant_consumer: pd.DataFrame,
    ) -> bool:
        """
        Validate that the loaded data has the required structure.

        Args:
            generations: Generation DataFrame
            consumptions: Consumption DataFrame
            plant_consumer: Plant-Consumer mapping DataFrame

        Returns:
            True if data is valid, False otherwise
        """
        try:
            assert "Plant" in generations.columns
            assert "Generation" in generations.columns
            assert "Datetime" in generations.columns

            assert "Consumer" in consumptions.columns
            assert "Consumption" in consumptions.columns
            assert "Datetime" in consumptions.columns

            assert "Plant" in plant_consumer.columns
            assert "Consumer" in plant_consumer.columns
            assert "Pct" in plant_consumer.columns

            return True
        except (AssertionError, KeyError):
            return False
