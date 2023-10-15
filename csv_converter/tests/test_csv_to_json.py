import copy
import textwrap

import pytest

from csv_converter.csv_to_json import CSVToJsonConverter


class TestCSVToJSONConverter:
    @pytest.fixture
    def csv_response(self):
        yield textwrap.dedent(
            """\
        Payment Date,Amount,Holding Currency,Refund Amount,Tax
        2023-09-23T00:00:00.000,3000.50,EUR,-150.25,25.75
        """
        )  # noqa B950

    @pytest.fixture
    def column_mapping(self):
        return {
            "Refund Amount": "refund_amounts",
            "Holding Currency": "currency",
            "Amount": "processed_amounts",
            "Payment Date": "date",
            "Tax": "current_period_breakdown.tax",
        }

    def test_csv_converter_success(self, column_mapping, csv_response):
        csv_to_json_converter = CSVToJsonConverter(
            csv_string=csv_response, column_mapping=column_mapping
        )
        json_objects = csv_to_json_converter.pandas_convert()
        assert len(json_objects) == 1

        expected_json = {
            "processed_amounts": 3000.50,
            "refund_amounts": -150.25,
            "currency": "EUR",
            "date": "2023-09-23T00:00:00.000",
            "current_period_breakdown": {"tax": 25.75},
        }
        assert json_objects[0] == expected_json

    @pytest.fixture
    def csv_response__missing_header(self):
        yield textwrap.dedent(
            """\
        Payment Date,Amount,Holding Currency,Refund Amount
        2023-09-22T00:00:00.000,2030.3944,USD,-200.48
        """
        )

    def test_csv_converter_fail__missing_header(
        self, column_mapping, csv_response__missing_header
    ):
        """
        An expected header for mapping is absent in the reponse
        """
        csv_to_json_converter = CSVToJsonConverter(
            csv_string=csv_response__missing_header,
            column_mapping=column_mapping,
        )

        with pytest.raises(KeyError) as exc:
            csv_to_json_converter.pandas_convert()

        assert str(exc.value) == "'Tax'"

    @pytest.fixture
    def csv_response__multi_response(self):
        yield textwrap.dedent(
            """\
        Payment Date,Amount,Holding Currency,Refund Amount,Gross Tax,Net Tax,Network Fee
        2023-09-22T00:00:00.000,2030.3944,USD,200.48,40.21,30.56,4.50
        2023-09-22T00:00:00.000,2100.55,USD,298.48,42.21,34.63,3.26
        """
        )  # noqa B950

    @pytest.fixture
    def column_mapping_multiple_responses(self, column_mapping):
        column_mapping = copy.deepcopy(column_mapping)
        column_mapping.pop("Tax")
        new_mappings = {
            "Gross Tax": "current_period_breakdown.gross_tax",
            "Net Tax": "current_period_breakdown.net_tax",
            "Network Fee": "current_period_breakdown.network_fees",
        }
        column_mapping.update(new_mappings)
        return column_mapping

    def test_csv_converter_success__multiple_response(
        self, column_mapping_multiple_responses, csv_response__multi_response
    ):
        csv_to_json_converter = CSVToJsonConverter(
            csv_string=csv_response__multi_response,
            column_mapping=column_mapping_multiple_responses,
        )
        json_objects = csv_to_json_converter.pandas_convert()
        assert len(json_objects) == 2

        expected_response = [
            {
                "processed_amounts": 2030.3944,
                "refund_amounts": 200.48,
                "currency": "USD",
                "date": "2023-09-22T00:00:00.000",
                "current_period_breakdown": {
                    "gross_tax": 40.21,
                    "net_tax": 30.56,
                    "network_fees": 4.50,
                },
            },
            {
                "processed_amounts": 2100.55,
                "refund_amounts": 298.48,
                "currency": "USD",
                "date": "2023-09-22T00:00:00.000",
                "current_period_breakdown": {
                    "gross_tax": 42.21,
                    "net_tax": 34.63,
                    "network_fees": 3.26,
                },
            },
        ]
        assert json_objects == expected_response

        # TODO: add csv module tests
