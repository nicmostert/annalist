=======
History
=======

0.1.0 (2023-09-13)
------------------

* First release on PyPI.

0.1.1 (2023-10-27)
------------------

* Basic logging functionality.
* Only supports logging to console.

0.2.0 (2023-11-2)
------------------

* Implemented Annalist as a Singleton.
* Usage now includes configuration step.

0.3.0 (2023-11-20)
------------------

* Now takes arbitrary input paramaters.
* Able to support Hilltop audit trail parity.
* User can control logging levels

0.3.3 (2023-11-24)
------------------

* I'm not sure what happened to 0.3.1 and 0.3.2
* Now REALLLY able to support Hilltop audit trail parity.
* Improved support for class method logging

0.3.4 (2023-11-28)
------------------

* Fixed a bug with argument handling

0.3.5 (2023-11-29)
------------------

* Added basic string sanitation and truncating of long values in default message fields.

0.3.6 (2023-11-29)
------------------

* Now also sanitizing newline characters.

0.4.0 (2024-02-13)
------------------

* Moved to pyproject.toml package.
* Fixed bug relating to method identity crisis (decorated functions thought they were their decorators).

0.4.1 (2024-02-13)
------------------

* Fixed pyproject.toml package
* Updated .readthedocs.yaml to reflect changes in pyproject.toml

0.4.2 (2024-04-02)
------------------

* Relaxed Python dependency from 3.11.6 to 3.11

0.4.3 (2024-04-02)
------------------

* Considered being Ruff B905 compliant, but it turns out we're zipping over some unequal lists. Shelving this for later.
* Switched logfile mode from "append" to "write", which overwrites the logfile every time.

0.4.4 (2025-01-14)
------------------

* Added support for Python 3.12 onwards
