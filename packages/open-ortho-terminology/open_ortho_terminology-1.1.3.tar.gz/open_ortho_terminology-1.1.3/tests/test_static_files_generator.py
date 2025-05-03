import unittest
from pathlib import Path
import json
import os

from terminology.main import get_all_code_systems
from terminology.resources.code_systems import extraoral_2d_photographic_scheduled_protocol 

class TestMain(unittest.TestCase):

    def test_get_all_code_systems(self):
        all_code_systems = get_all_code_systems()
        self.assertIsInstance(all_code_systems, dict)
        self.assertTrue(all_code_systems)
        self.assertTrue(all_code_systems.get(extraoral_2d_photographic_scheduled_protocol.Extraoral2DPhotographicScheduledProtocolCodeSystem().url))

if __name__ == '__main__':
    unittest.main()