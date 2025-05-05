import unittest
from unittest.mock import MagicMock

from palaestrai_mosaik.util import parse_end, parse_start_date


class TestUtil(unittest.TestCase):
    def test_parse_start_date(self):
        rng = MagicMock()
        rng.randint = MagicMock(return_value=3)

        start_date = parse_start_date(None, rng)
        self.assertIsNone(start_date)
        rng.randint.assert_not_called()

        start_date = parse_start_date("random", rng)
        self.assertEqual("2020-03-03 03:00:00+0100", start_date)

        start_date = parse_start_date("2010-10-09 08:07:06+0100", rng)
        self.assertEqual("2010-10-09 08:07:06+0100", start_date)

        with self.assertLogs("palaestrai_mosaik", level="ERROR") as logger:
            start_date = parse_start_date("hello", rng)
        self.assertIn("Unable to parse start_date", logger.output[0])

    def test_parse_end(self):
        end = parse_end(5)
        self.assertEqual(5, end)

        end = parse_end("4*3")
        self.assertEqual(12, end)

        end = parse_end("4*3+2")
        self.assertEqual(14, end)

        end = parse_end("4+2*3+4*5")
        self.assertEqual(30, end)


if __name__ == "__main__":
    unittest.main()
