
Changelog
=========
..
   All enhancements and patches to Feed2Fedi will be documented
   in this file. It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).

Unreleased
----------

See the fragment files in the `changelog.d directory`_.

.. _changelog.d directory: https://codeberg.org/MarvinsMastodonTools/feed2fedi/src/branch/main/changelog.d


.. scriv-insert-here

.. _changelog-3.2.0:

3.2.0 — 2025-05-05
==================

Changed
-------

- Updated pre-commit, CI and dependencies versions.

- Implemented `whenever`_ use instead of datetime.

.. _whenever: https://whenever.rtfd.io/

.. _changelog-3.1.2:

3.1.2 — 2024-12-24
==================

Added
-----

- Added first tests... more to come over time.

Changed
-------

- Updated dependecies versions

- Update CI / Nox with more checks

.. _changelog-3.1.1:

3.1.1 — 2024-10-28
==================

Changed
-------

- Updated dependencies versions

Fixed
-----

- Address `issue #24`_ for GotoSocial servers at least.

.. _issue #24: https://codeberg.org/marvinsmastodontools/feed2fedi/issues/24

.. _changelog-3.1.0:

3.1.0 — 2024-05-04
==================

Added
-----

- Added checking `<link [...]>` tags as well for attachments to upload. This might address issue #24

- Added a command line option to limit the number of statuses to post. See `feed2fedi --help`

Changed
-------

- Updated dependencies

.. _changelog-3.0.0:

3.0.0 — 2024-04-08
==================

Breaking
--------

- `Feed2Fedi` now requires Python versions 3.9, 3.10, 3.11, or 3.12. We no longer support Python 3.8.

Added
-----

- Now using `stamina`_ to automatically retry failed API calls.

- Now checking mime type of attachment against list of supported mime types as reported by instance server.

- Now catching exception when using Ctrl-C to stop program.

.. _stamina: https://stamina.hynek.me/en/stable/

Changed
-------

- Removed dependence on `arrow` and using `datetime` and related functions

- Changed to using `httpx`_ instead of `aiohttp`.

.. _httpx: https://www.python-httpx.org/

- Trying out `rye`_ for dependency and virtual environment management during development.

.. _rye: https://rye-up.com/

- Reformated "Server 'cool down'" message

- Update dependencies versions

Removed
-------

- `Safety` from CI. `pip-audit`_ covers the same and is more up to date than the free version of safety.

.. _pip-audit: https://pypi.org/project/pip-audit/

.. _changelog-2.0.0:

2.0.0 — 2024-01-17
==================

Breaking
--------

- Implement `msgspec` for loading configuration. Unfortunatley this introduces a breaking change with how
  boolean values a configured.
  Specifically, the value for the configuration field `bot_post_media` needs to be changed from "True" or "False"
  to `true`, or `false` respectively.

Added
-----

- `MrClon`_ added feed filters to filter some text with configurable actions.
  (Details see PRs #18 and #19)

Changed
-------

- Move css selector for images to config (thank you `MrClon`_ for `pull request #16`_)
  With this change users can determine what images from original feed should be posted.
  Now default is img[src] which mean all img tags with src attribute

.. _pull request #16: https://codeberg.org/MarvinsMastodonTools/feed2fedi/pulls/16

- Updated dependencies versions

Fixed
-----

- Re-factored a little to address issue #17

Security
--------

- Address potential vulnerability in dependency.
  Details: https://github.com/advisories/GHSA-j225-cvw7-qrx7

.. _changelog-1.0.0:

1.0.0 — 2023-12-07
==================

Breaking
--------

- Changed configuration file format to `JSON`

Added
-----

- Conversion tool to convert old format config file to new format config file. Usage is as follows:

.. code-block:: console

    feed2fedi_convert_config --config-file config.ini --config-json /tmp/config.json

  `--config-file` nominates the existing old-style config file, while
  `--config-json` nominates the new style config file to be generated.

- Configurable templating of posts. Thank you to `MrClon`_ (`issue #5`_)

.. _MrClon: https://codeberg.org/MrClon
.. _issue #5: https://codeberg.org/MarvinsMastodonTools/feed2fedi/issues/5

Changed
-------

- Updated dependencies versions

- Now allowing multiple attachments to be included with each post

- Move post template to config (thank you `MrClon`_ for `pull request #8`_ and `#9`_)

.. _pull request #8: https://codeberg.org/MarvinsMastodonTools/feed2fedi/pulls/8
.. _#9: https://codeberg.org/MarvinsMastodonTools/feed2fedi/pulls/9

- Using BeautifulSoup4 to determine image urls (thank you `MrClon`_ for `pull request #10`_)

.. _pull request #10: https://codeberg.org/MarvinsMastodonTools/feed2fedi/pulls/10

- Reorder entries in feed for predictable order (thank you `MrClon`_ for `pull request #11`_)

.. _pull request #11: https://codeberg.org/MarvinsMastodonTools/feed2fedi/pulls/11

Fixed
-----

- Now able to process feeds with `%` in the feed url. (thank you `MrClon`_ for `pull request #7`_)

.. _pull request #7: https://codeberg.org/MarvinsMastodonTools/feed2fedi/pulls/7

.. _changelog-0.4.1:

0.4.1 — 2023-10-23
==================

Added
-----

- Weekly check to CI. This checks for vulnerabilities using pip-audit.

Changed
-------

- Using typer now for cli options definition
- Updated dependencies versions

Removed
-------

- doc and dev dependencies. These are handled within nox now

.. _changelog-0.4.0:

0.4.0 — 2023-08-24
==================

Added
-----

- Ability to define and include a prefix for any feed items being posted. This is defined per feed.

Changed
-------

- Updated dependencies versions

.. _changelog-0.3.3:

0.3.3 — 2023-05-16
==================

Changed
-------

- Updated dependencies.

.. _changelog-0.3.2:

0.3.2 — 2023-03-04
==================

Changed
-------

- Changed bot setting to only post with media to config if media should be posted or not.

.. _changelog-0.3.1:

0.3.1 — 2023-03-04
==================

Changed
-------

- Updated dependencies, in particular minimal-activitypub. This should fix the error when uploading an image with mimte-type "image/webp"

.. _changelog-0.3.0:

0.3.0 — 2023-03-02
==================

This is the first version I think is ready for use. It's still a bit rough around the edges but works quite well for me.

Added
-----

- Added "-c" / "--config-file" command line option to specify config file.

- Added configuration options to specify visibility to use when posting new statuses and to control if
  bot should post feed items only if there is an accompanying media file

- Now respecting rate limits when instance returns 429 error

Changed
-------

- Improved checking if image URL points to image file.

- Catching error during posting of feed items and ensuring app exits with non-zero return code when this occurs.

- Using proper temporary files for downloading and uploading of accompanying media files.

.. _changelog-0.2.1:

0.2.1 — 2023-02-27
==================

Changed
-------

- Corrected references to license in README file and added LICENSE.md

.. _changelog-0.2.0:

0.2.0 — 2023-02-27
==================

Added
-----

- Added import function to be able to import a file of URLs for the cache database.
  This is aimed at people migrating from feed2toot and wanting to import the cache.db file that
  feed2toot produces.

Changed
-------

- Improved finding article image in feed.

.. _changelog-0.1.0:

0.1.0 — 2023-02-26
==================

Added
-----

- Initial release of Feed2Fedi for preview.
