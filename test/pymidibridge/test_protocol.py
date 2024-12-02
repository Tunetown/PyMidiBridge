import sys
import unittest
from unittest.mock import patch, mock_open

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "os": MockOs
}):
    from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pymidibridge import PyMidiBridge, PMB_MANUFACTURER_ID, PMB_REQUEST_MESSAGE


class TestProtocol(unittest.TestCase):

    def test_send_receive(self):
        self._test_send_receive(
            temp_path = ".tmppath",
            path = "/foo/path/to/bar.txt",
            data = "Some foo file content \n with newlines \n etc.pp and Umlauts äöü \n acbdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789°^!\2§$%&/()=ß?´`+*#'-_.:,;<>"
        )

    def _test_send_receive(self, temp_path, path, data):
        MockOs.RENAME_CALLS = []
        midi = MockMidi()

        bridge = PyMidiBridge(
            midi = midi,
            temp_file_path = temp_path
        )

        # Let the bridge send a mocked file
        with patch("builtins.open", mock_open(read_data = data)) as mock_file_open:
            bridge.send(path)

            mock_file_open.assert_called_with(path, "r")

        # Are there any messages?
        self.assertGreater(len(midi.messages_sent), 0)

        # Feed back the generated MIDI messages to the bridge, yielding the input data again
        with patch("builtins.open", mock_open()) as mock_file_open:        
            for msg in midi.messages_sent:
                bridge.receive(msg)

            #mock_file_open.assert_called_with(temp_path, "w")
            mock_file_open.assert_called_with(temp_path, "a")
            
            handle = mock_file_open()
            handle.write.assert_called_with(data)

            self.assertEqual(MockOs.RENAME_CALLS, [{ 
                "source": temp_path,
                "target": path
            }])

    def test_send_no_path(self):
        bridge = PyMidiBridge(
            midi = MockMidi(),
            temp_file_path = "foo"
        )

        with self.assertRaises(Exception):
            bridge.send(None)

        with self.assertRaises(Exception):
            bridge.send("")


############################################################################################################


    def test_request_file(self):
        self._test_request_file(" ")
        self._test_request_file("foo")
        self._test_request_file("/foo/path/to/bar.txt")

    def _test_request_file(self, path):
        midi = MockMidi()

        bridge = PyMidiBridge(
            midi = midi,
            temp_file_path = None
        )        
        
        bridge.request(path)

        msg_sent = midi.messages_sent[0]
        self.assertIsInstance(msg_sent, SystemExclusive)
        self.assertEqual(msg_sent.manufacturer_id, PMB_MANUFACTURER_ID)
        self.assertEqual(msg_sent.data[:1], PMB_REQUEST_MESSAGE)

        checksum = msg_sent.data[1:4]
        payload = bridge._bytes_2_string(msg_sent.data[4:])
        
        self.assertEqual(payload, path)
        self.assertEqual(checksum, bridge._get_checksum(msg_sent.data[4:]))


    def test_request_no_path(self):
        midi = MockMidi()

        bridge = PyMidiBridge(
            midi = midi,
            temp_file_path = None
        )

        with self.assertRaises(Exception):
            bridge.request(None)

        with self.assertRaises(Exception):
            bridge.request("")
