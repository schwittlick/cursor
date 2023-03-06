from tools.octet.plotter import Plotter
from tools.octet.server import Server

import unittest
from threading import Thread
import wasabi

logger = wasabi.Printer(pretty=False, no_print=False)


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the server in a separate thread
        cls.server = Server()
        cls.server_thread = Thread(target=cls.server.listen)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        # Stop the server thread
        cls.server.socket.close()
        cls.server_thread.join()

    def test_socket_connection(self):
        plotter = Plotter("COM1", 9600, 1)
        plotter.connect()

        self.assertTrue(plotter.is_connected)

        plotter.is_open_serial()
        success, answer = plotter.recv()

        self.assertFalse(success)
        self.assertEqual(answer, 'IS NOT OPEN')

        plotter.disconnect()

        self.assertFalse(plotter.is_connected)
