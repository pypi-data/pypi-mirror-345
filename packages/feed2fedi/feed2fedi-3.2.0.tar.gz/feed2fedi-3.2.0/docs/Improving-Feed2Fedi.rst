Improving Feed2Fedi
===================

I use `PDM`_ to keep track of and control dependencies / requirements for tootbot. If you want to make
changes to tootbot, I recommend you set up `PDM`_ on your system to make this easier.

After cloning the `Feed2Fedi repository`_ use the command below to set up your virtual environment for Feed2Fedi.
With this command, `PDM`_ will create a python virtual environment and install all dependencies / requirements
into it.

.. code-block:: console

   pdm sync --group :all

When making changes, I test against the feeds below:

- https://rss-bridge.icebox.anyaforger.art/?action=display&username=cats_cats&bridge=TelegramBridge&format=Mrss
- https://www.abc.net.au/news/feed/51120/rss.xml
- https://www.theguardian.com/au/rss
- http://timesofindia.indiatimes.com/rssfeedstopstories.cms
- https://www.indiatoday.in/rss/1206514

.. _PDM: https://pdm.fming.dev/latest/
.. _Feed2Fedi repository: https://codeberg.org/MarvinsMastodonTools/feed2fedi
