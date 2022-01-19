import json
import unittest
import os
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.utils import get_message, send_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, ENCODING, \
    RESPONDEFAULT_IP_ADDRESSES


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_length):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):

    send_dict = {
        ACTION: PRESENCE,
        TIME: 2.5,
        USER: {
            ACCOUNT_NAME: 'Guest'
        }
    }

    recv_err_dict = {
        RESPONDEFAULT_IP_ADDRESSES: 400,
        ERROR: 'Bad Request'
    }

    recv_ok_dict = {
        RESPONSE: 200,
    }

    def test_get_message_correct_input(self):
        correct_test_socket = TestSocket(self.recv_ok_dict)
        correct_message = get_message(correct_test_socket)
        self.assertEqual(correct_message, self.recv_ok_dict)

    def test_get_message_incorrect_input(self):
        incorrect_test_socket = TestSocket(self.recv_err_dict)
        incorrect_message = get_message(incorrect_test_socket)
        self.assertEqual(incorrect_message, self.recv_err_dict)

    def test_get_message_wrong_dict(self):
        recv_wrong_dict = {
            RESPONSE: 200,
            'strange_stuff': {'I', 'am', 'set'}
        }
        wrong_client = TestSocket(recv_wrong_dict)

        with self.assertRaises(TypeError):
            get_message(wrong_client)

    def test_send_message_input(self):
        correct_test_socket = TestSocket(self.send_dict)
        send_message(correct_test_socket, self.send_dict)
        self.assertEqual(correct_test_socket.encoded_message, correct_test_socket.received_message)



if __name__ == '__main__':
    unittest.main()
