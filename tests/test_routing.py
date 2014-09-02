# -*- coding: utf-8; -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Flavien Charlon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import colorcore.routing
import io
import openassets.transactions
import unittest
import unittest.mock


class RouterTests(unittest.TestCase):

    def test_parse_call(self):
        router = self.create_router()
        router.parse(['test_operation', 'val1', 'val2'])

        self.assertEqual('"val1val2default"\n', self.output.getvalue())

    def test_raise_controller_error(self):
        router = self.create_router()
        router.parse(['test_raise_controller_error'])

        self.assertEqual('Error: Test error\n', self.output.getvalue())

    def test_raise_transaction_builder_error(self):
        router = self.create_router()
        router.parse(['test_raise_transaction_builder_error'])

        self.assertEqual('Error: InsufficientAssetQuantityError\n', self.output.getvalue())

    def test_parse_help(self):
        router = self.create_router()
        with unittest.mock.patch('argparse.ArgumentParser.exit') as error_patch, \
            unittest.mock.patch('argparse._sys', stdout=self.output):
            error_patch.side_effect = SystemError

            self.assertRaises(SystemError, router.parse, ['test_operation', '--help'])
            self.assertIn('help1', self.output.getvalue())
            self.assertIn('help2', self.output.getvalue())
            self.assertIn('help3', self.output.getvalue())

    def test_parse_server(self):
        router = self.create_router()
        self.configuration.rpc_enabled = True
        self.configuration.rpc_port = 8080
        with unittest.mock.patch('http.server.HTTPServer.serve_forever') as serve_forever_patch:
            serve_forever_patch.return_value = None

            router.parse(['server'])
            self.assertIn('Starting RPC server on port 8080...\n', self.output.getvalue())
            serve_forever_patch.assert_called_with()

    def test_parse_server_not_enabled(self):
        router = self.create_router()
        self.configuration.rpc_enabled = False
        self.configuration.rpc_port = 8080
        with unittest.mock.patch('http.server.HTTPServer.serve_forever') as serve_forever_patch:

            router.parse(['server'])
            self.assertIn('Error: RPC must be enabled in the configuration.\n', self.output.getvalue())
            serve_forever_patch.assert_not_called()

    def create_router(self):
        class MockController(object):
            def __init__(self, configuration, *args):
                pass

            def test_operation(self, parameter1: 'help1', parameter2: 'help2', parameter3: 'help3'='default'):
                """function help"""
                return parameter1 + parameter2 + parameter3

            def test_raise_controller_error(self):
                """raise 1"""
                raise colorcore.routing.ControllerError('Test error')

            def test_raise_transaction_builder_error(self):
                """raise 2"""
                raise openassets.transactions.InsufficientAssetQuantityError

        self.configuration = unittest.mock.Mock()
        self.output = io.StringIO()
        return colorcore.routing.Router(MockController, self.output, self.configuration)
