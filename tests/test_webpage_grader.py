import csv
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch
from shared import utils
from shared import webchecks
from shared import browser
from student_mode import webpage_grader
from teacher_mode import batch_grader
import app as flask_app

TEST_URL = "https://codeprojects.org/projects/weblab/JONWyX5NqCkqfKdglTZSkoL6S3cHatmg3MFurTWWDXY"


def successful_page_status(content='<h1>Title</h1>'):
    return {
        'ok': True,
        'status_code': 200,
        'reason': 'OK',
        'label': 'HTTP Status: 200 OK',
        'message': None,
        'content': content,
    }


def failed_page_status(status_code, reason, message):
    return {
        'ok': False,
        'status_code': status_code,
        'reason': reason,
        'label': f'HTTP Status: {status_code} {reason}',
        'message': message,
        'content': '',
    }


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

    @patch('shared.utils.requests.get')
    def test_page_status_200_ok(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.reason = 'OK'
        mock_get.return_value.text = '<h1>Working page</h1>'

        result = utils.get_page_status('https://www.example.com')

        self.assertTrue(result['ok'])
        self.assertEqual(result['label'], 'HTTP Status: 200 OK')
        self.assertEqual(result['content'], '<h1>Working page</h1>')

    @patch('shared.utils.requests.get')
    def test_page_status_403_forbidden(self, mock_get):
        mock_get.return_value.status_code = 403
        mock_get.return_value.reason = 'Forbidden'
        mock_get.return_value.text = ''

        result = utils.get_page_status('https://www.example.com')

        self.assertFalse(result['ok'])
        self.assertEqual(result['label'], 'HTTP Status: 403 Forbidden')
        self.assertIn('server blocked the request', result['message'])

    @patch('shared.utils.requests.get')
    def test_page_status_404_not_found(self, mock_get):
        mock_get.return_value.status_code = 404
        mock_get.return_value.reason = 'Not Found'
        mock_get.return_value.text = ''

        result = utils.get_page_status('https://www.example.com/missing')

        self.assertFalse(result['ok'])
        self.assertEqual(result['label'], 'HTTP Status: 404 Not Found')
        self.assertIn('could not find this page', result['message'])

    @patch('shared.utils.requests.get',
           side_effect=utils.requests.exceptions.Timeout)
    def test_page_status_timeout(self, mock_get):
        result = utils.get_page_status('https://www.example.com')

        self.assertFalse(result['ok'])
        self.assertEqual(result['label'], 'Connection Error')
        self.assertIn('timed out', result['message'])

    @patch('shared.utils.requests.get',
           side_effect=utils.requests.exceptions.ConnectionError)
    def test_page_status_connection_error(self, mock_get):
        result = utils.get_page_status('https://www.example.com')

        self.assertFalse(result['ok'])
        self.assertEqual(result['label'], 'Connection Error')
        self.assertEqual(result['message'], 'Site Sensei could not reach this webpage.')


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
    def test_get_links_returns_list(self, mock_urlopen):
        mock_urlopen.return_value.read.return_value = b'<a href="about.html">About</a>'
        links = webchecks.get_links("https://www.example.com")
        self.assertEqual(links, ['about.html'])

    @patch('shared.webchecks.urllib.request.urlopen')
    def test_get_links_skips_missing_href(self, mock_urlopen):
        mock_urlopen.return_value.read.return_value = (
            b'<a>Missing</a><a href="about.html">About</a>'
        )

        self.assertEqual(
            webchecks.get_links("https://www.example.com"),
            ['about.html'],
        )

    @patch('shared.webchecks.urllib.request.urlopen',
           side_effect=urllib.error.URLError('offline'))
    def test_get_links_returns_empty_list_when_page_unavailable(self, mock_urlopen):
        self.assertEqual(webchecks.get_links("https://www.example.com"), [])

    @patch('shared.webchecks.requests.get')
    def test_get_class_output(self, mock_get):
        mock_get.return_value.text = '<p class="intro">Text</p>'
        msg = webchecks.get_class("https://www.example.com")
        self.assertIsInstance(msg, str)

    @patch('shared.webchecks.requests.get',
           side_effect=webchecks.requests.RequestException('offline'))
    def test_get_class_returns_message_when_page_unavailable(self, mock_get):
        msg = webchecks.get_class("https://www.example.com")

        self.assertIsInstance(msg, str)
        self.assertIn('could not be loaded', msg)

    @patch('shared.webchecks.urllib.request.urlopen')
    def test_has_image_credit_boolean(self, mock_urlopen):
        mock_urlopen.return_value.read.return_value = b'<p>Image by Example</p>'
        result = webchecks.has_image_credit("https://www.example.com")
        self.assertIn(result, [True, False])

    @patch('shared.webchecks.urllib.request.urlopen',
           side_effect=urllib.error.URLError('offline'))
    def test_has_image_credit_returns_false_when_page_unavailable(self, mock_urlopen):
        self.assertFalse(webchecks.has_image_credit("https://www.example.com"))


class TestGraderIntegration(unittest.TestCase):
    @patch('student_mode.webpage_grader.check_page_link')
    @patch('student_mode.webpage_grader.get_links', return_value=['about.html'])
    @patch('student_mode.webpage_grader.get_class', return_value='✔️ Class')
    @patch('student_mode.webpage_grader.get_tags', return_value={'h1': 1, 'p': 3, 'img': 3})
    def test_grade_student_output_keys(self, mock_tags, mock_class, mock_links,
                                       mock_page_link):
        mock_page_link.return_value = 'link status'
        result = webpage_grader.grade_student(
            "https://www.example.com",
            page_status=successful_page_status(),
        )
        self.assertIn("feedback", result)
        self.assertIn("class_message", result)
        self.assertIn("url_status", result)

    @patch('student_mode.webpage_grader.get_tags')
    def test_grade_student_stops_after_http_failure(self, mock_tags):
        status = failed_page_status(
            404,
            'Not Found',
            'Site Sensei could not find this page.',
        )

        result = webpage_grader.grade_student(
            'https://www.example.com/missing.html',
            page_status=status,
        )

        self.assertEqual(result['url_status'], 'HTTP Status: 404 Not Found')
        self.assertEqual(result['feedback'], '❌ Page not analyzed')
        mock_tags.assert_not_called()

    @patch('student_mode.webpage_grader.count_comments', return_value=0)
    @patch('student_mode.webpage_grader.count_broken_tags', return_value={})
    @patch('student_mode.webpage_grader.get_css_file_url', return_value=None)
    @patch('student_mode.webpage_grader.has_image_credit', return_value=True)
    @patch('student_mode.webpage_grader.check_page_link', return_value='link status')
    @patch('student_mode.webpage_grader.get_links', return_value=['about.html'])
    @patch('student_mode.webpage_grader.get_class', return_value='CSS UPDATE')
    @patch('student_mode.webpage_grader.get_tags', return_value={})
    def test_generate_feedback_html_format(self, mock_tags, mock_class, mock_links,
                                           mock_page_link, mock_image_credit,
                                           mock_css_url, mock_broken_tags,
                                           mock_comments):
        html_output = webpage_grader.generate_feedback_html(
            "https://www.example.com",
            page_status=successful_page_status(),
        )
        self.assertIn("<ul>", html_output)
        self.assertIn("https://www.example.com", html_output)
        self.assertIn("HTTP Status: 200 OK", html_output)

    @patch('student_mode.webpage_grader.count_comments', return_value=0)
    @patch('student_mode.webpage_grader.count_broken_tags', return_value={})
    @patch('student_mode.webpage_grader.check_css_properties', return_value={
        'used': [f'property-{index}' for index in range(8)],
        'missing': [],
        'selector_count': 2,
        'message': 'CSS details',
    })
    @patch('student_mode.webpage_grader.get_css_file_url',
           return_value='https://www.example.com/style.css')
    @patch('student_mode.webpage_grader.has_image_credit', return_value=False)
    @patch('student_mode.webpage_grader.check_page_link')
    @patch('student_mode.webpage_grader.get_links', return_value=[])
    @patch('student_mode.webpage_grader.get_class', return_value='No classes')
    @patch('student_mode.webpage_grader.get_tags', return_value={
        'h1': 1, 'h2': 1, 'p': 1, 'img': 1,
        'li': 1, 'a': 1, 'br': 1, 'h3': 1,
    })
    def test_feedback_shows_rubric_tag_and_css_targets(
            self, mock_tags, mock_class, mock_links, mock_page_link,
            mock_image_credit, mock_css_url, mock_css_properties,
            mock_broken_tags, mock_comments):
        html_output = webpage_grader.generate_feedback_html(
            'https://www.example.com',
            page_status=successful_page_status(),
        )

        self.assertIn('HTML tag types: 8 (target: 8+)', html_output)
        self.assertIn('CSS properties: 8 (target: 8+)', html_output)

    @patch('student_mode.webpage_grader.count_comments', return_value=0)
    @patch('student_mode.webpage_grader.count_broken_tags', return_value={})
    @patch('student_mode.webpage_grader.get_css_file_url', return_value=None)
    @patch('student_mode.webpage_grader.has_image_credit', return_value=False)
    @patch('student_mode.webpage_grader.check_page_link')
    @patch('student_mode.webpage_grader.get_class', return_value='No classes')
    @patch('student_mode.webpage_grader.get_tags', return_value={})
    def test_generate_feedback_handles_no_links(
            self, mock_tags, mock_class, mock_page_link, mock_image_credit,
            mock_css_url, mock_broken_tags, mock_comments):
        with patch('student_mode.webpage_grader.get_links', return_value=[]):
            html_output = webpage_grader.generate_feedback_html(
                'https://www.example.com/index.html',
                page_status=successful_page_status(),
            )

        mock_page_link.assert_not_called()
        self.assertIn('Missing or invalid link to another HTML page', html_output)

    @patch('student_mode.webpage_grader.count_comments', return_value=0)
    @patch('student_mode.webpage_grader.count_broken_tags', return_value={})
    @patch('student_mode.webpage_grader.get_css_file_url', return_value=None)
    @patch('student_mode.webpage_grader.has_image_credit', return_value=False)
    @patch('student_mode.webpage_grader.check_page_link', return_value='link status')
    @patch('student_mode.webpage_grader.get_links',
           return_value=[None, '', 'about.html'])
    @patch('student_mode.webpage_grader.get_class', return_value='No classes')
    @patch('student_mode.webpage_grader.get_tags', return_value={})
    def test_generate_feedback_ignores_invalid_hrefs(
            self, mock_tags, mock_class, mock_links, mock_page_link,
            mock_image_credit, mock_css_url, mock_broken_tags,
            mock_comments):
        webpage_grader.generate_feedback_html(
            'https://www.example.com/projects/index.html',
            page_status=successful_page_status(),
        )

        mock_page_link.assert_called_once_with(
            'https://www.example.com/projects/about.html'
        )

    @patch('student_mode.webpage_grader.get_tags')
    @patch('student_mode.webpage_grader.get_page_status')
    def test_generate_feedback_stops_when_page_unavailable(
            self, mock_status, mock_tags):
        mock_status.return_value = {
            'ok': False,
            'status_code': None,
            'reason': None,
            'label': 'Connection Error',
            'message': 'Site Sensei could not reach this webpage.',
            'content': None,
        }

        html_output = webpage_grader.generate_feedback_html(
            'https://www.example.com/unavailable.html'
        )

        self.assertIn('Connection Error', html_output)
        self.assertIn('could not reach this webpage', html_output)
        self.assertNotIn('Images:', html_output)
        mock_tags.assert_not_called()

    @patch('student_mode.webpage_grader.get_tags')
    def test_http_failures_do_not_produce_grading_results(self, mock_tags):
        cases = (
            (403, 'Forbidden', 'server blocked the request'),
            (404, 'Not Found', 'could not find this page'),
            (500, 'Internal Server Error', 'request was unsuccessful'),
        )
        for status_code, reason, expected_message in cases:
            with self.subTest(status_code=status_code):
                status = failed_page_status(
                    status_code,
                    reason,
                    f'Site Sensei {expected_message}.',
                )
                html_output = webpage_grader.generate_feedback_html(
                    'https://www.example.com/page.html',
                    page_status=status,
                )

                self.assertIn(f'HTTP Status: {status_code} {reason}', html_output)
                self.assertIn(expected_message, html_output)
                self.assertNotIn('Paragraphs:', html_output)
        mock_tags.assert_not_called()


class TestBatchGrader(unittest.TestCase):
    @patch('teacher_mode.batch_grader.get_page_status',
           return_value=successful_page_status())
    @patch('teacher_mode.batch_grader.generate_feedback_html',
           side_effect=ValueError('malformed student page'))
    @patch('teacher_mode.batch_grader.count_comments', return_value=0)
    @patch('teacher_mode.batch_grader.count_broken_tags', return_value={})
    @patch('teacher_mode.batch_grader.get_css_file_url', return_value=None)
    @patch('teacher_mode.batch_grader.get_tags', return_value={})
    def test_malformed_student_page_does_not_break_batch_row(
            self, mock_tags, mock_css_url, mock_broken_tags,
            mock_comments, mock_feedback, mock_status):
        result = batch_grader.analyze_student_row({
            'name': 'Student',
            'url': 'https://www.example.com/broken.html',
        })

        self.assertEqual(result['name'], 'Student')
        self.assertIn('Could not generate detailed feedback', result['feedback_html'])

    @patch('teacher_mode.batch_grader.generate_feedback_html')
    @patch('teacher_mode.batch_grader.get_tags')
    @patch('teacher_mode.batch_grader.get_page_status')
    def test_retrieval_failures_record_status_without_grading_student(
            self, mock_status, mock_tags, mock_feedback):
        statuses = (
            failed_page_status(
                403,
                'Forbidden',
                'Site Sensei could not analyze this page because the server blocked the request.',
            ),
            failed_page_status(
                404,
                'Not Found',
                'Site Sensei could not find this page.',
            ),
            {
                'ok': False, 'status_code': None, 'reason': None,
                'label': 'Connection Error',
                'message': 'Site Sensei could not reach this webpage because the request timed out.',
                'content': None,
            },
            {
                'ok': False, 'status_code': None, 'reason': None,
                'label': 'Connection Error',
                'message': 'Site Sensei could not reach this webpage.',
                'content': None,
            },
        )
        for status in statuses:
            with self.subTest(status=status['label'], message=status['message']):
                mock_status.return_value = status
                mock_feedback.return_value = (
                    f"<p><strong>{status['label']}</strong></p>"
                )

                result = batch_grader.analyze_student_row({
                    'name': 'Student',
                    'url': 'https://www.example.com/page.html',
                })

                self.assertEqual(result['page_status'], status['label'])
                self.assertEqual(result['paragraph_count'], 'N/A')
                self.assertIn(status['label'], result['feedback_html'])
        mock_tags.assert_not_called()

    @patch('teacher_mode.batch_grader.get_page_status')
    def test_batch_continues_after_multiple_retrieval_failures(self, mock_status):
        mock_status.side_effect = [
            failed_page_status(
                403,
                'Forbidden',
                'Site Sensei could not analyze this page because the server blocked the request.',
            ),
            {
                'ok': False, 'status_code': None, 'reason': None,
                'label': 'Connection Error',
                'message': 'Site Sensei could not reach this webpage.',
                'content': None,
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_csv = temp_path / 'students.csv'
            output_csv = temp_path / 'grades.csv'
            output_html = temp_path / 'feedback.html'
            with input_csv.open('w', newline='', encoding='utf-8') as csv_out:
                writer = csv.DictWriter(csv_out, fieldnames=['name', 'url'])
                writer.writeheader()
                writer.writerows([
                    {'name': 'Blocked', 'url': 'https://example.com/blocked'},
                    {'name': 'Offline', 'url': 'https://example.com/offline'},
                ])

            batch_grader.grade_from_csv(input_csv, output_csv, output_html)

            with output_csv.open(newline='', encoding='utf-8') as csv_in:
                rows = list(csv.DictReader(csv_in))
            feedback = output_html.read_text(encoding='utf-8')

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['page_status'], 'HTTP Status: 403 Forbidden')
        self.assertEqual(rows[1]['page_status'], 'Connection Error')
        self.assertIn('Blocked', feedback)
        self.assertIn('Offline', feedback)


class TestStudentRoutes(unittest.TestCase):
    def setUp(self):
        flask_app.app.config.update(TESTING=True, SECRET_KEY='test-secret')
        self.client = flask_app.app.test_client()

    def test_get_student_returns_upload_page(self):
        response = self.client.get('/student')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student Self Check', response.data)
        self.assertIn(b'Current grading profile', response.data)
        self.assertIn(b'View example rubric', response.data)
        self.assertIn(b'require teacher review', response.data)
        self.assertIn(b'/static/assets/favicon-32x32.png', response.data)
        self.assertIn(b'/static/assets/favicon-16x16.png', response.data)
        self.assertIn(b'/static/assets/apple-touch-icon.png', response.data)
        self.assertIn(b'Built for student HTML/CSS feedback', response.data)
        self.assertIn(
            b'href="https://github.com/parcheesime/site-sensei" '
            b'target="_blank" rel="noopener noreferrer"',
            response.data,
        )
        self.assertIn(b'>Example Rubric</a>', response.data)

    def test_favicon_assets_are_served(self):
        for filename in (
            'favicon-32x32.png',
            'favicon-16x16.png',
            'apple-touch-icon.png',
        ):
            with self.subTest(filename=filename):
                response = self.client.get(f'/static/assets/{filename}')

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, 'image/png')
                self.assertTrue(response.data.startswith(b'\x89PNG\r\n\x1a\n'))

    def test_example_rubric_pdf_is_available(self):
        response = self.client.get('/rubrics/html-mini-web-page-rubric.pdf')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')
        self.assertTrue(response.data.startswith(b'%PDF'))

    def test_blank_url_returns_upload_page_with_validation_message(self):
        response = self.client.post('/student', data={'url': '   '})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter a project URL.', response.data)
        self.assertIn(b'Student Self Check', response.data)

    @patch('app.generate_feedback_html', return_value='<p>Grader result</p>')
    def test_valid_url_calls_grader_and_renders_results(self, mock_grader):
        url = 'https://student.example/project'

        response = self.client.post('/student', data={'url': f'  {url}  '})

        self.assertEqual(response.status_code, 200)
        mock_grader.assert_called_once_with(url)
        self.assertIn(b'Student Feedback', response.data)
        self.assertIn(url.encode(), response.data)
        self.assertIn(b'<p>Grader result</p>', response.data)



class TestTeacherRoutes(unittest.TestCase):
    def setUp(self):
        flask_app.app.config.update(TESTING=True, SECRET_KEY='test-secret')
        self.client = flask_app.app.test_client()

    @patch.dict('os.environ', {}, clear=True)
    def test_teacher_mode_is_unavailable_without_password(self):
        for route in (
            '/teacher',
            '/teacher-batch',
            '/teacher-results',
            '/download/csv',
            '/download/html',
        ):
            with self.subTest(route=route):
                response = self.client.get(route)

                self.assertEqual(response.status_code, 503)
                self.assertIn(b'Teacher Mode Unavailable', response.data)
                self.assertIn(b'contact me for a demonstration', response.data)

    @patch.dict('os.environ', {'TEACHER_PASSWORD': 'classroom-secret'}, clear=True)
    def test_teacher_mode_accepts_configured_password(self):
        response = self.client.post(
            '/teacher',
            data={'password': 'classroom-secret'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/teacher-batch')

    @patch.dict('os.environ', {'TEACHER_PASSWORD': 'classroom-secret'}, clear=True)
    def test_teacher_mode_rejects_incorrect_password(self):
        response = self.client.post('/teacher', data={'password': 'admin'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect password. Try again.', response.data)

    @patch.dict('os.environ', {'TEACHER_PASSWORD': 'classroom-secret'}, clear=True)
    def test_teacher_batch_is_available_when_configured(self):
        response = self.client.get('/teacher-batch')

        self.assertEqual(response.status_code, 200)


class TestContainerConfiguration(unittest.TestCase):
    @patch.dict('os.environ', {}, clear=True)
    def test_default_flask_bind_configuration(self):
        self.assertEqual(flask_app.get_server_config(), {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': False,
        })

    @patch.dict('os.environ', {
        'FLASK_HOST': '127.0.0.1',
        'PORT': '5050',
        'FLASK_DEBUG': 'true',
    }, clear=True)
    def test_environment_flask_bind_configuration(self):
        self.assertEqual(flask_app.get_server_config(), {
            'host': '127.0.0.1',
            'port': 5050,
            'debug': True,
        })

    @patch('shared.browser.webdriver.Remote')
    @patch.dict('os.environ', {'SELENIUM_URL': 'http://selenium:4444'}, clear=True)
    def test_remote_selenium_url_selection(self, mock_remote):
        driver = browser.create_driver()
        self.assertIs(driver, mock_remote.return_value)
        self.assertEqual(
            mock_remote.call_args.kwargs['command_executor'],
            'http://selenium:4444',
        )

    @patch('shared.browser.webdriver.Remote', side_effect=Exception('offline'))
    @patch.dict('os.environ', {'SELENIUM_URL': 'http://selenium:4444'}, clear=True)
    def test_remote_selenium_unavailable_is_controlled(self, mock_remote):
        with self.assertRaisesRegex(
            browser.BrowserUnavailableError,
            'Selenium browser is unavailable',
        ):
            browser.create_driver()


if __name__ == '__main__':
    unittest.main()
