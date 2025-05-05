# Copyright (c) 2025 Dimetor GmbH.
#
# NOTICE: All information contained herein is, and remains the property
# of Dimetor GmbH and its suppliers, if any. The intellectual and technical
# concepts contained herein are proprietary to Dimetor GmbH and its
# suppliers and may be covered by European and Foreign Patents, patents
# in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from
# Dimetor GmbH.


import logging

import pandas as pd

from airbornerf_data_validator.constants import ErrorMessages
from airbornerf_data_validator.utils import show_duration

logger = logging.getLogger(__name__)


class Validator:
    def __init__(self, df, params):
        self.df = df
        self.params = params
        self.bad_rows = set()
        self.results = {'errors': {ErrorMessages.non_numeric: {},
                                   ErrorMessages.non_int: {},
                                   ErrorMessages.out_of_range: {},
                                   ErrorMessages.unexpected_value: {},
                                   ErrorMessages.empty_str: {},
                                   ErrorMessages.non_unique: {}
                                   },
                        'missing_parameters': [],
                        'ignored_parameters': [],
                        'duplicated_rows': [],
                        'stats': {'missing_parameters': 0,
                                  'errors': 0,
                                  'total_rows': df.shape[0],
                                  'bad_rows': 0,
                                  'duplicated_rows': 0,
                                  'good_rows': 0
                                  }
                        }

    def process_result(self, df_bad, error_msg):
        """
        Update result object with errors and statistics.

        :param df_bad: dataFrame with only one column which represents problematic parameter
        :param error_msg: str error message as per ErrorMessages
        :return:
        """
        if not df_bad.empty:
            logger.debug(f'STATUS: {error_msg} in column {df_bad.columns[0]}, number of bad rows {df_bad.shape[0]}')
            self.results['errors'][error_msg].update(df_bad.to_dict())
            self.bad_rows = self.bad_rows | set(df_bad.index.to_list())
            self.results['stats']['errors'] += df_bad.shape[0]
            self.results['stats']['bad_rows'] = len(self.bad_rows)

        self.results['stats']['good_rows'] = (self.results['stats']['total_rows'] - len(self.bad_rows)
                                              - self.results['stats']['duplicated_rows'])

    @show_duration(logger)
    def check_num_params(self, params_to_check, _type):
        """

        :param params_to_check: list of parameter names
        :param _type: str one of 'flt' or 'int', represents type of the parameters
        :return:
        """
        for param_name in params_to_check:
            # Determine errors due to non-numerical values, identify empty rows and keep only numeric data.
            df_buf = pd.to_numeric(self.df[param_name], errors='coerce').to_frame()
            df_non_numeric = self.df[[param_name]][df_buf[param_name].isna() & self.df[param_name].notna()]
            self.process_result(df_non_numeric, ErrorMessages.non_numeric)
            df_numeric = df_buf[~df_buf[param_name].isna()]

            if df_numeric.empty:
                logger.debug(f'No numeric values in {param_name}. Skipping values check.')
                continue

            if _type == 'int':
                # Check column values for floats, report and remove from set.
                df_non_integer = df_numeric[(df_numeric[param_name] - df_numeric[param_name].astype(int) != 0)]
                self.process_result(df_non_integer, ErrorMessages.non_int)

                if len(df_non_integer) == len(df_numeric):
                    logger.debug(f'All numbers in the {param_name} column are float values when integer values are '
                                 f'expected. The range / value check is therefore skipped for the entire column.')
                    continue
                df_numeric = df_numeric[~df_numeric.index.isin(df_non_integer.index)]

            enum_params = self.params[_type][param_name].get('enum')
            if enum_params:
                df_bad_value = df_numeric[~df_numeric[param_name].isin(enum_params)]
                self.process_result(df_bad_value, ErrorMessages.unexpected_value)
            else:
                low = self.params[_type][param_name]['low']
                high = self.params[_type][param_name]['high']
                df_bad_value = df_numeric[~df_numeric[param_name].between(low, high)]
                self.process_result(df_bad_value, ErrorMessages.out_of_range)

    @show_duration(logger)
    def check_str_params(self, params_to_check):
        """

        :param params_to_check: list of parameter names
        :return:
        """
        for param_name in params_to_check:
            # check if string is not empty
            df_empty_str = self.df[self.df[param_name].eq('') | self.df[param_name].str.isspace()][[param_name]]
            self.process_result(df_empty_str, ErrorMessages.empty_str)

            enums_params = self.params['str'][param_name]['enum']
            if enums_params:
                df_param = self.df[param_name].str.lower()
                df_bad_value = self.df[~df_param.isin(enums_params)][[param_name]]
                self.process_result(df_bad_value, ErrorMessages.unexpected_value)
            elif self.params['str'][param_name]['unique']:
                df_duplicated = self.df[self.df.duplicated(subset=[param_name], keep=False)][[param_name]]
                self.process_result(df_duplicated, ErrorMessages.non_unique)

    @show_duration(logger)
    def run_check(self):
        """
        Remove duplicated rows, process missing parameters and then group delivered parameters by their type and
        execute respective checks.
        :return: dict result with errors and statistics
        """
        duplicated_rows = self.df[self.df.duplicated()].index.to_list()
        self.df = self.df.drop(duplicated_rows)

        self.results['duplicated_rows'] = duplicated_rows
        self.results['stats']['duplicated_rows'] = len(duplicated_rows)

        delivered_params = set(self.df.columns)
        missing_params = self.params['names'] - delivered_params

        # based on "skip_if" conditions check determining columns to skip, see rules.py for explanation.
        to_skip = set()
        for param in self.params['names']:
            skip_if = self.params[param].get('skip_if', ())
            if not skip_if:
                continue
            # loop is logical "OR" - if one of the conditions is true then "param" can be skipped
            for required_params in skip_if:
                if len(required_params & delivered_params) == len(required_params):
                    to_skip.add(param)
                    break

        missing_params = missing_params - to_skip
        ignored_params = delivered_params - self.params['names']

        logger.debug(f'ignored parameters: {ignored_params or None}')
        logger.debug(f'missing parameters: {missing_params or None}')

        # Data sorting to have consistent results for easier analysis down the road.
        self.results['missing_parameters'].extend(sorted(missing_params))
        self.results['ignored_parameters'].extend(sorted(ignored_params))

        self.results['stats']['missing_parameters'] = len(self.results['missing_parameters'])

        present_params_int = sorted(self.params['int'].keys() & delivered_params)
        self.check_num_params(present_params_int, 'int')

        present_params_float = sorted(self.params['flt'].keys() & delivered_params)
        self.check_num_params(present_params_float, 'flt')

        present_params_str = sorted(self.params['str'].keys() & delivered_params)
        self.check_str_params(present_params_str)

        return self.results
