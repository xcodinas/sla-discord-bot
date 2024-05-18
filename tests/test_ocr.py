import unittest
from ocr import check_sidebar, extract_numbers_with_template

images = [
        {"path": "./img/image.png", "expected": "302418"},
        {"path": "./img/image2.png", "expected": "302418"},
        {"path": "./img/image_es.png", "expected": "98980"},
        ]


class TestImageTextExtraction(unittest.TestCase):
    def setUp(self):
        self.template_path = "./img/template.png"
        self.sidebar_template_path = "./img/sidebar_template.png"

    def test_check_sidebar(self):
        image_path = "./img/image.png"
        result, width = check_sidebar(image_path)
        self.assertTrue(result)

        image_path = "./img/image2.png"
        result, width = check_sidebar(image_path)
        self.assertFalse(result)

    def test_extract_numbers_with_template(self):
        for image in images:
            text = extract_numbers_with_template(image["path"])
            try:
                self.assertEqual(text, image["expected"])
            except AssertionError:
                print(f"Failed for image: {image['path']}")
                print(f"Expected: {image['expected']}, got: {text}")


if __name__ == '__main__':
    unittest.main()
