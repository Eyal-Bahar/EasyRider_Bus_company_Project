from dataclasses import dataclass, field
import json
from collections import Counter, defaultdict
import inspect
import time
import re
import itertools


@dataclass
class EzRider:
    """ class for sorting out the existing database of the "Easy Rider" bus company"""
    user_input: str
    #is_required: list = field(default_factory=lambda: ["bus_id", "stop_id", "stop_name", "next_stop", "a_time"])

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
        # all fields
        self.fields = ["bus_id", "stop_id", "stop_name", "next_stop", "stop_type", "a_time"]

        # required fields to fill in
        self.is_required = ["bus_id", "stop_id", "stop_name", "next_stop", "a_time"]

        # pasring the input
        self.parsed_input = json.loads(self.user_input)

        # list of data types and formats
        self.dtypes_list = {"bus_id": int,
                            "stop_id": int,
                            "stop_name": self._stop_name,
                            "next_stop": int,
                            "stop_type": self._stop_type,
                            "a_time": self._atime}

        # initialize dictionaries for keeping track of errors
        self.data_type_errors = dict.fromkeys(self.fields, 0)  # the error_counter dict
        self.error_counter = dict.fromkeys(self.fields, 0)  # the error_counter dict

    def check_data_types(self, inp_field, inp_value) -> bool:
        """ return bool signaling if inp_value matches the required type"""

        checker = self.dtypes_list[inp_field]
        if inspect.ismethod(checker):
            match = checker(inp_value)
        else:
            match = checker == type(inp_value)
        return match

    def check_if_filled(self, inp_field, inp_value) -> bool:
        empty = ""
        if inp_value == empty:
            return False
        return True

    def total_report_errors_found(self) -> dict:

        # go over all blocks in the json file

        for data_point in self.parsed_input:

        # go over each field
            for inp_field, inp_value in data_point.items():

                match = self.check_data_types(inp_field, inp_value)
                # check is its filled (if required and matched)
                if not match:
                    self.data_type_errors[inp_field] += 1

                required = inp_field in self.is_required
                #  check if its filled - if it is required
                if required and match:
                    is_filled = self.check_if_filled(inp_field, inp_value)
                    if not is_filled:
                        self.error_counter[inp_field] += 1

        self.total_errors_dict = Counter(self.data_type_errors) + Counter(self.error_counter)

    def get_tot_error(self) -> list:
        return sum(self.total_errors_dict.values())

    def stops_counter(self, stand_alone=False):
        if stand_alone:
            self.stops_report = defaultdict(lambda: 0)
            for data_point in self.parsed_input:
                bus_id_instance = data_point["bus_id"]

                # check if its filled according to format
                match = self.check_data_types("bus_id", bus_id_instance)
                required = "bus_id" in self.is_required
                if not (required and match):
                    continue
                else:
                    is_filled = self.check_if_filled("bus_id", bus_id_instance)

                if is_filled:
                    self.stops_report[bus_id_instance] += 1
            return dict(self.stops_report)
        else:
            pass #Todo

    def unqiue_start_final_stops(self):
        self.start_stops
        self.final_stops
        for data_point in self.parsed_input:

            stop_type = data_point["stop_type"]
            # check if its filled according to format
            match = self.check_data_types("stop_type", stop_type)
            required = "bus_id" in self.is_required
            if not (required and match):
                continue
            else:
                is_filled = self.check_if_filled("stop_type", stop_type)

            if is_filled:
                stop_type

    def add_stop_name(self, data_point):
        stop_name = data_point["stop_name"]
        # check if its filled according to format
        match = self.check_data_types("stop_name", stop_name)
        required = "stop_name" in self.is_required
        if (required and match):
            is_filled = self.check_if_filled("stop_name", stop_name)
        else:
            raise (NameError, "format or requirement not fulfilled")
        bus_id = data_point["bus_id"]
        match = self.check_data_types("bus_id", bus_id)
        required = "stop_name" in self.is_required
        if (required and match):
            is_filled = self.check_if_filled("bus_id", bus_id)
        else:
            raise (NameError, "format or requirement not fulfilled")
        self.all_stops[data_point["bus_id"]] += stop_name


    def find_transfer_stops(self, all_stops):
        pass

    def stops_sepcifier(self):
        # checks if all bus's have unique start and final stops. if not return and instance of the failing bus line
        if not self.unqiue_start_final_stops(): # TODO
            return
        # map routes
        self.stops_sepcifier_report = defaultdict(lambda: 0)
        for data_point in self.parsed_input:
            self.add_stop_name(data_point)

        self.find_transfer_stops(self.all_stops) # TODO
        starts_list = list(set(self.start_stops()))
        finals_list = list(set(self.final_stops()))
        transfer_set = set()
        for bus_a, bus_b in itertools.combinations(self.all_stops.keys(), 2):
            a_b_shared_stops = list(bus_a.intersect(bus_b))
            transfer_set.update(a_b_shared_stops)
        transfer_list = list(transfer_set)
        self.stops_sepcifier_report = {"S": starts_list,"T": transfer_list,"F": finals_list}




def report_format(format_type, ezrider, stops_report=0, tot_err=0, stops_sepcifier_report=0):
    if format_type == "stage_four":
        # check if report stopped becuase of a bus line information miss
        if type(stops_sepcifier_report) == int:
            print(f"There is no start or end stop for the line: {stops_sepcifier_report}")

        report = []
        headlines = {"S": "Start", "T": "Transfer", "F": "Finish"}
        for stop_type, headline in headlines.items():
            stop_list = stops_sepcifier_report[stop_type]
            total_stops = len(stops_sepcifier_report[stop_type])
            report += [f"{headline} stops: {total_stops} {stop_list}"]
        parsed_report = "\n".join(report)
        return parsed_report

    if format_type == "stage_three":
        report = ["Line names and number of stops:"]
        for bus_id in stops_report.keys():
            report += ["bus_id: " +  f"{bus_id}, " + f"stops: {stops_report[bus_id]}"]
        parsed_report = "\n".join(report)
        return parsed_report

    if format_type == "stage_two":
        report = [f"Format validation: {tot_err} errors"]
        for field in ["stop_name", "stop_type", "a_time"]:
            report += [field + ": " + f"{ezrider.total_errors_dict[field]}"]
        parsed_report = "\n".join(report)
        return parsed_report

    if format_type == "stage_one":
        report = [f"Type and required field validation: {tot_err} errors"]
        for field in ezrider.fields:
            report += [field + ": " + f"{ezrider.total_errors_dict[field]}"]
        parsed_report = "\n".join(report)
        return parsed_report

def stage_one(user_input):
    ezrider = EzRider(user_input)
    ezrider.total_report_errors_found()
    tot_err = ezrider.get_tot_error()
    parsed_report = report_format("stage_one", ezrider, tot_err=tot_err)
    return parsed_report

def stage_two(user_input):
    ezrider = EzRider(user_input)
    ezrider.total_report_errors_found()
    tot_err = ezrider.get_tot_error()
    parsed_report = report_format("stage_two", ezrider, tot_err=tot_err)
    return parsed_report

def stage_three(user_input):
    ezrider = EzRider(user_input)
    stops_report = ezrider.stops_counter(stand_alone=True)
    parsed_report = report_format("stage_three", ezrider, stops_report=stops_report)
    return parsed_report

def stage_four(user_input):
    ezrider = EzRider(user_input)
    ezrider.stops_sepcifier()
    stops_sepcifier_report = ezrider.stops_sepcifier_report()
    parsed_report = report_format("stage_four", ezrider, stops_sepcifier_report=stops_sepcifier_report)
    return parsed_report

if __name__ == '__main__':
    report = stage_three(input())
    print(report)
