=====================
fake-py-pathy-storage
=====================
.. External references

.. _fake.py: https://fakepy.readthedocs.io/
.. _Pathy: https://github.com/justindujardin/pathy
.. _faker-file: https://faker-file.readthedocs.io/
.. _Django: https://www.djangoproject.com/

.. Internal references

.. _fake-py-pathy-storage: https://github.com/barseghyanartur/fake-py-pathy-storage/
.. _Read the Docs: http://fake-py-pathy-storage.readthedocs.io/
.. _Contributor guidelines: https://fake-py-pathy-storage.readthedocs.io/en/latest/contributor_guidelines.html

`Pathy`_ storage for `fake.py`_.

.. image:: https://img.shields.io/pypi/v/fake-py-pathy-storage.svg
   :target: https://pypi.python.org/pypi/fake-py-pathy-storage
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/fake-py-pathy-storage.svg
    :target: https://pypi.python.org/pypi/fake-py-pathy-storage/
    :alt: Supported Python versions

.. image:: https://github.com/barseghyanartur/fake-py-pathy-storage/actions/workflows/test.yml/badge.svg?branch=main
   :target: https://github.com/barseghyanartur/fake-py-pathy-storage/actions
   :alt: Build Status

.. image:: https://readthedocs.org/projects/fake-py-pathy-storage/badge/?version=latest
    :target: http://fake-py-pathy-storage.readthedocs.io
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/barseghyanartur/fake-py-pathy-storage/#License
   :alt: MIT

.. image:: https://coveralls.io/repos/github/barseghyanartur/fake-py-pathy-storage/badge.svg?branch=main&service=github
    :target: https://coveralls.io/github/barseghyanartur/fake-py-pathy-storage?branch=main
    :alt: Coverage

`fake-py-pathy-storage`_ is a `Pathy`_ storage integration for `fake.py`_ - a
standalone, portable library designed for generating various
random data types for testing.

Features
========
- Cloud storages integration includes support for AWS S3, Google Cloud Storage
  and Azure Cloud Storage.

Prerequisites
=============
Python 3.9+

Installation
============

.. code-block:: sh

    pip install fake-py-pathy-storage

Documentation
=============
- Documentation is available on `Read the Docs`_.
- For guidelines on contributing check the `Contributor guidelines`_.

Usage
=====
Local cloud-alike file system storage
-------------------------------------
.. code-block:: python
    :name: test_pathy_file_system_storage

    from fake import FAKER
    from fakepy.pathy_storage.cloud import LocalFileSystemStorage

    STORAGE = LocalFileSystemStorage(
        bucket_name="bucket_name",
        root_path="tmp",  # Optional
        rel_path="sub-tmp",  # Optional
    )

    pdf_file = FAKER.pdf_file(storage=STORAGE)

    STORAGE.exists(pdf_file)

AWS S3
------

.. pytestmark: aws
.. code-block:: python
    :name: test_pathy_aws_s3_storage

    from fake import FAKER
    from fakepy.pathy_storage.aws_s3 import AWSS3Storage

    STORAGE = AWSS3Storage(
        bucket_name="bucket_name",
        root_path="tmp",  # Optional
        rel_path="sub-tmp",  # Optional
        # Credentials are optional too. If your AWS credentials are properly
        # set in the ~/.aws/credentials, you don't need to send them
        # explicitly.
        credentials={
            "key_id": "YOUR KEY ID",
            "key_secret": "YOUR KEY SECRET"
        },
    )

    pdf_file = FAKER.pdf_file(storage=STORAGE)

    STORAGE.exists(pdf_file)

Google Cloud Storage
--------------------

.. pytestmark: google_cloud_storage
.. code-block:: python
    :name: test_pathy_google_cloud_storage

    from fake import FAKER
    from fakepy.pathy_storage.google_cloud_storage import GoogleCloudStorage

    STORAGE = GoogleCloudStorage(
        bucket_name="bucket_name",
        root_path="tmp",  # Optional
        rel_path="sub-tmp",  # Optional
    )

    pdf_file = FAKER.pdf_file(storage=STORAGE)

    STORAGE.exists(pdf_file)

Azure Cloud Storage
-------------------

.. pytestmark: azure_cloud_storage
.. code-block:: python
    :name: test_pathy_azure_cloud_storage

    from fake import FAKER
    from fakepy.pathy_storage.azure_cloud_storage import AzureCloudStorage

    STORAGE = AzureCloudStorage(
        bucket_name="bucket_name",
        root_path="tmp",  # Optional
        rel_path="sub-tmp",  # Optional
    )

    pdf_file = FAKER.pdf_file(storage=STORAGE)

    STORAGE.exists(pdf_file)

Tests
=====

.. code-block:: sh

    pytest

Writing documentation
=====================

Keep the following hierarchy.

.. code-block:: text

    =====
    title
    =====

    header
    ======

    sub-header
    ----------

    sub-sub-header
    ~~~~~~~~~~~~~~

    sub-sub-sub-header
    ^^^^^^^^^^^^^^^^^^

    sub-sub-sub-sub-header
    ++++++++++++++++++++++

    sub-sub-sub-sub-sub-header
    **************************

License
=======

MIT

Support
=======
For security issues contact me at the e-mail given in the `Author`_ section.

For overall issues, go to `GitHub <https://github.com/barseghyanartur/fake-py-pathy-storage/issues>`_.

Author
======

Artur Barseghyan <artur.barseghyan@gmail.com>
