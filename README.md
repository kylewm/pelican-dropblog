Dropblog
========

Hacked together script to poll dropbox for blog content, generate a
new blog with pelican, and ftp the generated content to a remote ftp
server.

This is not remotely robust/well-tested/secure, but it seems to work
for me, and might be a good starting point if you want to write
something similar. To get started, Copy `dropblogconf.py.template` to
`dropblogconf.py` and fill in your Dropbox API key and FTP
information. Install pelican, markdown, and dropbox (in a virtualenv
preferably) and run `python dropblog.py`. The cron job uses `cd
path/to/pelican-dropblog && path/to/virtualenv/bin/python
dropblog.py`.