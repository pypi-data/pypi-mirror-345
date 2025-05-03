# tests/test_frontmatter_timestamps.py

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta, timezone
import tempfile
import os
import shutil # For teardown

# Assuming these are in the correct relative paths for your project structure
# Make sure the path to FrontMatterParser is correct based on your project layout
try:
    # Adjust this import based on where your tests are relative to the code
    from django_spellbook.markdown.frontmatter import FrontMatterParser
    # SpellbookContext is needed if you inspect the context type, but not for these tests
    # from django_spellbook.markdown.context import SpellbookContext
except ImportError:
    # Handle potential import errors if structure is different
    print("Error: Could not import FrontMatterParser. Adjust import path.")
    # You might need to add the project root to sys.path in your test runner or here
    # import sys
    # sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    # from django_spellbook.markdown.frontmatter import FrontMatterParser
    raise

# --- Test Constants ---
# Define test constants using UTC then convert to naive for consistency checks
NOW_UTC = datetime.now(timezone.utc)
MTIME_DT_NAIVE = NOW_UTC.replace(tzinfo=None)
CTIME_DT_NAIVE = (NOW_UTC - timedelta(days=1)).replace(tzinfo=None)
BIRTHTIME_DT_NAIVE = (NOW_UTC - timedelta(days=2)).replace(tzinfo=None)
FM_DATETIME_DT_NAIVE = (NOW_UTC - timedelta(days=3)).replace(tzinfo=None)
FM_STRING_DT_NAIVE = (NOW_UTC - timedelta(days=4)).replace(tzinfo=None)

# Timestamps for mocking stat (must be Unix timestamps)
MTIME_TS = NOW_UTC.timestamp()
CTIME_TS = (NOW_UTC - timedelta(days=1)).timestamp()
BIRTHTIME_TS = (NOW_UTC - timedelta(days=2)).timestamp()
# --- End Test Constants ---


# --- Mocking Helper ---
def create_mock_stat_result(mtime=MTIME_TS, ctime=None, birthtime=None):
    """Creates a MagicMock simulating a stat_result object using spec_set."""
    config = {'st_mtime': mtime}
    present_attrs = ['st_mtime']

    if ctime is not None:
        config['st_ctime'] = ctime
        present_attrs.append('st_ctime')
    if birthtime is not None:
        config['st_birthtime'] = birthtime
        present_attrs.append('st_birthtime')

    # Create the mock with spec_set to ensure hasattr works correctly
    # Only attributes defined in present_attrs will exist on the mock
    mock_stat = MagicMock(spec_set=present_attrs, **config)
    return mock_stat
# --- End Mocking Helper ---


# --- Test Class ---
class TestFrontMatterParserTimestamps(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory and a dummy file path
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file_path = Path(self.temp_dir) / "test_timestamps.md"
        # No need to actually create the file as we mock stat

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.temp_dir)

    # --- Test Cases (using naive datetime comparisons) ---

    @patch('pathlib.Path.stat')
    def test_priority_1_birthtime_used(self, mock_stat):
        """CREATED_AT: Test st_birthtime is used when available and valid."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=CTIME_TS, birthtime=BIRTHTIME_TS)
        parser = FrontMatterParser("---", self.temp_file_path) # Minimal content needed
        context = parser.get_context('/test')
        # Compare naive results from fromtimestamp
        self.assertEqual(context.created_at, datetime.fromtimestamp(BIRTHTIME_TS))
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertNotEqual(context.created_at, context.updated_at) # Ensure they are different

    @patch('pathlib.Path.stat')
    def test_priority_2_ctime_used(self, mock_stat):
        """CREATED_AT: Test st_ctime is used when st_birthtime is absent."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=CTIME_TS, birthtime=None) # No birthtime
        parser = FrontMatterParser("---", self.temp_file_path)
        context = parser.get_context('/test')
        # Compare naive results from fromtimestamp
        self.assertEqual(context.created_at, datetime.fromtimestamp(CTIME_TS))
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertNotEqual(context.created_at, context.updated_at)

    @patch('pathlib.Path.stat')
    def test_priority_3_frontmatter_datetime_used(self, mock_stat):
        """CREATED_AT: Test frontmatter naive datetime object used when FS times absent."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=None, birthtime=None) # No FS times
        parser = FrontMatterParser("---", self.temp_file_path)
        # Set naive datetime directly in metadata after parsing
        parser.metadata = {'created_at': FM_DATETIME_DT_NAIVE}
        context = parser.get_context('/test')
        # Compare naive result from frontmatter
        self.assertEqual(context.created_at, FM_DATETIME_DT_NAIVE)
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertNotEqual(context.created_at, context.updated_at)

    @patch('pathlib.Path.stat')
    def test_priority_3_frontmatter_iso_string_used(self, mock_stat):
        """CREATED_AT: Test frontmatter ISO string used when FS times absent."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=None, birthtime=None)
        # Use naive datetime to generate string
        fm_string = FM_STRING_DT_NAIVE.strftime('%Y-%m-%d %H:%M:%S')
        content = f"---\ncreated_at: '{fm_string}'\n---"
        parser = FrontMatterParser(content, self.temp_file_path)
        context = parser.get_context('/test')
        # Compare naive result from parsed string (ignore microseconds)
        self.assertEqual(context.created_at.replace(microsecond=0), FM_STRING_DT_NAIVE.replace(microsecond=0))
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertNotEqual(context.created_at.replace(microsecond=0), context.updated_at.replace(microsecond=0))

    @patch('pathlib.Path.stat')
    def test_priority_3_frontmatter_date_string_used(self, mock_stat):
        """CREATED_AT: Test frontmatter date string (YYYY-MM-DD) used."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=None, birthtime=None)
        fm_date_string = FM_STRING_DT_NAIVE.strftime('%Y-%m-%d')
        content = f"---\ncreated_at: '{fm_date_string}'\n---"
        parser = FrontMatterParser(content, self.temp_file_path)
        context = parser.get_context('/test')
        # Expected is naive datetime at midnight
        expected_dt = datetime.strptime(fm_date_string, '%Y-%m-%d')
        self.assertEqual(context.created_at, expected_dt)
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertNotEqual(context.created_at, context.updated_at)

    @patch('pathlib.Path.stat')
    def test_priority_4_fallback_to_updated_at(self, mock_stat):
        """CREATED_AT: Test fallback to updated_at when FS and frontmatter absent."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=None, birthtime=None)
        content = "---\ntitle: Test\n---" # No created_at key
        parser = FrontMatterParser(content, self.temp_file_path)
        context = parser.get_context('/test')
        # Compare naive results from fromtimestamp (fallback)
        self.assertEqual(context.created_at, datetime.fromtimestamp(MTIME_TS))
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertEqual(context.created_at, context.updated_at) # Should be equal in this case

    # --- Edge Cases and Fallbacks ---

    @patch('pathlib.Path.stat')
    def test_fallback_birthtime_invalid_to_ctime(self, mock_stat):
        """CREATED_AT: Test fallback from invalid birthtime to valid ctime."""
        # Use a timestamp known to cause errors, like negative or non-numeric if possible
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=CTIME_TS, birthtime=-1)
        parser = FrontMatterParser("---", self.temp_file_path)
        context = parser.get_context('/test')
        # Should skip invalid birthtime (-1) and use ctime (naive result)
        self.assertEqual(context.created_at, datetime.fromtimestamp(CTIME_TS))
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertNotEqual(context.created_at, context.updated_at)

    @patch('pathlib.Path.stat')
    def test_fallback_fs_invalid_to_frontmatter(self, mock_stat):
        """CREATED_AT: Test fallback from invalid FS times to valid frontmatter."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=-1, birthtime=-1) # Both FS invalid
        parser = FrontMatterParser("---", self.temp_file_path)
        # Use naive datetime in metadata
        parser.metadata = {'created_at': FM_DATETIME_DT_NAIVE}
        context = parser.get_context('/test')
        # Compare naive result from frontmatter
        self.assertEqual(context.created_at, FM_DATETIME_DT_NAIVE)
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertNotEqual(context.created_at, context.updated_at)

    @patch('pathlib.Path.stat')
    def test_fallback_frontmatter_invalid_string(self, mock_stat):
        """CREATED_AT: Test fallback from invalid frontmatter string to updated_at."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=None, birthtime=None) # No FS times
        content = "---\ncreated_at: 'not-a-valid-date-string'\n---"
        parser = FrontMatterParser(content, self.temp_file_path)
        context = parser.get_context('/test')
        # Compare naive results from fallback (mtime)
        self.assertEqual(context.created_at, datetime.fromtimestamp(MTIME_TS))
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertEqual(context.created_at, context.updated_at)

    @patch('pathlib.Path.stat')
    def test_fallback_frontmatter_wrong_type(self, mock_stat):
        """CREATED_AT: Test fallback from wrong frontmatter type to updated_at."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=None, birthtime=None)
        content = "---\ncreated_at: [2024, 5, 2]\n---" # List, not datetime or string
        parser = FrontMatterParser(content, self.temp_file_path)
        context = parser.get_context('/test')
        # Compare naive results from fallback (mtime)
        self.assertEqual(context.created_at, datetime.fromtimestamp(MTIME_TS))
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        self.assertEqual(context.created_at, context.updated_at)

    @patch('pathlib.Path.stat')
    def test_fs_time_priority_over_frontmatter(self, mock_stat):
        """CREATED_AT: Test valid FS time (birthtime) takes priority over frontmatter."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=CTIME_TS, birthtime=BIRTHTIME_TS) # Valid birthtime
        # Use naive string in frontmatter
        fm_string = FM_STRING_DT_NAIVE.strftime('%Y-%m-%d %H:%M:%S')
        content = f"---\ncreated_at: '{fm_string}'\n---" # Has frontmatter too
        parser = FrontMatterParser(content, self.temp_file_path)
        context = parser.get_context('/test')
        # Compare naive result from FS birthtime
        self.assertEqual(context.created_at, datetime.fromtimestamp(BIRTHTIME_TS))
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))
        # Ensure it didn't use the frontmatter value (comparing naive representations)
        self.assertNotEqual(context.created_at.replace(microsecond=0), FM_STRING_DT_NAIVE.replace(microsecond=0))

    # --- UPDATED_AT Test (Simpler, always mtime) ---
    @patch('pathlib.Path.stat')
    def test_updated_at_always_mtime(self, mock_stat):
        """UPDATED_AT: Test updated_at always uses st_mtime regardless of others."""
        mock_stat.return_value = create_mock_stat_result(mtime=MTIME_TS, ctime=CTIME_TS, birthtime=BIRTHTIME_TS)
        content = f"---\ncreated_at: 'irrelevant'\n---"
        parser = FrontMatterParser(content, self.temp_file_path)
        context = parser.get_context('/test')
        self.assertEqual(context.updated_at, datetime.fromtimestamp(MTIME_TS))

# --- End Test Class ---

# Standard entry point for running tests
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)