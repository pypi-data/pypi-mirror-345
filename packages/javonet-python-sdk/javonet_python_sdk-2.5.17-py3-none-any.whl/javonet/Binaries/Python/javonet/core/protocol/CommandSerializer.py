import io
from javonet.core.protocol.TypeSerializer import TypeSerializer
from javonet.utils.Command import Command
from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.connectionData.IConnectionData import IConnectionData

class CommandSerializer:
    def serialize(self, root_command: Command, connection_data: IConnectionData, runtime_version=0):
        ms = io.BytesIO()

        ms.write(bytes([root_command.runtime_name.value, runtime_version]))

        if connection_data is not None:
            ms.write(bytes(connection_data.serialize_connection_data()))
        else:
            ms.write(bytes([0, 0, 0, 0, 0, 0, 0]))

        ms.write(bytes([RuntimeName.python.value, root_command.command_type.value]))

        self.serialize_recursively(root_command, ms)
        return ms.getvalue()

    def serialize_recursively(self, command: Command, ms: io.BytesIO):
        for item in command.get_payload():
            if isinstance(item, Command):
                ms.write(bytes(TypeSerializer.serialize_command(item)))
                self.serialize_recursively(item, ms)
            else:
                ms.write(bytes(TypeSerializer.serialize_primitive(item)))