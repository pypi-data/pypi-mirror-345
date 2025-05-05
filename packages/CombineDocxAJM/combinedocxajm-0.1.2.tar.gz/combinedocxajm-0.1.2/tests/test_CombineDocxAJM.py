import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from CombineDocxAJM.CombineDocxAJM import CombineDocx


class TestCombineDocx(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.test_files = [str(self.test_dir / f"test{i}.docx") for i in range(1, 3)]

    @patch("CombineDocxAJM.CombineDocxAJM.Document")
    @patch("CombineDocxAJM.CombineDocxAJM.Path.is_file")
    def test_missing_master_file(self, mock_is_file, mock_document):
        # Mock `Path.is_file` to always return True
        mock_is_file.return_value = True

        # Mock `Document` creation to simulate a dummy document being loaded
        mock_document.return_value = MagicMock()

        try:
            combine_docx = CombineDocx("master_test.docx", self.test_files, str(self.test_dir))
        except Exception as e:
            self.fail(f"Initialization failed with unexpected exception: {e}")

        self.assertIsInstance(combine_docx, CombineDocx)
        mock_document.assert_called_once_with("master_test.docx")  # Confirm file is passed to `Document`

    @patch("CombineDocxAJM.CombineDocxAJM.Document")
    @patch("CombineDocxAJM.CombineDocxAJM.Path.is_file")
    def test_created_instance_with_mocked_file(self, mock_is_file, mock_document):
        mock_is_file.return_value = True
        mock_document.return_value = MagicMock()

        combine_docx = CombineDocx("master_test.docx", self.test_files, str(self.test_dir))
        self.assertIsInstance(combine_docx, CombineDocx)

    @patch("CombineDocxAJM.CombineDocxAJM.Document")
    @patch("CombineDocxAJM.CombineDocxAJM.Path.is_file")
    def test_file_list_getter_setter_with_mocked_file(self, mock_is_file, mock_document):
        mock_is_file.return_value = True
        mock_document.return_value = MagicMock()

        combine_docx = CombineDocx("master_test.docx", self.test_files, str(self.test_dir))

        new_files = [str(self.test_dir / f"test{i}.docx") for i in range(3, 5)]
        combine_docx.file_list = new_files
        self.assertEqual(combine_docx.file_list, new_files)


if __name__ == "__main__":
    unittest.main()
