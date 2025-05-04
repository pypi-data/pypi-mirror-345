from argenta.command.flag import Flag, InputFlag, Flags
from argenta.command.models import InputCommand, Command
from argenta.command.exceptions import (UnprocessedInputFlagException,
                                        RepeatedInputFlagsException,
                                        EmptyInputCommandException)

import unittest


class TestInputCommand(unittest.TestCase):
    def test_parse_correct_raw_command(self):
        self.assertEqual(InputCommand.parse('ssh --host 192.168.0.3').get_trigger(), 'ssh')

    def test_parse_raw_command_without_flag_name_with_value(self):
        with self.assertRaises(UnprocessedInputFlagException):
            InputCommand.parse('ssh 192.168.0.3')

    def test_parse_raw_command_with_repeated_flag_name(self):
        with self.assertRaises(RepeatedInputFlagsException):
            InputCommand.parse('ssh --host 192.168.0.3 --host 172.198.0.43')

    def test_parse_empty_raw_command(self):
        with self.assertRaises(EmptyInputCommandException):
            InputCommand.parse('')

    def test_validate_correct_input_flag1(self):
        command = Command('some', flags=Flag('test'))
        self.assertEqual(command.validate_input_flag(InputFlag('test')), True)

    def test_validate_correct_input_flag2(self):
        command = Command('some', flags=Flags(Flag('test'), Flag('more')))
        self.assertEqual(command.validate_input_flag(InputFlag('more')), True)

    def test_validate_incorrect_input_flag1(self):
        command = Command('some', flags=Flags(Flag('test')))
        self.assertEqual(command.validate_input_flag(InputFlag('more')), False)

    def test_validate_incorrect_input_flag2(self):
        command = Command('some', flags=Flags(Flag('test'), Flag('more')))
        self.assertEqual(command.validate_input_flag(InputFlag('case')), False)

    def test_validate_incorrect_input_flag3(self):
        command = Command('some')
        self.assertEqual(command.validate_input_flag(InputFlag('case')), False)

    def test_isinstance_parse_correct_raw_command(self):
        cmd = InputCommand.parse('ssh --host 192.168.0.3')
        self.assertIsInstance(cmd, InputCommand)

