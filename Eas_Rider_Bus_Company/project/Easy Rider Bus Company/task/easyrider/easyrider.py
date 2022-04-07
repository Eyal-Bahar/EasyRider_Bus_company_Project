from dataclasses import dataclass


@dataclass
class EzRider:
    """ class for sorting out the existing database of the "Easy Rider" bus company"""
    user_input: list

    def check_data_types(self):
        self.data_types_report

    def check_required_fields(self):
        self.data_required_fields

    def report_errors_found(self) -> list:
        self.data_types_report
        self.data_required_fields



def stage_one(user_input):
    ezrider = EzRider(user_input)
    ezrider.check_data_types()
    ezrider.check_required_fields()
    ezrider.disply_errors_found()




if __name__ == '__main__':
    stage_one(input())