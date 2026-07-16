import unittest
from unittest.mock import Mock, patch
from shared import utils
from shared import webchecks
from student_mode import webpage_grader

TEST_URL = "https://codeprojects.org/projects/weblab/JONWyX5NqCkqfKdglTZSkoL6S3cHatmg3MFurTWWDXY"


class TestLinkChecks(unittest.TestCase):
    def test_check_localhost(self):
        self.assertTrue(utils.check_localhost())

    @patch('shared.utils.requests.get')
    def test_reachable_project_url(self, mock_get):
        mock_get.return_value.status_code = 200
        msg = utils.check_project_url("http://example.com")
        self.assertIn("Status: 200", msg)
        mock_get.assert_called_once_with("http://example.com", timeout=5)

    @patch('shared.utils.requests.get')
    def test_unreachable_project_url(self, mock_get):
        mock_get.return_value.status_code = 404
        msg = utils.check_project_url("http://example.com")
        self.assertIn("Status: 404", msg)
        self.assertIn("Request Failed", msg)

    @patch('shared.utils.requests.get')
    def test_working_discovered_page_link(self, mock_get):
        mock_get.return_value.status_code = 200
        msg = utils.check_page_link("http://example.com/about.html")
        self.assertIn("Status: 200", msg)

    @patch('shared.utils.requests.get')
    def test_broken_discovered_page_link(self, mock_get):
        mock_get.return_value.status_code = 404
        msg = utils.check_page_link("http://example.com/missing.html")
        self.assertIn("Status: 404", msg)
        self.assertIn("Request Failed", msg)

    @patch('shared.utils.requests.get')
    def test_project_url_request_exception(self, mock_get):
        mock_get.side_effect = utils.requests.exceptions.Timeout
        msg = utils.check_project_url("http://example.com")
        self.assertIn("Error connecting", msg)

    @patch('shared.utils.requests.get')
    def test_page_link_request_exception(self, mock_get):
        mock_get.side_effect = utils.requests.exceptions.RequestException
        msg = utils.check_page_link("http://example.com/about.html")
        self.assertIn("Error connecting", msg)


class TestWebChecks(unittest.TestCase):
    @patch('shared.webchecks.urllib.request.urlopen')
    def test_get_tags_returns_dict(self, mock_urlopen):
        mock_urlopen.return_value.read.return_value = b'<h1>Title</h1><p>Text</p>'
        tags = webchecks.get_tags("https://www.example.com", ["p", "h1", "li"])
        self.assertIsInstance(tags, dict)

    @patch('shared.webchecks.urllib.request.urlopen')
    def test_count_comments_returns_int(self, mock_urlopen):
        mock_urlopen.return_value.read.return_value = b'<!-- comment -->'
        comments = webchecks.count_comments("https://www.example.com")
        self.assertIsInstance(comments, int)

    @patch('shared.webchecks.urllib.request.urlopen')
    def test_count_broken_tags_type(self, mock_urlopen):
        mock_urlopen.return_value.read.return_value = b'<p>Text</p>'
        result = webchecks.count_broken_tags("https://www.example.com")
        self.assertIsInstance(result, dict)

    @patch('shared.webchecks.urllib.request.urlopen')
    def test_get_links_list_or_error(self, mock_urlopen):
        mock_urlopen.return_value.read.return_value = b'<a href="about.html">About</a>'
        links = webchecks.get_links("https://www.example.com")
        self.assertTrue(isinstance(links, list) or isinstance(links, Exception))

    @patch('shared.webchecks.requests.get')
    def test_get_class_output(self, mock_get):
        mock_get.return_value.text = '<p class="intro">Text</p>'
        msg = webchecks.get_class("https://www.example.com")
        self.assertIsInstance(msg, str)

    @patch('shared.webchecks.urllib.request.urlopen')
    def test_has_image_credit_boolean(self, mock_urlopen):
        mock_urlopen.return_value.read.return_value = b'<p>Image by Example</p>'
        result = webchecks.has_image_credit("https://www.example.com")
        self.assertIn(result, [True, False])


class TestGraderIntegration(unittest.TestCase):
    @patch('student_mode.webpage_grader.check_page_link')
    @patch('student_mode.webpage_grader.check_project_url')
    @patch('student_mode.webpage_grader.get_links', return_value=['about.html'])
    @patch('student_mode.webpage_grader.get_class', return_value='✔️ Class')
    @patch('student_mode.webpage_grader.get_tags', return_value={'h1': 1, 'p': 3, 'img': 3})
    def test_grade_student_output_keys(self, mock_tags, mock_class, mock_links,
                                       mock_project_url, mock_page_link):
        mock_project_url.return_value = 'project status'
        mock_page_link.return_value = 'link status'
        result = webpage_grader.grade_student("https://www.example.com")
        self.assertIn("feedback", result)
        self.assertIn("class_message", result)
        self.assertIn("url_status", result)

    @patch('student_mode.webpage_grader.count_comments', return_value=0)
    @patch('student_mode.webpage_grader.count_broken_tags', return_value={})
    @patch('student_mode.webpage_grader.get_css_file_url', return_value=None)
    @patch('student_mode.webpage_grader.requests.get')
    @patch('student_mode.webpage_grader.check_page_link', return_value='link status')
    @patch('student_mode.webpage_grader.get_links', return_value=['about.html'])
    @patch('student_mode.webpage_grader.get_class', return_value='CSS UPDATE')
    @patch('student_mode.webpage_grader.get_tags', return_value={})
    def test_generate_feedback_html_format(self, mock_tags, mock_class, mock_links,
                                           mock_page_link, mock_get, mock_css_url,
                                           mock_broken_tags, mock_comments):
        mock_get.return_value.text = '<h1>Title</h1>'
        mock_get.return_value.raise_for_status = Mock()
        html_output = webpage_grader.generate_feedback_html("https://www.example.com")
        self.assertIn("<ul>", html_output)
        self.assertIn("https://www.example.com", html_output)


if __name__ == '__main__':
    unittest.main()
