from vapi_tools.code_generators.web_service import generate_web_service
from vapi_tools.protobuf_parser.ast import Newline, ProtoModule, Comment, Syntax, Package, Import, Option, Message, MessageProperty, Enum, EnumItem, Service, ServiceEndpoint


def test__generate_web_service__generates_code_for_test_proto(tmp_path):
    proto_module = ProtoModule(
        instructions=[
            Comment(" Example of protobuf definition for parser tests"),
            Newline('\n\n'),
            Syntax('proto3'),
            Newline('\n\n'),
            Package('vapi_tests.parser_proto_example'),
            Newline('\n\n'),
            Import('google/protobuf/timestamp.proto'),
            Newline('\n\n'),
            Comment(' option example'),
            Newline('\n'),
            Option(name='java_multiple_files', value=True),
            Newline('\n\n'),
            Message(name='Person', statements=[
                Newline('\n'),
                MessageProperty(repeated=False, name='name', data_type='string', number=1),
                Newline('\n'),
                MessageProperty(repeated=False, name='id', data_type='int32', number=2),
                Comment(' Unique ID number for this person.'),
                Newline('\n'),
                MessageProperty(repeated=False, name='email', data_type='string', number=3),
                Newline('\n\n'),
                Enum(name='PhoneType', items=[
                    EnumItem(name='MOBILE', value=0),
                    EnumItem(name='HOME', value=1),
                    EnumItem(name='WORK', value=2),
                ]),
                Newline('\n\n'),
                Message(name='PhoneNumber', statements=[
                    Newline('\n'),
                    MessageProperty(repeated=False, name='number', data_type='string', number=1),
                    Newline('\n'),
                    MessageProperty(repeated=False, name='type', data_type='PhoneType', number=2),
                    Newline('\n'),
                ]),
                Newline('\n\n'),
                MessageProperty(repeated=True, name='phones', data_type='PhoneNumber', number=4),
                Newline('\n\n'),
                MessageProperty(repeated=False, name='last_updated', data_type='google.protobuf.Timestamp', number=5),
                Newline('\n'),
            ]),
            Newline('\n\n'),
            Message(name='AddressBook', statements=[
                Newline('\n'),
                MessageProperty(repeated=False, name='id', data_type='uint32', number=1),
                Newline('\n'),
                MessageProperty(repeated=True, name='people', data_type='Person', number=2),
                Newline('\n'),
            ]),
            Newline('\n\n'),
            Message(name='GetPersonListResponse', statements=[
                Newline('\n'),
                MessageProperty(repeated=True, name='items', data_type='Person', number=1),
                Newline('\n'),
            ]),
            Newline('\n\n'),
            Message(name='GetAddressBookRequest', statements=[
                Newline('\n'),
                MessageProperty(repeated=False, name='id', data_type='uint32', number=1),
                Newline('\n'),
            ]),
            Newline('\n\n'),
            Message(name='GetAddressBookListResponse', statements=[
                Newline('\n'),
                MessageProperty(repeated=True, name='items', data_type='AddressBook', number=1),
                Newline('\n'),
            ]),
            Newline('\n\n'),
            Message(name='GetPersonRequest', statements=[
                Newline('\n'),
                MessageProperty(repeated=False, name='id', data_type='int32', number=1),
                Newline('\n'),
            ]),
            Newline('\n\n'),
            Service(name='AddressBookService', statements=[
                Newline('\n'),
                Comment(' unary-unary'),
                Newline('\n'),
                ServiceEndpoint(name='GetPersonList', argument_is_stream=False, argument_type='Person', return_is_stream=False, return_type='GetPersonListResponse'),
                Newline('\n'),
                Comment(' unary-stream'),
                Newline('\n'),
                ServiceEndpoint(name='GetAddressBookList', argument_is_stream=False, argument_type='AddressBook', return_is_stream=True, return_type='GetAddressBookListResponse'),
                Newline('\n'),
                Comment(' stream-unary'),
                Newline('\n'),
                ServiceEndpoint(name='GetPerson', argument_is_stream=True, argument_type='GetPersonRequest', return_is_stream=False, return_type='Person'),
                Newline('\n'),
                Comment(' stream-stream'),
                Newline('\n'),
                ServiceEndpoint(name='GetAddressBook', argument_is_stream=True, argument_type='GetAddressBookRequest', return_is_stream=True, return_type='AddressBook'),
                Newline('\n'),
            ]),
            Newline('\n'),
        ],
    )
    output_file = tmp_path / 'addressbook.js'

    generate_web_service(proto_module, output_file)

    assert output_file.read_text() == """import { vapi_tests } from './protos.js';
import { rpcStreamStreamCall, rpcStreamUnaryCall, rpcUnaryStreamCall, rpcUnaryUnaryCall } from './rpc.js';

//  Example of protobuf definition for parser tests
//  option example
//  Unique ID number for this person.
export const addressBookService = {
//  unary-unary
getPersonList({name = null, id = null, email = null, phones = null, last_updated = null} = {}) {
    return rpcUnaryUnaryCall(
        '/vapi_tests.parser_proto_example.AddressBookService/GetPersonList',
        vapi_tests.parser_proto_example.Person,
        vapi_tests.parser_proto_example.GetPersonListResponse,
        { name, id, email, phones, last_updated }
    );
},

//  unary-stream
getAddressBookList({id = null, people = null} = {}) {
    return rpcUnaryStreamCall(
        '/vapi_tests.parser_proto_example.AddressBookService/GetAddressBookList',
        vapi_tests.parser_proto_example.AddressBook,
        vapi_tests.parser_proto_example.GetAddressBookListResponse,
        { id, people }
    );
},

//  stream-unary
getPerson({id = null} = {}) {
    return rpcStreamUnaryCall(
        '/vapi_tests.parser_proto_example.AddressBookService/GetPerson',
        vapi_tests.parser_proto_example.GetPersonRequest,
        vapi_tests.parser_proto_example.Person,
        { id }
    );
},

//  stream-stream
getAddressBook({id = null} = {}) {
    return rpcStreamStreamCall(
        '/vapi_tests.parser_proto_example.AddressBookService/GetAddressBook',
        vapi_tests.parser_proto_example.GetAddressBookRequest,
        vapi_tests.parser_proto_example.AddressBook,
        { id }
    );
},

};"""
