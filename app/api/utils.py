import datetime
from typing import Callable


def is_valid_date_format(date: str) -> bool:
    """validation string by python datetime lib"""
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return False
    return True


class Params:
    """This class is for query parameter of request"""

    def __init__(self, params: dict):
        self.params = params


class ParamsValidator(Params):
    """This class is used for validation of query parameters of request"""

    def check_if_params_passed(self, *args: str) -> bool:
        return len([key for key in self.params.keys() if key in args]) == len(args)

    def validate_values(self, func: Callable, *args: str) -> bool:
        for i in args:
            if not func(self.params.get(i, '')):
                return False
        return True
