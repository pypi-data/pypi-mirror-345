# SPDX-FileCopyrightText: 2025 Sofía Aritz <sofiaritz@fsfe.org>
#
# SPDX-License-Identifier: AGPL-3.0-only

from mp_scrape_core import PipelineProcess, ModuleDefinition, ModuleDescription, ModuleArgument, ModuleMaintainer
import pandas as pd

import logging

class FilterProcess(PipelineProcess):
    def __init__(self, check_col: str, expect: str):
        """
        Filter rows based on the value of a column

        :param str check_col: (Column to check) Column to check.
        :param str expect: (Expected value) Expected value of the column. If this value matches the value of the column on a given row, it will be kept.
        """
        self.check_col = check_col
        self.expect = expect

    @staticmethod
    def metadata() -> ModuleDefinition:
        return ModuleDefinition({
            "name": "Filter",
            "identifier": "filter",
            "description": ModuleDescription.from_init(FilterProcess.__init__),
            "arguments": ModuleArgument.list_from_init(FilterProcess.__init__),
            "maintainers": [
                ModuleMaintainer({
                    "name": "Free Software Foundation Europe",
                    "email": "mp-scrape@fsfe.org"
                }),
                ModuleMaintainer({
                    "name": "Sofía Aritz",
                    "email": "sofiaritz@fsfe.org"
                }),
            ],
        })
    
    async def pipeline(self, logger: logging.Logger, identifier: str, data: pd.DataFrame) -> pd.DataFrame:
        if self.check_col not in data.columns:
            raise ValueError(f"Column '{self.check_col}' not found in '{self.identifier}' dataset")
        
        return data[
            data[self.check_col] == self.expect
        ]