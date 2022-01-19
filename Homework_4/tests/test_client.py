import unittest
import os
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
from client import create_presence, process_ans
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR


class TestClient(unittest.TestCase):

    def test_presence_input_name(self):
        test_dict = create_presence('Alberto')
        test_dict[TIME] = 2.9
        self.assertNotEqual(test_dict, {ACTION: PRESENCE, TIME: 2.9, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_presence_input_name_with_not(self):
        test_dict = create_presence('Alberto')
        test_dict[TIME] = 2.9
        self.assertNotEqual(test_dict, {ACTION: PRESENCE, TIME: 2.9, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_presence_base_arg(self):
        test_dict = create_presence()
        test_dict[TIME] = 3.1
        self.assertEqual(test_dict, {ACTION: PRESENCE, TIME: 3.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_process_ans_correct_input(self):
        response = process_ans({RESPONSE: 200})
        self.assertEqual(response, '200 : OK')

    def test_process_ans_incorrect_input_with_other_message(self):
        inc_response = process_ans({RESPONSE: 222, ERROR: 'Oh, wrong data!'})
        self.assertEqual(inc_response, '400 : Oh, wrong data!')

    def test_process_ans_without_response(self):
        with self.assertRaises(ValueError):
            process_ans({ERROR: 'I am error'})


if __name__ == '__main__':
    unittest.main()
