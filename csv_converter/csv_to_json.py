import csv
from io import StringIO
from typing import Any

import pandas as pd

from utils.timer import timer_decorator


class CSVToJsonConverter:
    def __init__(self, csv_string: str, column_mapping: dict[str, Any]):
        self.csv_string = csv_string
        self.column_mapping = column_mapping
        self.string_reader = StringIO(self.csv_string)

    @timer_decorator
    def pandas_convert(self) -> list[dict[str, Any]]:
        """
        Convert CSV data to a list of JSON objects based on the provided column mapping.
        This method parses the CSV data and maps each column to a corresponding field in
        the JSON objects according to the provided column mapping.
        If a field is specified to be nested using dot notation (e.g., 'nested.field'),
        it will create a nested structure in the resulting JSON object.

        uses pandas library to perform the conversion
        """
        # Read the CSV data into a Pandas DataFrame
        df = pd.read_csv(self.string_reader)

        json_objects = []
        for _, row in df.iterrows():
            json_obj = {}
            for csv_column, json_field in self.column_mapping.items():
                if "." in json_field:
                    json_field_parts = json_field.split(".")
                    nested_field_name = json_field_parts[0]
                    if nested_field_name not in json_obj:
                        json_obj[nested_field_name] = {}
                    # assuming we're only going one level deep
                    json_obj[nested_field_name][json_field_parts[-1]] = row[
                        csv_column
                    ]
                else:
                    json_obj[json_field] = row[csv_column]
            json_objects.append(json_obj)

        return json_objects

    @staticmethod
    def _parse_nested_field(
        field_name: str, field_value: Any
    ) -> dict[str, Any]:
        """
        Parse a field as a nested object.
        This function takes a field name and its corresponding value and wraps them
        in a dictionary to represent a nested object.
        :param field_name: The name of the field to be used as the key.
        :param field_value: The value associated with the field.
        :return: A dictionary representing the nested field.
        """
        nested_obj = {field_name: field_value}
        return nested_obj

    @timer_decorator
    def csv_module_convert(self) -> list[dict[str, Any]]:
        """
        Convert CSV data to a list of JSON objects based on the provided column mapping.
        This method parses the CSV data and maps each column to a corresponding field in
        the JSON objects according to the provided column mapping.
        If a field is specified to be nested using dot notation (e.g., 'nested.field'),
        it will create a nested structure in the resulting JSON object.

        uses the csv module from the standard library to perform the conversion
        """
        csv_data = csv.DictReader(self.string_reader)
        json_objects = []

        for row in csv_data:
            json_obj = {}
            for csv_column, json_field in self.column_mapping.items():
                if "." in json_field:
                    json_field_parts = json_field.split(".")
                    nested_field_name = json_field_parts[0]
                    if nested_field_name not in json_obj:
                        json_obj[nested_field_name] = {}
                    # assuming we're only going one level deep
                    nested_value = self._parse_nested_field(
                        field_name=json_field_parts[-1],
                        field_value=row[csv_column],
                    )
                    json_obj[nested_field_name].update(nested_value)
                else:
                    json_obj[json_field] = row[csv_column]
            json_objects.append(json_obj)
        return json_objects


# run individual functions
# CSVToJsonConverter().csv_module_convert()
# CSVToJsonConverter().pandas_convert()
