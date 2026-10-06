# ABOUTME: Verifies Chrome process ownership and shutdown using a real browser.
# ABOUTME: Checks driver binary version parsing without deprecated APIs.
import gc
import tempfile
import unittest
from pathlib import Path

import undetected_chromedriver as uc
from undetected_chromedriver.patcher import Patcher


class BrowserResourcesTest(unittest.TestCase):
    def test_quit_reaps_browser_and_closes_pipes(self):
        browser = uc.Chrome(headless=True, no_sandbox=True, use_subprocess=True)
        try:
            browser.get('data:text/html,<title>resources</title>')
            self.assertEqual(browser.title, 'resources')
            process = browser.browser_process
            self.assertIsNone(process.poll())
            browser.quit()
            self.assertIsNotNone(process.returncode)
            self.assertTrue(all(pipe.closed for pipe in
                                (process.stdin, process.stdout, process.stderr)))
            browser.quit()
        finally:
            browser.quit()
        del browser
        gc.collect()

    def test_parse_driver_binary_version(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / 'chromedriver'
            binary.write_bytes(b'platform_handle\x00content\x00154.0.8012.3\x00')
            patcher = Patcher(executable_path=str(binary))
            version = patcher.parse_exe_version()
            self.assertEqual(str(version), '154.0.8012.3')
            self.assertEqual(version.release[0], 154)


if __name__ == '__main__':
    unittest.main()
