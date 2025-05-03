# tests/test_frontmatter_exceptions_log.py  (Or add to an existing test file)

import unittest
from unittest.mock import patch, MagicMock, ANY # ANY helps assert calls without matching exact objects
from pathlib import Path
from datetime import datetime, timedelta, timezone
import tempfile
import os
import shutil
import logging # Import logging to potentially configure or capture logs if needed

# Assuming these are in the correct relative paths for your project structure
try:
    from django_spellbook.markdown.frontmatter import FrontMatterParser
except ImportError:
    print("Error: Could not import FrontMatterParser. Adjust import path.")
    raise

# --- Test Constants (can reuse or redefine minimal set) ---
NOW_UTC = datetime.now(timezone.utc)
MTIME_TS = NOW_UTC.timestamp()
CTIME_TS = (NOW_UTC - timedelta(days=1)).timestamp()
BIRTHTIME_TS = (NOW_UTC - timedelta(days=2)).timestamp()
FIXED_NOW = datetime(2024, 1, 1, 12, 0, 0) # Predictable fallback time
AWARE_DATETIME = datetime(2024, 2, 1, 10, 30, 0, tzinfo=timezone.utc)
# --- End Test Constants ---


# --- Mocking Helper (Simplified as needed for these tests) ---
def create_minimal_mock_stat(mtime=MTIME_TS, ctime=None, birthtime=None):
    """Creates a MagicMock simulating stat_result for exception tests."""
    config = {'st_mtime': mtime}
    present_attrs = ['st_mtime']
    if ctime is not None:
        config['st_ctime'] = ctime
        present_attrs.append('st_ctime')
    if birthtime is not None:
        config['st_birthtime'] = birthtime
        present_attrs.append('st_birthtime')
    # spec_set ensures hasattr works correctly for defined attributes
    mock_stat = MagicMock(spec_set=present_attrs, **config)
    return mock_stat
# --- End Mocking Helper ---


# --- New Test Class for Exceptions and Logging ---
# Patch the logger within the module where it's defined and used
@patch('django_spellbook.markdown.frontmatter.logger', autospec=True)
class TestFrontMatterParserExceptionsAndLogging(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file_path = Path(self.temp_dir) / "test_exceptions.md"

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # --- Exception Test Cases ---

    @patch('django_spellbook.markdown.frontmatter.datetime') # Mock datetime module used in frontmatter.py
    @patch('pathlib.Path.stat')
    def test_updated_at_exception_fallback_and_log(self, mock_stat_method, mock_datetime, mock_logger):
        """UPDATED_AT: Test fallback and error log when fromtimestamp fails for mtime."""
        # 1. Setup Mocks
        mock_stat_method.return_value = create_minimal_mock_stat(mtime=MTIME_TS)
        # Make fromtimestamp raise an error *only* for MTIME_TS
        mock_datetime.fromtimestamp.side_effect = lambda ts: (_ for _ in ()).throw(ValueError("Invalid mtime")) if ts == MTIME_TS else datetime.fromtimestamp(ts)
        # Mock datetime.now() used in the except block
        mock_datetime.now.return_value = FIXED_NOW

        # 2. Run Code
        parser = FrontMatterParser("---", self.temp_file_path)
        context = parser.get_context('/test')

        # 3. Assertions
        # Assert fallback value was used
        self.assertEqual(context.updated_at, FIXED_NOW)
        # Assert logger.error was called
        mock_logger.error.assert_called_once()
        # Assert basic log message structure (can be more specific)
        self.assertIn(f"Failed to get updated_at from mtime {MTIME_TS}", mock_logger.error.call_args[0][0])
        self.assertIn("Falling back to now", mock_logger.error.call_args[0][0])

    @patch('django_spellbook.markdown.frontmatter.datetime')
    @patch('pathlib.Path.stat')
    def test_birthtime_conversion_exception_and_log(self, mock_stat_method, mock_datetime, mock_logger):
        """CREATED_AT: Test warning log when fromtimestamp fails for birthtime."""
        # 1. Setup Mocks
        # Provide valid birthtime >= 0, but make conversion fail
        mock_stat_method.return_value = create_minimal_mock_stat(mtime=MTIME_TS, ctime=CTIME_TS, birthtime=BIRTHTIME_TS)
        # Raise error only for BIRTHTIME_TS
        mock_datetime.fromtimestamp.side_effect = lambda ts: (_ for _ in ()).throw(OSError("Bad birthtime")) if ts == BIRTHTIME_TS else datetime.fromtimestamp(ts)

        # 2. Run Code
        parser = FrontMatterParser("---", self.temp_file_path)
        context = parser.get_context('/test')

        # 3. Assertions
        # Assert logger.warning was called for birthtime
        mock_logger.warning.assert_any_call(
            f"Invalid file system timestamp (birthtime='{BIRTHTIME_TS}') during conversion for {self.temp_file_path}: Bad birthtime. Will try ctime."
        )
        # Assert that it fell back correctly (should have used CTIME in this case)
        # Check if ctime conversion was attempted (and succeeded due to side_effect)
        mock_datetime.fromtimestamp.assert_any_call(CTIME_TS)
        self.assertEqual(context.created_at, datetime.fromtimestamp(CTIME_TS))
        # Ensure the error log for updated_at wasn't called
        mock_logger.error.assert_not_called()

    @patch('django_spellbook.markdown.frontmatter.datetime')
    @patch('pathlib.Path.stat')
    def test_ctime_conversion_exception_and_log(self, mock_stat_method, mock_datetime, mock_logger):
        """CREATED_AT: Test warning log when fromtimestamp fails for ctime."""
        # 1. Setup Mocks
        # No birthtime, valid ctime >= 0, make ctime conversion fail
        mock_stat_method.return_value = create_minimal_mock_stat(mtime=MTIME_TS, ctime=CTIME_TS, birthtime=None)
        # Raise error only for CTIME_TS
        mock_datetime.fromtimestamp.side_effect = lambda ts: (_ for _ in ()).throw(ValueError("Bad ctime")) if ts == CTIME_TS else datetime.fromtimestamp(ts)

        # 2. Run Code
        parser = FrontMatterParser("---\nfoo: bar\n---", self.temp_file_path) # No frontmatter date
        context = parser.get_context('/test')

        # 3. Assertions
        # Assert logger.warning was called for ctime
        mock_logger.warning.assert_any_call(
            f"Invalid file system timestamp (ctime='{CTIME_TS}') during conversion for {self.temp_file_path}: Bad ctime. Will try frontmatter."
        )
        # Assert that it fell back correctly (should use updated_at as no frontmatter date)
        # Check mtime conversion was attempted (and succeeded)
        mock_datetime.fromtimestamp.assert_any_call(MTIME_TS)
        self.assertEqual(context.created_at, datetime.fromtimestamp(MTIME_TS))
        # Ensure the error log for updated_at wasn't called
        mock_logger.error.assert_not_called()


    # --- Logging Test Case ---

    @patch('pathlib.Path.stat') # Still need to mock stat
    def test_timezone_aware_frontmatter_log(self, mock_stat_method, mock_logger):
        """LOGGING: Test warning log for timezone-aware frontmatter datetime."""
        # 1. Setup Mocks
        # Minimal stat result, no FS creation times to force frontmatter check
        mock_stat_method.return_value = create_minimal_mock_stat(mtime=MTIME_TS, ctime=None, birthtime=None)

        # 2. Run Code
        parser = FrontMatterParser("---", self.temp_file_path)
        # Inject aware datetime into metadata *after* parsing
        parser.metadata = {'created_at': AWARE_DATETIME}
        context = parser.get_context('/test')

        # 3. Assertions
        # Assert logger.warning was called with the specific message
        mock_logger.warning.assert_any_call(
             f"Frontmatter 'created_at' for {self.temp_file_path} is timezone-aware. Tests assume naive."
        )
        # Assert the context still uses the aware datetime provided
        self.assertEqual(context.created_at, AWARE_DATETIME)
        # Ensure other logs not called unexpectedly
        mock_logger.error.assert_not_called()

# --- End Test Class ---


# Standard entry point for running tests
if __name__ == '__main__':
    # Configure logging level if you want to see logs during tests (optional)
    # logging.basicConfig(level=logging.DEBUG)
    unittest.main(argv=['first-arg-is-ignored'], exit=False)