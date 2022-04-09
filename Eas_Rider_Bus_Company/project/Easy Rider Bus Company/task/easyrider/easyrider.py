from dataclasses import dataclass, field
import json
from collections import Counter
import inspect
import time
import re


@dataclass
class EzRider:
    """ class for sorting out the existing database of the "Easy Rider" bus company"""
    user_input: str
    is_required: list = field(default_factory=lambda: ["bus_id", "stop_id", "stop_name", "next_stop", "a_time"])
    # error_counter: dict
    fields: list = field(default_factory=lambda: ["bus_id", "stop_id", "stop_name", "next_stop", "stop_type", "a_time"])

    def _one_char_check(self, x, allowed_chars="SOF "):
        """ check is x is a single upper case letter"""
        try:
            is_string = type(x) == str
            single_letter = len(x) <= 1
            upper_case = x.upper() == x
            allowed_char = x in allowed_chars
            return is_string and single_letter and upper_case and allowed_char
        except TypeError:
            return False

    def _atime(self, x):
        """ check is x is a HH:MM """
        if type(x) != str:
            return False
        def is_hh_mm_time(time_string):
            try:
                time.strptime(time_string, '%H:%M')
            except ValueError:
                return False
            return (len(time_string) == 5)

        try:
            return is_hh_mm_time(x)
        except TypeError:
            return False


    def _stop_name(self, x):
        if type(x) != str: # check type
            return False
        template = re.compile(r"((([A-Z][a-z]*) )+(Boulevard|Street|Avenue|Road))$")
        reg_match = re.match(template, x)
        return bool(reg_match)

    def _stop_type(self, x):
        # check datatype
        if type(x) != str:
            return False
        # check formatd
        if "stop_type" in self.is_required:
            allowed_chars = "SOF"
        else:
            allowed_chars = "SOF "
        match = self._one_char_check(x, allowed_chars)
        return match


    def __post_init__(self):
        """ initialize instance variables"""
        self.parsed_input = json.loads(self.user_input)
        self.data_type_errors = dict.fromkeys(self.fields, 0)  # the error_counter dict
        self.error_counter = dict.fromkeys(self.fields, 0)  # the error_counter dict
        self.dtypes_list = {"bus_id": int,
                            "stop_id": int,
                            "stop_name": self._stop_name,
                            "next_stop": int,
                            "stop_type": self._stop_type,
                            "a_time": self._atime}

    def check_data_types(self, inp_field, inp_value) -> bool:
        """ return bool signaling if inp_value matches the required type"""

        checker = self.dtypes_list[inp_field]
        if inspect.ismethod(checker):
            match = checker(inp_value)
        else:
            match = checker == type(inp_value)
        if not match:
            self.data_type_errors[inp_field] += 1
        return match

    def check_if_filled(self, inp_field, inp_value) -> bool:
        empty = ""
        if inp_value == empty:
            self.error_counter[inp_field] += 1

    def total_report_errors_found(self) -> dict:

        # go over all blocks in the json file

        for data_point in self.parsed_input:

        # go over each field
            for inp_field, inp_value in data_point.items():

                match = self.check_data_types(inp_field, inp_value)
                # check is its filled (if required and matched)
                required = inp_field in self.is_required
                if required and match:
                    self.check_if_filled(inp_field, inp_value)

        self.total_errors_dict = Counter(self.data_type_errors) + Counter(self.error_counter)

    def get_tot_error(self) -> list:
        return sum(self.total_errors_dict.values())



def stage_one(user_input):
    ezrider = EzRider(user_input)
    ezrider.total_report_errors_found()
    tot_err = ezrider.get_tot_error()
    report = [f"Type and required field validation: {tot_err} errors"]
    for field in ezrider.fields:
        report += [field + ": " + f"{ezrider.total_errors_dict[field]}"]
    parsed_report = "\n".join(report)
    return parsed_report


def report_format(format_type, tot_err, ezrider):
    if format_type == "stage_two":
        report = [f"Format validation: {tot_err} errors"]
        for field in ["stop_name", "stop_type", "a_time"]:
            report += [field + ": " + f"{ezrider.total_errors_dict[field]}"]
        parsed_report = "\n".join(report)
    return parsed_report


def stage_two(user_input):
    ezrider = EzRider(user_input)
    ezrider.total_report_errors_found()
    tot_err = ezrider.get_tot_error()
    parsed_report = report_format("stage_two", tot_err, ezrider)
    return parsed_report


if __name__ == '__main__':
    report = stage_two(input())
    print(report)
