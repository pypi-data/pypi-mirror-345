# -*- coding: utf-8 -*-
"""
The CommandSerializer module implements command serialization.
"""

from javonet.core.protocol.TypeSerializer import TypeSerializer
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.connectionData.IConnectionData import IConnectionData


class CommandSerializer(object):
    """
    Class responsible for command serialization.
    """
    buffer = []

    def serialize(self, root_command, connection_data, runtime_version=0):
        """
        Serializes a command.

        :param root_command: Command to serialize
        :param connection_data: Connection data
        :param runtime_version: Runtime version
        :return: Serialized command
        """
        self.buffer = []  # Reset buffer for each serialization
        self.insert_into_buffer([root_command.runtime_name.value, runtime_version])
        self.insert_into_buffer(connection_data.serialize_connection_data())
        self.insert_into_buffer([RuntimeName.python.value, root_command.command_type.value])
        self.serialize_recursively(root_command)
        return self.buffer

    def serialize_recursively(self, command):
        """
        Serializes a command recursively.

        :param command: Command to serialize
        """
        for item in command.get_payload():
            if isinstance(item, Command):
                self.insert_into_buffer(TypeSerializer.serialize_command(item))
                self.serialize_recursively(item)
            else:
                self.insert_into_buffer(TypeSerializer.serialize_primitive(item))

        return

    def insert_into_buffer(self, arguments):
        """
        Inserts arguments into the buffer.

        :type arguments: list
        """
        self.buffer = self.buffer + arguments 