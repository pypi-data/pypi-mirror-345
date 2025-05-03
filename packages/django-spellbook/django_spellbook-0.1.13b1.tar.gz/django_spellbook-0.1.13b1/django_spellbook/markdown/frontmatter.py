# django_spellbook/markdown/frontmatter.py
import yaml
from datetime import datetime
from pathlib import Path
import logging
import os       # Needed for stat constants/attributes potentially
# import platform # Optional: if you want OS-specific logging messages

from django_spellbook.utils import remove_leading_dash, titlefy
from .context import SpellbookContext

logger = logging.getLogger(__name__) # Setup logger

# --- (FrontmatterError, FrontMatterParser.__init__, FrontMatterParser._parse remain the same) ---
class FrontmatterError(Exception):
    """Custom exception for errors during frontmatter parsing."""
    pass

class FrontMatterParser:
    def __init__(self, content: str, file_path: Path):
        self.content = content
        self.file_path = file_path
        self.raw_content = ""
        self.metadata = {}
        self._parse()

    def _parse(self):
        """Parse front matter and content"""
        if self.content.startswith('---'):
            parts = self.content.split('---', 2)
            if len(parts) >= 3:
                try:
                    yaml_content = parts[1].encode('utf-8').decode('utf-8')
                    self.metadata = yaml.safe_load(yaml_content) or {}
                    if not isinstance(self.metadata, dict):
                        logger.warning(f"Frontmatter in {self.file_path} did not parse as a dictionary. Ignoring.")
                        self.metadata = {}
                    self.raw_content = parts[2].strip()
                except (yaml.YAMLError, AttributeError, UnicodeError) as e:
                    logger.warning(f"Error parsing YAML frontmatter in {self.file_path}: {e}. Ignoring frontmatter.")
                    self.metadata = {}
                    self.raw_content = self.content # Use original content if parsing fails
            else:
                # If split doesn't yield 3 parts, assume no valid frontmatter
                self.metadata = {}
                self.raw_content = self.content
        else:
            self.metadata = {}
            self.raw_content = self.content

    def get_context(self, url_path: str) -> SpellbookContext:
        """
        Generates the SpellbookContext, prioritizing file system creation time,
        then frontmatter 'created_at', and finally file modification time for 'created_at'.
        'updated_at' always uses file modification time.
        """
        split_path = url_path.split('/')
        clean_path = [remove_leading_dash(part) for part in split_path]
        clean_url = "/".join(clean_path)

        # --- Timestamp Logic ---
        stats = self.file_path.stat()
        try:
            updated_at_dt = datetime.fromtimestamp(stats.st_mtime)
        except (ValueError, OSError) as e:
            logger.error(f"Failed to get updated_at from mtime {getattr(stats, 'st_mtime', 'N/A')} for {self.file_path}: {e}. Falling back to now.")
            updated_at_dt = datetime.now()

        created_at_dt = None # Initialize
        is_valid_fs_timestamp_found = False # Flag if we found and converted a valid FS time

        # --- Priority 1: File System Creation Time ---

        # Step 1: Try st_birthtime
        if hasattr(stats, 'st_birthtime'):
            birthtime_ts = stats.st_birthtime
            # Check value validity (allows 0, rejects None and negative)
            if birthtime_ts is not None and birthtime_ts >= 0:
                try:
                    created_at_dt = datetime.fromtimestamp(birthtime_ts)
                    logger.debug(f"Using valid file system timestamp (birthtime={birthtime_ts}) for created_at for {self.file_path}")
                    is_valid_fs_timestamp_found = True # Success! Birthtime is valid and converted.
                except (ValueError, OSError) as e:
                    logger.warning(f"Invalid file system timestamp (birthtime='{birthtime_ts}') during conversion for {self.file_path}: {e}. Will try ctime.")
                    # Keep created_at_dt = None, is_valid_fs_timestamp_found = False
            else:
                # birthtime existed but was None or negative
                logger.debug(f"Ignoring invalid file system timestamp (birthtime='{birthtime_ts}') for {self.file_path}. Will try ctime.")
                # Keep created_at_dt = None, is_valid_fs_timestamp_found = False

        # Step 2: Try st_ctime ONLY IF birthtime didn't yield a valid datetime
        if not is_valid_fs_timestamp_found and hasattr(stats, 'st_ctime'):
            ctime_ts = stats.st_ctime
            # Check value validity (allows 0, rejects None and negative)
            if ctime_ts is not None and ctime_ts >= 0:
                try:
                    created_at_dt = datetime.fromtimestamp(ctime_ts)
                    logger.debug(f"Using valid file system timestamp (ctime={ctime_ts}) for created_at for {self.file_path}")
                    is_valid_fs_timestamp_found = True # Success! Ctime is valid and converted.
                except (ValueError, OSError) as e:
                    logger.warning(f"Invalid file system timestamp (ctime='{ctime_ts}') during conversion for {self.file_path}: {e}. Will try frontmatter.")
                    created_at_dt = None # Ensure None if conversion failed
                    # is_valid_fs_timestamp_found remains False
            else:
                 # ctime existed but was None or negative
                 logger.debug(f"Ignoring invalid file system timestamp (ctime='{ctime_ts}') for {self.file_path}. Will try frontmatter.")
                 created_at_dt = None # Ensure None

        # --- Priority 2: Frontmatter 'created_at' ---
        # Only proceed if we didn't get a valid datetime from the file system check above
        if not is_valid_fs_timestamp_found:
             logger.debug(f"No valid file system creation timestamp found for {self.file_path}. Trying frontmatter.")
             # Ensure created_at_dt is None before trying frontmatter
             created_at_dt = None

             fm_created_at = self.metadata.get('created_at')
             if fm_created_at:
                 if isinstance(fm_created_at, datetime):
                    # Handle naive/aware if necessary - assume naive for now based on tests
                    if fm_created_at.tzinfo is not None:
                        logger.warning(f"Frontmatter 'created_at' for {self.file_path} is timezone-aware. Tests assume naive.")
                    created_at_dt = fm_created_at
                    logger.debug(f"Using frontmatter datetime object for created_at for {self.file_path}")

                 elif isinstance(fm_created_at, str):
                    try:
                        if 'T' in fm_created_at or ' ' in fm_created_at and ':' in fm_created_at :
                             created_at_dt = datetime.fromisoformat(fm_created_at.replace(' ', 'T'))
                        else:
                             created_at_dt = datetime.strptime(fm_created_at, '%Y-%m-%d')
                        logger.debug(f"Parsed frontmatter string for created_at for {self.file_path}: {created_at_dt}")
                    except ValueError:
                        logger.warning(f"Could not parse frontmatter 'created_at' string '{fm_created_at}' in {self.file_path}. Will use final fallback.")
                        created_at_dt = None
                 else:
                    logger.warning(f"Unexpected type '{type(fm_created_at)}' for frontmatter 'created_at' in {self.file_path}. Will use final fallback.")
                    created_at_dt = None


        # --- Priority 3: Final Fallback to updated_at ---
        # This fires if created_at_dt is still None after checking FS and Frontmatter
        if created_at_dt is None:
            logger.debug(f"Using final fallback (updated_at) for created_at for {self.file_path}")
            created_at_dt = updated_at_dt
        # --- End Timestamp Logic ---

        # --- Other Metadata ---
        title = titlefy(remove_leading_dash(
            self.metadata.get('title', self.file_path.stem))
        )
        is_public = multi_bool(self.metadata.get('is_public', True))
        tags = self.metadata.get('tags', [])
        excluded_keys = {'title', 'is_public', 'tags', 'created_at', 'updated_at'}
        custom_meta = {k: v for k, v in self.metadata.items() if k not in excluded_keys}
        # --- End Other Metadata ---

        return SpellbookContext(
            title=title,
            created_at=created_at_dt,
            updated_at=updated_at_dt,
            url_path=clean_url,
            raw_content=self.raw_content,
            is_public=is_public,
            tags=tags,
            custom_meta=custom_meta,
            toc={},
            next_page=None,
            prev_page=None
        )

# --- (multi_bool function remains the same) ---
def multi_bool(value):
    """
    Converts various string representations or boolean values to a boolean.

    Handles 'false', 'f', 'no', 'n', '0' as False (case-insensitive)
    and 'true', 't', 'yes', 'y', '1' as True (case-insensitive).
    Otherwise, uses standard Python boolean conversion.

    Args:
        value: The value to convert.

    Returns:
        The boolean representation.
    """
    if isinstance(value, str):
        low_val = value.lower()
        if low_val in ['false', 'f', 'no', 'n', '0']:
            return False
        elif low_val in ['true', 't', 'yes', 'y', '1']:
            return True
    # Fallback to standard boolean conversion for other types or non-matching strings
    return bool(value)