Changelog
=========

[8.0.0] - 2025-05-05
--------------------

Breaking change
~~~~~~~~~~~~~~~

-  Dropped support of Python 3.8. ### Added
-  Testing for Python 3.11, 3.12, and 3.13. ### Fixed
-  Large paylod for ntfy notifier. Thanks to
   `wunter8 <https://github.com/wunter8>`__ in
   `PR#146 <https://github.com/kibitzr/kibitzr/pull/146>`__.

.. _section-1:

[7.0.6] - 2024-01-05
--------------------

Added
~~~~~

-  Support for ntfy notifier. Thanks to
   `wunter8 <https://github.com/wunter8>`__ in
   `PR#141 <https://github.com/kibitzr/kibitzr/pull/141>`__.

.. _section-2:

[7.0.5] - 2023-03-29
--------------------

Fixed
~~~~~

-  Restore CHANGELOG markup conversion

.. _section-3:

[7.0.4] - 2023-03-29
--------------------

.. _fixed-1:

Fixed
~~~~~

-  Update usage for the new version of telegram bot. Thanks to `Pan
   Luo <https://github.com/xcompass>`__ in
   `PR#139 <https://github.com/kibitzr/kibitzr/pull/139>`__

.. _section-4:

[7.0.3] - 2023-03-23
--------------------

.. _fixed-2:

Fixed
~~~~~

-  Update import path for the new version of telegram bot.
   `Issue#138 <https://github.com/kibitzr/kibitzr/issues/138>`__

.. _section-5:

[7.0.2] - 2023-02-24
--------------------

.. _added-1:

Added
~~~~~

-  Support for Twilio notifier. Thanks to `Colin
   Unger <https://github.com/lockshaw>`__ in
   `PR#137 <https://github.com/kibitzr/kibitzr/pull/137>`__

.. _section-6:

[7.0.1] - 2023-02-24
--------------------

.. _added-2:

Added
~~~~~

-  Support for Discord webhook notifier. Thanks to
   `Iwa <https://github.com/mcrozz>`__ in
   `PR#136 <https://github.com/kibitzr/kibitzr/pull/136>`__

.. _section-7:

[7.0.0] - 2022-07-19
--------------------

Removed
~~~~~~~

-  Python 3.6 and 3.7 support.

.. _added-3:

Added
~~~~~

-  Python 3.10 support

.. _section-8:

[6.2.1] - 2022-05-07
--------------------

.. _fixed-3:

Fixed
~~~~~

-  Python version requirement (3.6+) for the package.

.. _section-9:

[6.2.0] - 2022-05-07
--------------------

Changed
~~~~~~~

-  SMTP notifier will not try to authenticate when either user or
   password is missing from configuration. Thanks to
   `QJKX <https://github.com/QJKX>`__ in
   `PR#122 <https://github.com/kibitzr/kibitzr/pull/122>`__

.. _section-10:

[6.1.0] - 2022-01-28
--------------------

.. _added-4:

Added
~~~~~

-  ``kibitzr reload`` command to pick up configuration changes without
   restart by `fi-do <https://github.com/fi-do>`__ in
   `PR#115 <https://github.com/kibitzr/kibitzr/pull/115>`__

.. _section-11:

[6.0.2] - 2021-12-05
--------------------

-  Update docker image

.. _section-12:

[6.0.1] - 2021-10-11
--------------------

.. _added-5:

Added
~~~~~

-  `Gotify
   notifier <https://kibitzr.readthedocs.io/en/latest/gotify.html>`__ by
   `egvimo <https://github.com/egvimo>`__ in
   `PR#108 <for://github.com/kibitzr/kibitzr/pull/108>`__

.. _section-13:

[6.0.0] - 2019-08-06
--------------------

.. _removed-1:

Removed
~~~~~~~

-  Support for Python 2.6, 3.4

.. _added-6:

Added
~~~~~

-  Support for Python 3.7

.. _section-14:

[5.4.4] - 2019-08-06
--------------------

.. _fixed-4:

Fixed
~~~~~

-  skip handling of unsupported SIGUSR1 under Windows #73.

.. _added-7:

Added
~~~~~

-  provide context for ``{{ env }}`` dictionary in all Jinja templates.

.. _section-15:

[5.4.3] - 2019-06-07
--------------------

.. _fixed-5:

Fixed
~~~~~

-  Fixed ``xpath`` in Jinja transform for attribute and namespace access
   (#81 thanks to @mstarzyk).

.. _section-16:

[5.4.2] - 2018-12-27
--------------------

.. _changed-1:

Changed
~~~~~~~

-  Better support for dynamic forms filling. Check only first form field
   for accessibility.
-  Changed ``bash`` to ``shell`` in docs and added alias.

.. _section-17:

[5.4.1] - 2018-11-27
--------------------

.. _changed-2:

Changed
~~~~~~~

-  Replaced option ``verify_cert`` with ``verify-cert`` for consistency.

.. _section-18:

[5.4.0] - 2018-10-20
--------------------

.. _added-8:

Added
~~~~~

-  Schedule option (#71 thanks to @cescobarresi).
-  Option to omit HTTPS certificate verification in simple fetcher (#72
   thanks to @cescobarresi).

.. _section-19:

[5.3.5] - 2018-10-02
--------------------

.. _added-9:

Added
~~~~~

-  Telegram notifier option ``split-on`` (#70 thanks to @cescobarresi).
   ### Changed
-  Fixed ``xpath`` transform for attribute and namespace access (#68
   thanks to @cescobarresi).

.. _section-20:

[5.3.4] - 2018-09-28
--------------------

.. _added-10:

Added
~~~~~

-  ``xpath-all`` transform (#67 thanks to @cescobarresi).

.. _section-21:

[5.3.3] - 2018-08-24
--------------------

.. _added-11:

Added
~~~~~

-  [undocumented] ``before_start`` extension interface.

.. _section-22:

[5.3.2] - 2018-08-16
--------------------

.. _changed-3:

Changed
~~~~~~~

-  Made custom Jinja filters ignore None values.
-  convert lxml to defusedxml in transformer/html.py (#61 thanks to
   @unit-00).

.. _section-23:

[5.3.1] - 2018-07-06
--------------------

.. _added-12:

Added
~~~~~

-  [undocumented] CLI extension interface.

[5.3.0.alpha] - 2018-05-06
--------------------------

.. _added-13:

Added
~~~~~

-  [undocumented] fetcher extension interface.

.. _section-24:

[5.2.0] - 2018-05-06
--------------------

.. _changed-4:

Changed
~~~~~~~

-  ``kibitzr firefox`` now prompts for Return to save profile.
-  Firefox profile directory path moved to capabilities in the new
   version.

.. _section-25:

[5.1.1] - 2018-04-19
--------------------

.. _added-14:

Added
~~~~~

-  ``kibitzr stash`` command to show stash contents.

.. _section-26:

[5.1.0] - 2018-04-10
--------------------

.. _added-15:

Added
~~~~~

-  kibitzr clean command to delete changes history (#13 thanks to
   @attilanagy).
-  Jinja filters: int and float.

.. _section-27:

[5.0.0] - 2017-12-16
--------------------

.. _changed-5:

Changed
~~~~~~~

-  Dropped support for Firefox < 56 (using -headless instead of XVFB).

.. _section-28:

[4.0.10] - 2017-08-28
---------------------

.. _changed-6:

Changed
~~~~~~~

-  Fix #47: Xpath transform encodes content to UTF-8 before parsing
   (X|HT)ML.

.. _section-29:

[4.0.9] - 2017-08-21
--------------------

.. _fixed-6:

Fixed
~~~~~

-  Allow SMTP without authentication. ### Changed
-  Use local SMTP server by default.

.. _section-30:

[4.0.8] - 2017-08-02
--------------------

.. _fixed-7:

Fixed
~~~~~

-  Fixed xpath selector transform.

.. _section-31:

[4.0.7] - 2017-06-29
--------------------

.. _fixed-8:

Fixed
~~~~~

-  Fixed interruption exit code (1).

.. _section-32:

[4.0.6] - 2017-06-28
--------------------

.. _fixed-9:

Fixed
~~~~~

-  Exit(2) when receiving SIGTERM/SIGINT.

.. _section-33:

[4.0.5] - 2017-06-14
--------------------

.. _fixed-10:

Fixed
~~~~~

-  Exit(1) Kibitzr when Firefox goes funny business.

.. _section-34:

[4.0.4] - 2017-06-07
--------------------

.. _changed-7:

Changed
~~~~~~~

-  Firefox fetcher: Implicitly wait 2 seconds for selects.
-  Firefox fetcher: Resize window before each fetch. ### Fixed
-  bash transform: Skip execution for empty content.

.. _section-35:

[4.0.3] - 2017-05-25
--------------------

.. _added-16:

Added
~~~~~

-  Changes style “new” - show only current content if it changed. ###
   Fixed
-  text filter in Jinja templates.
-  Adapted list of requirements for Windows.

.. _section-36:

[4.0.2] - 2017-05-21
--------------------

.. _added-17:

Added
~~~~~

-  Explicit telegram imprinting. ### Fixed
-  Dynamically import only what’s needed in checks.
-  Better Windows support.
-  Support for non-ascii URLs.

.. _section-37:

[4.0.1] - 2017-05-10
--------------------

.. _added-18:

Added
~~~~~

-  Credentials extensions through entry points (for kibitzr-keyring).

.. _section-38:

[4.0.0] - 2017-05-08
--------------------

.. _added-19:

Added
~~~~~

-  ``kibitzr init`` - create sample configuration files. ### Changed
-  Changed kibitzr CLI commands structure (``kibitzr run`` instead of
   ``kibitzr``).

.. _section-39:

[3.1.8] - 2017-05-08
--------------------

.. _fixed-11:

Fixed
~~~~~

-  Unspecified period caused error (introduced in 3.1.4).

.. _section-40:

[3.1.7] - 2017-05-06
--------------------

.. _fixed-12:

Fixed
~~~~~

-  Gracefull shutdown on SIGTERM (as on SIGINT).

.. _section-41:

[3.1.6] - 2017-05-05
--------------------

.. _fixed-13:

Fixed
~~~~~

-  Jinja transform. ### Added
-  CHANGELOG to PyPI page.

.. _section-42:

[3.1.4] - 2017-05-04
--------------------

.. _changed-8:

Changed
~~~~~~~

-  human-readable period.

.. _section-43:

[3.1.3] - 2017-05-01
--------------------

.. _fixed-14:

Fixed
~~~~~

-  Bash and Python transforms parameter (dis)order.
-  Skip Bash transform if input is empty. ### Changed
-  Requests fetcher uses caching.

.. _section-44:

[3.1.0] - 2017-05-01
--------------------

.. _added-20:

Added
~~~~~

-  Jinja transform. ### Removed
-  cut and sort transforms (superseded by bash).

.. _section-45:

[3.0.11] - 2017-04-30
---------------------

.. _added-21:

Added
~~~~~

-  Browser form filling shorthand.

.. _section-46:

[3.0.10] - 2017-04-29
---------------------

.. _added-22:

Added
~~~~~

-  Bash transform. ### Fixed
-  jq transform input encoding.

.. _section-47:

[3.0.9] - 2017-04-25
--------------------

.. _fixed-15:

Fixed
~~~~~

-  Firefox fetcher: retry 3 times on stale element exception.
-  Persistent Firefox: Ignore all exceptions when closing.

.. _section-48:

[3.0.8] - 2017-04-24
--------------------

.. _added-23:

Added
~~~~~

-  Transformer css-all selector which returns all elements instead of
   first.
-  Python transformer. ### Changed
-  Missing check name autopopulated from URL or autogenerated.

.. _section-49:

[3.0.7] - 2017-04-19
--------------------

.. _added-24:

Added
~~~~~

-  Zapier notifier.

.. _section-50:

[3.0.6] - 2017-04-19
--------------------

.. _added-25:

Added
~~~~~

-  Telegram notifier.

.. _section-51:

[3.0.3] - 2017-04-18
--------------------

.. _added-26:

Added
~~~~~

-  Persistent firefox profile [undocumented].

.. _section-52:

[3.0.2] - 2017-04-18
--------------------

.. _added-27:

Added
~~~~~

-  Short form for SMTP notifier #11. ### Fixed
-  Weird BS4 misbehaviour in CSS selector.

.. _section-53:

[3.0.1] - 2017-04-07
--------------------

.. _fixed-16:

Fixed
~~~~~

-  Exit if no checks defined.
-  Better credentials reloading.

.. _section-54:

[3.0.0] - 2017-04-04
--------------------

.. _changed-9:

Changed
~~~~~~~

-  Switched to selenium >3 and Firefox >48.

.. _section-55:

[2.7.4] - 2017-04-01
--------------------

.. _changed-10:

Changed
~~~~~~~

-  Closing FireFox tab after it was fetched to reduce idle CPU.

.. _section-56:

[2.7.3] - 2017-03-31
--------------------

.. _added-28:

Added
~~~~~

-  Started CHANGELOG.
-  script.python fetcher.
