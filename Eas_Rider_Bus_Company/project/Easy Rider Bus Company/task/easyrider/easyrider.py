from dataclasses import dataclass, field
import json
from collections import Counter, defaultdict
import inspect
import time
import re
import itertools


class BadBusException(Exception):
    """Base class for other exceptions"""
    pass

class FormatError(Exception):
    pass

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

    def find_bus_without_f_s(self, start_stops, final_stops):
        """ find the bus that does not have a s/f stop"""
        for id in start_stops:
            if id not in final_stops:
                return id, f"There is no start or end stop for the line: {id}."
        for id in final_stops:
            if id not in start_stops:
                return id, f"There is no start or end stop for the line: {id}."

    def check_field_validity(self,field="stop_type",entry=" "):
        match = self.check_data_types(field, entry)
        required = field in self.is_required
        if not (required and match):
            return True
        else:
            is_filled = self.check_if_filled(field, entry)
            return is_filled


    def get_buses_with_starts_finals(self):
        self.start_stops_buses = []
        self.final_stops_buses = []
        self.start_stops = []
        self.final_stops = []
        for data_point in self.parsed_input:
            stop_type = data_point["stop_type"]
            stop_name = data_point["stop_name"]
            # check if its filled according to format
            if self.check_field_validity(field="stop_type",entry=stop_type):
                bus_id = data_point["bus_id"]
                if self.check_field_validity(field="bus_id", entry=bus_id):
                    if stop_type == "S":
                        if bus_id in self.start_stops_buses:
                            return bus_id, "has more than one start_stop"
                        self.start_stops_buses.append(bus_id)
                        self.start_stops.append(stop_name)
                    if stop_type == "F":
                        if bus_id in self.final_stops_buses:
                            return bus_id, "has more than one final_stop"
                        self.final_stops_buses.append(bus_id)
                        self.final_stops.append(stop_name)
        return None, "unique"





    def unqiue_start_final_stops(self):
        """ list and check if start and final stop are unique across all lines"""
        bus_id, unique_status = self.get_buses_with_starts_finals() # create stops and finals lists return if are not unique()
        if unique_status != "unique":
            error_msg = unique_status
            return bus_id, error_msg
        start_bus_set = set(self.start_stops_buses)
        final_bus_set = set(self.final_stops_buses)
        if start_bus_set != final_bus_set:
            bad_bus, error_msg = self.find_bus_without_f_s(self.start_stops_buses, self.final_stops_buses)
            return bad_bus, error_msg
        return None, unique_status





        # for data_point in self.parsed_input:
        #     stop_type = data_point["stop_type"]
        #     # check if its filled according to format
        #     match = self.check_data_types("stop_type", stop_type)
        #     required = "bus_id" in self.is_required
        #     if not (required and match):
        #         continue
        #     else:
        #         is_filled = self.check_if_filled("stop_type", stop_type)
        #
        #     if is_filled:
        #         stop_type

    def add_stop_name(self, data_point):
        """ varify data and add stop name to lists"""

        #get stop name
        stop_name = data_point["stop_name"]

        # check if its filled according to format
        match = self.check_data_types("stop_name", stop_name)
        required = "stop_name" in self.is_required
        if (required and match):
            is_filled = self.check_if_filled("stop_name", stop_name)
        else:
            raise FormatError("format or requirement not fulfilled")

        # get bus id numbers
        bus_id = data_point["bus_id"]
        # check if its filled according to format
        match = self.check_data_types("bus_id", bus_id)
        required = "stop_name" in self.is_required
        if (required and match):
            is_filled = self.check_if_filled("bus_id", bus_id)
        else:
            raise (NameError, "format or requirement not fulfilled")

        # add stop name to bus id list
        self.all_stops[data_point["bus_id"]].append(stop_name)


    def find_transfer_stops(self, all_stops):
        transfer_set = set()
        for bus_a, bus_b in itertools.combinations(all_stops.keys(), 2):
            a_set = set(all_stops[bus_a])
            b_set = set(all_stops[bus_b])
            a_b_shared_stops = list(a_set.intersection(b_set))
            transfer_set.update(a_b_shared_stops)
        return transfer_set

    def stops_sepcifier(self):
        # checks if all bus's have unique start and final stops. if not return and instance of the failing bus line
        bad_bus, unique_status = self.unqiue_start_final_stops()
        if bad_bus:
            error_msg = unique_status
            print(error_msg)
            raise BadBusException

        # map routes
        self.all_stops = defaultdict(lambda: [])
        for data_point in self.parsed_input:
            self.add_stop_name(data_point)

        starts_list = list(set(self.start_stops))
        finals_list = list(set(self.final_stops))
        transfer_list = list(self.find_transfer_stops(self.all_stops))  # TODO
        self.stops_sepcifier_report = {"S": starts_list,
                                       "T": transfer_list,
                                       "F": finals_list}
        [self.stops_sepcifier_report[key].sort() for key in self.stops_sepcifier_report.keys()]

    def stops_time_validation(self):
        """
        Requirements from this function
        1. If the arrival time for the next stop is earlier than or equal to the time of the current stop, stop checking that bus line and remember the name of the incorrect stop.
        2. Display the information for those bus lines that have time anomalies. If all the lines are correct timewise, print OK.
        """
        last_bus_times = defaultdict(lambda: [])
        self.time_anomalies = defaultdict(lambda: [])
        for data_point in self.parsed_input:
            # validate_data(bus_id, "bus_id") # Todo
            bus_id = data_point["bus_id"]
            if self.time_anomalies[bus_id]:
                #  no need to keep track of a base that has an annomaly
                continue
            # validate_data(last_arrival_time, "a_time") # todo
            last_arrival_time = data_point["a_time"]
            if not last_bus_times[bus_id]:
                last_bus_times[bus_id] = last_arrival_time

            # check if arrival time is older:
            is_later = (last_bus_times[bus_id] <= last_arrival_time)
            if not is_later:
                self.time_anomalies[bus_id] = data_point["stop_name"]
            last_bus_times[bus_id] = last_arrival_time
        return self.time_anomalies

    def stops_time_validatr(self):
        pass


def report_format(format_type, ezrider, stop_time_validation_report=0, tot_err=0, stops_report=0):

    if format_type == "stage_five":
        report = ["Arrival time test:"]
        # check if all is good
        if not any(ezrider.time_anomalies.values()):
            report.append("OK")
            parsed_report = "\n".join(report)
            return parsed_report

        for bus_id, stop_name in ezrider.time_anomalies.items():
            if stop_name == []:
                continue
            report.append(f"bus_id line {bus_id}: wrong time on station {stop_name}")

        parsed_report = "\n".join(report)
        return parsed_report

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
    stops_sepcifier_report = ezrider.stops_sepcifier_report
    parsed_report = report_format("stage_four", ezrider, stops_sepcifier_report=stops_sepcifier_report)
    return parsed_report

def stage_five(user_input):
    ezrider = EzRider(user_input)
    ezrider.stops_time_validation()
    parsed_report = report_format("stage_five", ezrider)
    return parsed_report

if __name__ == '__main__':
    try:
        report = stage_five(input())
        print(report)
    except BadBusException:
        pass
