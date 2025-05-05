Config File Explained
=====================

The initial config file generated on the first run of Feed2Fedi is bare-bones and needs to be edited to make Feed2Fedi
work for you. Below is a copy of the bare-bones config file.

.. code-block:: JSON

   {
     "bot_post_visibility": "unlisted",
     "bot_post_media": true,
     "bot_post_image_selector": "img[src]",
     "bot_post_template": "{title}\n\n{link}",

     "cache_max_age": 30,
     "cache_db_path": "./cache.sqlite",

     "fedi_instance": "botsin.space",
     "fedi_access_token": "<redacted>",

     "feeds": [
       {
         "url": "http://feedparser.org/docs/examples/rss20.xml"
         "prefix": "Example",
         "max_attachments": 1
         "filters":[
          {"check":"", "check_params", "action":"", "action_params":""}
         ]
       }
     ]
   }



Variables starting with `bot_`
------------------------------

The variables starting with `bot_` specify how Feed2Fedi makes posts on your Fediverse server:

- `bot_post_visibility` = This specifies what kind of visibility Feed2Fedi uses for posts it makes.  This can be set to
  `public`, `unlisted`, or `private`. A post visibility of `direct` is technically also available but does not make
  sense in the context of Feed2Fedi. By default Feed2Fedi will post statuses with a visibility of `public`
- `bot_post_media` = This is a boolean and can be set to either `True` or `False`. This setting defaults to `False`

  - `True` - if set to True Feed2Fedi will attempt to upload any media linked in feed items to your fediverse account
    and add them to posts.
  - `False` - if set to False Feed2Fedi will just post the title and link of the feed item.
- `bot_post_image_selector` = This is css-like selector that determine what images will be attached to post.
- `bot_post_template` = This string defines template for posts. Available variables are:
  `{title}`, `{content_html}`, `{content_markdown}`, `{content_plaintext}`, `{link}`, `{author}`, `{published}`, `{updated}`.
  `\n` also available for a new line. `{content_html}` and `{content_markdown}` can work incorrectly with your instance
  This setting defaults to: `{title}\n\n{link}`

Variables starting with `cache_`
--------------------------------

The variables starting with `cache_` define some parameters used to attempt to avoid making duplicate posts.

- `cache_max_age` = This value defines how long URLs of feed items posted to your Fediverse account will be cached. Duplicate
  checks are performed against the cached URLs. This value defaults to `30` days.
- `cache_db_path` = This value defines the URL cache db file. The URL cache is stored in `SQLite`_ database at the location
  specified in this setting. This setting defaults to storing the URL cache in a SQLite database file stored in the
  current directory in a file called `cache.sqlite`

Variables starting with `fedi_`
-------------------------------

The variables starting with `fedi_` specifies the Fediverse account to post statuses to. The easiest way to complete
this section is by running Feed2Fedi without these values and Feed2Fedi will ask you for them and update the config
file as needed.

See :doc:`Setting-up-Feed2Fedi` for more details.

`feeds` section / Specifying RSS / Atom feeds / filters
-------------------------------------------------------

You can filter out words to prevent their appearance in the Fediverse posts. The filter list consists of dictionaries
(it can be zero). The structure is the same as in Feeds.
Every dictionary contains mandatory keys `check` and `action` and optional keys `check_params` and `action_params`
The `check` key defines what kind of checking is applied to every post. It can be:

- "any" - is true for every post.
- "none" - is false for every post
- "regex" - is true if "content_html" matches the regular expression(s) defined in check_params
- "action" defines what action will be applied to the post(s) if "check" is true for them
- "none" - do nothing
- "drop" - the post won't be published
- "mark_cw" - apply a content warning to the post. the cw text is the string in "action_params"
- "search_replace" - "action_params" should be a dictionary with keys "search" and "replace". It will find the text that matches the regular expression defined in "search" and replace it with the text from "replace". It is possible to use "\number" for linking to an element of the line (see https://docs.python.org/3/library/re.html#index-26)

Examples:

.. code-block:: JSON

   {"check": "any", "action": "search_replace", "action_params": {"search": "apple", "replace": "orange"}}

string "apple" will be replaced with "orange" in all posts

.. code-block:: JSON

   {"check": "any", "action": "search_replace", "action_params": {"search": "(@[a-z_-]+) ", "replace": "\1@twitter.com"}}

"@some_name" will be replaced with "some_name@twitter.com" in all posts.

.. code-block:: JSON

   {"check": "regex", "check_params": ".puppy[- ]?kick.", "action": "mark_cw", "action_params": "Worst crime ever!"}

The content warning "Worst crime ever" will be added to all posts matching the *puppy[- ]?kick.* regular expression

.. code-block:: JSON

   {"check": "regex", "check_params": ".puppy[- ]?kick.", "action": "drop"}

Posts matching the regular expression .*puppy[- ]?kick.* won't be published.

---------------------------------------------

To make Feed2Fedi post items from RSS / Atom feed(s) need to change the `feeds` section in the config file.

Each individual feed is comprised of a `url` and optionally a `prefix`, and a `max_attachments` setting.
The `url` is the link to the actually RSS / Atom feed.
If provided, the `prefix` variable is a string that will be prefixed with each item posted from the feed. This variable
defaults to an empty string if not provided.
If provided, the `max_attachments` variable defines the maximum number of images / videos that will be uploaded with
each feed item. This can be any positive integer number, including 0, or the string `max`. The value `max` will result
in Feed2Fedi uploading up to the maximum number of images supported by your fediverse instance.
This variable defaults to `max`

The `[Feeds]` section has a very simple format of identifier = url of RSS / Atom feed and you c

.. _SQLite: https://www.sqlite.org/
