#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Kyle Mahan'
SITENAME = u"kyle w.m."
SITEURL = u'http://kylewm.com'

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
#FEED_ALL_RSS = 'feeds/all.rss.xml'

CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

FILES_TO_COPY = ()

ARTICLE_EXCLUDES = ('pages','extra',)

DEFAULT_PAGINATION = None

THEME = 'themes/jinja-ripoff'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
