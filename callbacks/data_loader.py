# type: ignore
"""
Data loader utility for Excel file processing.
Handles extraction and transformation of energy consumption data.
"""

import pandas as pd

from dataclasses import dataclass
from io import BytesIO


@dataclass(frozen=True, slots=True)
class UploadedData:
    generations: pd.DataFrame
    consumptions: pd.DataFrame
    plant_consumer: pd.DataFrame


class EnergyDataLoader:
    """Utility class to load and process energy consumption data from Excel files."""

    @staticmethod
    def load_from_excel(file_content: bytes) -> UploadedData:
        """
        Load energy data from Excel file content.

        Args:
            file_content: Bytes content of the Excel file

        Returns:
            UploadedData
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
            usecols=["GMeter", "Generator_Name", "Wholesale_Supplier", "Gen_Mix"],
        )

        generations = generations.dropna(
            subset=["Date", "Time", "Generation", "Gen_Consumption", "GMeter"]
        ).copy()
        generations["Datetime"] = pd.to_datetime(
            generations["Date"].astype(str) + " " + generations["Time"].astype(str)
        )
        generations = generations.drop(columns=["Date", "Time"])

        plant_name_dict = dict(
            zip(name_mapping_gen["GMeter"], name_mapping_gen["Generator_Name"])
        )
        plant_wholesale_supplier_dict = dict(
            zip(name_mapping_gen["GMeter"], name_mapping_gen["Wholesale_Supplier"])
        )
        plant_gen_mix_dict = dict(
            zip(name_mapping_gen["GMeter"], name_mapping_gen["Gen_Mix"])
        )
        generations["Wholesale_Supplier"] = generations["GMeter"].map(
            plant_wholesale_supplier_dict
        )
        generations["Plant"] = generations["GMeter"].map(plant_name_dict)
        generations["Gen_Mix"] = generations["GMeter"].map(plant_gen_mix_dict)
        generations.drop(columns=["GMeter"], inplace=True)
        generations = (
            generations.set_index("Datetime")
            .groupby(["Plant", "Wholesale_Supplier", "Gen_Mix"])
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

        generations[["Generation", "Gen_Consumption"]] /= 1_000_000
        consumptions["Consumption"] /= 1_000_000

        return UploadedData(
            generations=generations,
            consumptions=consumptions,
            plant_consumer=plant_consumer,
        )

    @staticmethod
    def validate_data(uploaded_data: UploadedData) -> bool:
        """
        Validate that the loaded data has the required structure.

        Args:
            uploaded_data: UploadedData

        Returns:
            True if data is valid, False otherwise
        """
        try:
            assert "Plant" in uploaded_data.generations.columns
            assert "Generation" in uploaded_data.generations.columns
            assert "Datetime" in uploaded_data.generations.columns

            assert "Consumer" in uploaded_data.consumptions.columns
            assert "Consumption" in uploaded_data.consumptions.columns
            assert "Datetime" in uploaded_data.consumptions.columns

            assert "Plant" in uploaded_data.plant_consumer.columns
            assert "Consumer" in uploaded_data.plant_consumer.columns
            assert "Pct" in uploaded_data.plant_consumer.columns

            return True
        except (AssertionError, KeyError):
            return False
