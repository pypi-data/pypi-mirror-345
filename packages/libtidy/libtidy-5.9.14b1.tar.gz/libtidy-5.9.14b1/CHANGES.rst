Changelog
=========

5.9.14b1 (2025-05-05)
---------------------
- Add support for Python 3.14
- Drop support for Python 3.9 (due to compatibility issues).
- Update readthedocs's python to version 3.13
- Update tox's base_python to version 3.13
- Tox configuration is now in native (toml) format.
- Add support for PyPy 3.11
- Drop support for PyPy 3.9
- Removed mixed-cased variants of constants 'tidyFormatType_*'.
- | Removed mixed-cased constants 'tidyStrings'.
  | 'TidyStrings' should be used instead.
- | Removed mixed-cased constants 'tidyLocaleMapItem'.
  | 'TidyLocaleMapItem' should be used instead.
- | Added module libtidy.tidy as equivalent of standard tidy.exe.
- | The 'tidy' script was also created during the installation
  | (on Windows as Scripts/tidy.exe) as a convenience.
- Added preliminary tests for libtidy.tidy.
- 100% code linting.
- Copyright year update.
- Setup (dependencies) update.

5.9.14a1 (2025-01-01)
---------------------
- First release.

0.0.0 (2024-10-10)
------------------
- Initial commit.
