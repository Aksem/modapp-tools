from modapp_tools.code_generators.web_service import generate_web_service
from .fixtures import addressbook_proto_module


def test__generate_web_service__generates_code_for_test_proto(tmp_path):
    output_file = tmp_path / "addressbook.js"

    generate_web_service(addressbook_proto_module, output_file)

    assert (
        output_file.read_text()
        == """import { vapi_tests } from './protos.js';
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
    )
