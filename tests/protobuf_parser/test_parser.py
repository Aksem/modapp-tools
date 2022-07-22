from pathlib import Path

from modapp_tools.protobuf_parser.parser import (
    parse_protobuf,
    Newline,
    ProtoModule,
    Comment,
    Syntax,
    Package,
    Import,
    Option,
    Message,
    MessageProperty,
    Enum,
    EnumItem,
    Service,
    ServiceEndpoint,
)


def test__parse_protobuf__parses_test_proto_file():
    current_path = Path(__file__).parent
    proto_file = current_path / "addressbook.proto"

    result = parse_protobuf(proto_file)

    assert result == ProtoModule(
        instructions=[
            Comment(" Example of protobuf definition for parser tests", newline="\n\n"),
            Syntax("proto3"),
            Newline("\n\n"),
            Package("vapi_tests.parser_proto_example"),
            Newline("\n\n"),
            Import("google/protobuf/timestamp.proto"),
            Newline("\n\n"),
            Comment(" option example"),
            Option(name="java_multiple_files", value=True),
            Newline("\n\n"),
            Message(
                name="Person",
                statements=[
                    Newline("\n"),
                    MessageProperty(
                        repeated=False, name="name", data_type="string", number=1
                    ),
                    Newline("\n"),
                    MessageProperty(
                        repeated=False, name="id", data_type="int32", number=2
                    ),
                    Comment(" Unique ID number for this person."),
                    MessageProperty(
                        repeated=False, name="email", data_type="string", number=3
                    ),
                    Newline("\n\n"),
                    Enum(
                        name="PhoneType",
                        items=[
                            EnumItem(name="MOBILE", value=0),
                            EnumItem(name="HOME", value=1),
                            EnumItem(name="WORK", value=2),
                        ],
                    ),
                    Newline("\n\n"),
                    Message(
                        name="PhoneNumber",
                        statements=[
                            Newline("\n"),
                            MessageProperty(
                                repeated=False,
                                name="number",
                                data_type="string",
                                number=1,
                            ),
                            Newline("\n"),
                            MessageProperty(
                                repeated=False,
                                name="type",
                                data_type="PhoneType",
                                number=2,
                            ),
                            Newline("\n"),
                        ],
                    ),
                    Newline("\n\n"),
                    MessageProperty(
                        repeated=True, name="phones", data_type="PhoneNumber", number=4
                    ),
                    Newline("\n\n"),
                    MessageProperty(
                        repeated=False,
                        name="last_updated",
                        data_type="google.protobuf.Timestamp",
                        number=5,
                    ),
                    Newline("\n"),
                ],
            ),
            Newline("\n\n"),
            Message(
                name="AddressBook",
                statements=[
                    Newline("\n"),
                    MessageProperty(
                        repeated=False, name="id", data_type="uint32", number=1
                    ),
                    Newline("\n"),
                    MessageProperty(
                        repeated=True, name="people", data_type="Person", number=2
                    ),
                    Newline("\n"),
                ],
            ),
            Newline("\n\n"),
            Message(
                name="GetPersonListResponse",
                statements=[
                    Newline("\n"),
                    MessageProperty(
                        repeated=True, name="items", data_type="Person", number=1
                    ),
                    Newline("\n"),
                ],
            ),
            Newline("\n\n"),
            Message(
                name="GetAddressBookRequest",
                statements=[
                    Newline("\n"),
                    MessageProperty(
                        repeated=False, name="id", data_type="uint32", number=1
                    ),
                    Newline("\n"),
                ],
            ),
            Newline("\n\n"),
            Message(
                name="GetAddressBookListResponse",
                statements=[
                    Newline("\n"),
                    MessageProperty(
                        repeated=True, name="items", data_type="AddressBook", number=1
                    ),
                    Newline(content='\n'),
                    MessageProperty(
                        repeated=False, name="active", data_type="map<uint32, boolean>", number=2
                    ),
                    Newline("\n"),
                ],
            ),
            Newline("\n\n"),
            Message(
                name="GetPersonRequest",
                statements=[
                    Newline("\n"),
                    MessageProperty(
                        repeated=False, name="id", data_type="int32", number=1
                    ),
                    Newline("\n"),
                ],
            ),
            Newline("\n\n"),
            Service(
                name="AddressBookService",
                statements=[
                    Newline("\n"),
                    Comment(" unary-unary"),
                    ServiceEndpoint(
                        name="GetPersonList",
                        argument_is_stream=False,
                        argument_type="Person",
                        return_is_stream=False,
                        return_type="GetPersonListResponse",
                    ),
                    Newline("\n"),
                    Comment(" unary-stream"),
                    ServiceEndpoint(
                        name="GetAddressBookList",
                        argument_is_stream=False,
                        argument_type="AddressBook",
                        return_is_stream=True,
                        return_type="GetAddressBookListResponse",
                    ),
                    Newline("\n"),
                    Comment(" stream-unary"),
                    ServiceEndpoint(
                        name="GetPerson",
                        argument_is_stream=True,
                        argument_type="GetPersonRequest",
                        return_is_stream=False,
                        return_type="Person",
                    ),
                    Newline("\n"),
                    Comment(" stream-stream"),
                    ServiceEndpoint(
                        name="GetAddressBook",
                        argument_is_stream=True,
                        argument_type="GetAddressBookRequest",
                        return_is_stream=True,
                        return_type="AddressBook",
                    ),
                    Newline("\n"),
                ],
            ),
            Newline("\n"),
        ],
    )
