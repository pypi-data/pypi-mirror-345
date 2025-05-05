Setting up Feed2Fedi
================================================================

Downloading Feed2Fedi and installing dependencies / requirements
----------------------------------------------------------------

The easiest way to use Feed2Fedi is by installing from `PyPi`_ using `pipx`_ or `pip`_.

I highly recommend using `pipx`_ if your system supports it. Installing Feed2Fedi with `pipx`_ is as simple as
typing the following into a command line / terminal window:

.. code-block:: console

   pipx install feed2fedi

This command will download and install Feed2Fedi and all its dependencies / requirements from `PyPi`_

Settings
--------

All settings are defined in a config file that defaults to a file named `config.json` in the current directory.
If you are starting from scratch you can just run Feed2Fedi and it will ask you a few questions, ask you to sign into
your Fediverse account, and create a bare-bones config file.

If you've installed Feed2Fedi using pipx as recommended you can start Feed2Fedi from the command line by simply entering:

.. code-block:: console

   feed2fedi

When you run Feed2Fedi for the first time it will:
  1) ask you for the domain name of the server for your Fediverse account.
  2) display a special authorization URL. Please enter that URL into your web browser. Follow the instructions on that
     site to generate an Authorization Code.
  3) ask for the Authorization Code for your account. Please supply the code created in step 2
  4) save an access token in your config file for future use. This access token should not be shared with others.

Specifying RSS / Atom feeds
---------------------------

See :doc:`Config-File-Explained` for details of the different settings in the config file. This will explain in detail
how to specify the RSS / Atom feed(s) to read items from and cross post these to your Fediverse account.

Command Line Options
--------------------

Feed2Fedi also supports some command line options. The fastest and most accurate way to see all available command line
options is by adding `--help` when invoking Feed2Fedi as per below:

.. code-block:: console

   feed2fedi --help

Other than the `--help` option Feed2Fedi currently supports the following two options:
  - `--config-file` or `-c` allows you to specify an alternate configuration file. If this option is not specified
    Feed2Fedi will assume the config file to use is `config.json`
  - `--limit` or `-l` allows you to limit the maximum number of statuses to post before Feed2Fedi exits. The default is
    no limit, i.e. process all entries in all RSS / Atom feeds specified.

.. _PyPi: https://pypi.org/
.. _pipx: https://pypa.github.io/pipx/
.. _pip: https://pip.pypa.io/en/stable/
