import unittest
from functional.file_management import calculate_md5_sum


class TestFileManagement(unittest.TestCase):

    def test_md5_sum(self):
        calculated_md5_sum = calculate_md5_sum("./test_processed.hdf5")
        self.assertEqual("8c3770cde105d8048ec9cffa46e36dd8", calculated_md5_sum)


if __name__ == '__main__':
    unittest.main()
