import unittest
import easyrider


stage_1_input = """[
    {
        "bus_id": 128,
        "stop_id": 1,
        "stop_name": "Prospekt Avenue",
        "next_stop": 3,
        "stop_type": "S",
        "a_time": 8.12
    },
    {
        "bus_id": 128,
        "stop_id": 3,
        "stop_name": "",
        "next_stop": 5,
        "stop_type": "",
        "a_time": "08:19"
    },
    {
        "bus_id": 128,
        "stop_id": 5,
        "stop_name": "Fifth Avenue",
        "next_stop": 7,
        "stop_type": "O",
        "a_time": "08:25"
    },
    {
        "bus_id": 128,
        "stop_id": "7",
        "stop_name": "Sesame Street",
        "next_stop": 0,
        "stop_type": "F",
        "a_time": "08:37"
    },
    {
        "bus_id": "",
        "stop_id": 2,
        "stop_name": "Pilotow Street",
        "next_stop": 3,
        "stop_type": "S",
        "a_time": ""
    },
    {
        "bus_id": 256,
        "stop_id": 3,
        "stop_name": "Elm Street",
        "next_stop": 6,
        "stop_type": "",
        "a_time": "09:45"
    },
    {
        "bus_id": 256,
        "stop_id": 6,
        "stop_name": "Sunset Boulevard",
        "next_stop": 7,
        "stop_type": "",
        "a_time": "09:59"
    },
    {
        "bus_id": 256,
        "stop_id": 7,
        "stop_name": "Sesame Street",
        "next_stop": "0",
        "stop_type": "F",
        "a_time": "10:12"
    },
    {
        "bus_id": 512,
        "stop_id": 4,
        "stop_name": "Bourbon Street",
        "next_stop": 6,
        "stop_type": "S",
        "a_time": "08:13"
    },
    {
        "bus_id": "512",
        "stop_id": 6,
        "stop_name": "Sunset Boulevard",
        "next_stop": 0,
        "stop_type": 5,
        "a_time": "08:16"
    }
]"""

STAGE_ONE_OUTPUT = """Type and required field validation: 8 errors
bus_id: 2
stop_id: 1
stop_name: 1
next_stop: 1
stop_type: 1
a_time: 2"""

class TestEasyRider(unittest.TestCase):
    # def test_to_c_what_happens(self):
    #     self.assertTrue(easyrider.wat('apple', 'pineapple pie'))
    #     self.assertFalse(easyrider.wat('apple', 'orange'))

    def test_stage_one(self, STAGE_ONE_OUTPUT=STAGE_ONE_OUTPUT):
        self.assertTrue(STAGE_ONE_OUTPUT == easyrider.stage_one(stage_1_input))


if __name__ == '__main__':
    unittest.main()