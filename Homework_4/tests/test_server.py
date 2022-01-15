import unittest
import os
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
from server import process_client_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, RESPONDEFAULT_IP_ADDRESSES


class TestServer(unittest.TestCase):

    err_dict = {
        RESPONDEFAULT_IP_ADDRESSES: 400,
        ERROR: 'Bad Request'
    }

    ok_dict = {
        RESPONSE: 200,
    }

    def test_process_client_message_correct_input(self):
        correct_message = {
            ACTION: PRESENCE,
            TIME: 2.5,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }

        response_dict = process_client_message(correct_message)
        self.assertEqual(response_dict, self.ok_dict)

    def test_process_client_message_no_action(self):
        no_action_message = {
            TIME: 2.5,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }

        response_dict = process_client_message(no_action_message)
        self.assertEqual(response_dict, self.err_dict)

    def test_process_client_message_wrong_action(self):
        inc_action_message = {
            ACTION: 'run',
            TIME: 2.5,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }

        response_dict = process_client_message(inc_action_message)
        self.assertEqual(response_dict, self.err_dict)

    def test_process_client_message_no_time(self):
        no_time_message = {
            ACTION: 'run',
            TIME: 2.5,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }

        response_dict = process_client_message(no_time_message)
        self.assertEqual(response_dict, self.err_dict)

    def test_process_client_message_no_user(self):
        no_user_message = {
            ACTION: PRESENCE,
            TIME: 2.5,
        }

        response_dict = process_client_message(no_user_message)
        self.assertEqual(response_dict, self.err_dict)

    def test_process_client_message_wrong_name(self):
        inc_name_message = {
            ACTION: PRESENCE,
            TIME: 2.5,
            USER: {
                ACCOUNT_NAME: 'James'
            }
        }

        response_dict = process_client_message(inc_name_message)
        self.assertEqual(response_dict, self.err_dict)


if __name__ == '__main__':
    unittest.main()
