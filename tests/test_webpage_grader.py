import unittest
from unittest.mock import patch
from site_sensei import linkchecks, webchecks, webpage_grader

TEST_URL = "https://codeprojects.org/projects/weblab/JONWyX5NqCkqfKdglTZSkoL6S3cHatmg3MFurTWWDXY"


class TestLinkChecks(unittest.TestCase):
    def test_check_localhost(self):
        self.assertTrue(linkchecks.check_localhost())

    @patch('requests.get')
    def test_check_connectivity(self, mock_get):
        mock_get.return_value.status_code = 200
        self.assertTrue(linkchecks.check_connectivity("http://example.com"))

    @patch('requests.get')
    def test_link_status_success(self, mock_get):
        mock_get.return_value.status_code = 200
        msg = linkchecks.link_status("http://example.com")
        self.assertIn("Status: 200", msg)


class TestWebChecks(unittest.TestCase):
    def test_get_tags_returns_dict(self):
        tags = webchecks.get_tags("https://www.example.com", ["p", "h1", "li"])
        self.assertIsInstance(tags, dict)

    def test_count_comments_returns_int(self):
        comments = webchecks.count_comments("https://www.example.com")
        self.assertIsInstance(comments, int)

    def test_count_broken_tags_type(self):
        result = webchecks.count_broken_tags("https://www.example.com")
        self.assertIsInstance(result, dict)

    def test_get_links_list_or_error(self):
        links = webchecks.get_links("https://www.example.com")
        self.assertTrue(isinstance(links, list) or isinstance(links, Exception))

    def test_get_class_output(self):
        msg = webchecks.get_class("https://www.example.com")
        self.assertIsInstance(msg, str)

    def test_has_image_credit_boolean(self):
        result = webchecks.has_image_credit("https://www.example.com")
        self.assertIn(result, [True, False])


class TestGraderIntegration(unittest.TestCase):
    def test_grade_student_output_keys(self):
        result = webpage_grader.grade_student("https://www.example.com")
        self.assertIn("feedback", result)
        self.assertIn("class_message", result)
        self.assertIn("url_status", result)

    def test_generate_feedback_html_format(self):
        html_output = webpage_grader.generate_feedback_html("https://www.example.com")
        self.assertIn("<ul>", html_output)
        self.assertIn("https://www.example.com", html_output)


if __name__ == '__main__':
    unittest.main()
