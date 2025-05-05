Release history and notes
=========================
.. Internal references

.. _pathy: https://github.com/justindujardin/pathy
.. _`International Women's Day`: https://en.wikipedia.org/wiki/International_Women%27s_Day
.. _pytest-codeblock: https://github.com/barseghyanartur/pytest-codeblock

`Sequence based identifiers
<http://en.wikipedia.org/wiki/Software_versioning#Sequence-based_identifiers>`_
are used for versioning (schema follows below):

.. code-block:: text

    major.minor[.revision]

- It's always safe to upgrade within the same minor version (for example, from
  0.3 to 0.3.4).
- Minor and major version changes might be backwards incompatible. Read the
  release notes carefully before upgrading (for example, when upgrading from
  0.3.4 to 0.4).
- All backwards incompatible changes are mentioned in this document.

0.1.6
-----
2025-05-04

- Switch to `pytest-codeblock`_ for testing documentation codeblocks.
- Improve documentation and tests.
- Upgrade pyproject.toml to the new licenses standards.

0.1.5
-----
2025-03-12

- Added Python 3.13 support.

0.1.4
-----
2025-03-08

.. note::

    Dear women, congratulations with `International Women's Day`_!

- Added Python 3.12 support.
- Added `pathy`_ 0.11 support. Now this package supports both legacy (0.10.x)
  and modern (0.11.x) versions of `pathy`_.

0.1.3
-----
2025-03-05

- Minor fixes.

0.1.2
-----
2025-03-04

- Minor fixes.

0.1.1
-----
2024-09-11

- Minor optimisations.

0.1
-----
2024-08-09

- Initial beta release.
