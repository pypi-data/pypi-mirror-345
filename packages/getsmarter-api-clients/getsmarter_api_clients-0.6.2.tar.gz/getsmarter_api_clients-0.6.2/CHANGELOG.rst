Change Log
----------

..
   All enhancements and patches to getsmarter-api-clients will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~
* Nothing unreleased

[0.6.2]
~~~~~~~
* Logs the allocation payload sent to GEAG within the ``create_allocation`` method.

[0.6.1]
~~~~~~~
* Adds an enterprise allocation cancellation method

[0.6.0]
~~~~~~~
* Adds optional arg to create_enterprise_allocation() to either raise (current/default behavior),
  or not raise and fall through to returning the response. This will allow callers
  to do things with the response payload in error conditions.

[0.5.4]
~~~~~~~
* Add `org_id`` as an optional enterprise allocation param

[0.5.3]
~~~~~~~
* Return allocation response objects

[0.5.2]
~~~~~~~
* Include payload in error message

[0.5.1]
~~~~~~~
* Catch a `requests.HTTPError`, not an `urllib.error.HTTPError`.

[0.5.0] - 2023-04-12
~~~~~~~~~~~~~~~~~~~~

* Added new field for data_share_consent in enterprise_allocations

[0.4.0] - 2022-09-12
~~~~~~~~~~~~~~~~~~~~

* Add enterprise_allocations endpoint functionality to client

[0.1.0] - 2022-08-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* First release on PyPI.
