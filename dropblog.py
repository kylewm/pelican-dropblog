import dropbox.client, dropbox.session, dropbox.rest
import pelican
import os
import pickle
from subprocess import check_call

import dropblogconf as conf

def init_dropbox_client():
    sess = dropbox.session.DropboxSession(conf.APP_KEY, conf.APP_SECRET, conf.ACCESS_TYPE)
    try:
        with open(".access_token", "r") as f:
            access_token = pickle.load(f)
            sess.token = access_token
    except:
        request_token = sess.obtain_request_token()
        url = sess.build_authorize_url(request_token, oauth_callback="http://localhost")
        print "url:", url
        print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
        raw_input()

        # This will fail if the user didn't visit the above URL and hit 'Allow'
        access_token = sess.obtain_access_token(request_token)
        with open(".access_token", "w") as f:
            pickle.dump(access_token, f)
    client = dropbox.client.DropboxClient(sess)
    return client

def dropbox_synchronize(client):
    # Sync files from Dropbox to content/ folder
    cursor = None
    if os.path.exists(".cursor"):
        with open(".cursor", "r") as f:
            cursor = pickle.load(f);
            
    changed = False
    delta = client.delta(cursor)
    #print "delta: ", delta
    for filename, delta_metadata in delta["entries"]:
        dest_path = "content/" + filename
        if not delta_metadata:
            # file has been deleted
            if os.path.exists(dest_path):
                print "removing: ", dest_path
                os.remove(dest_path)
                changed = True
        elif not delta_metadata["is_dir"]:
            src_file, src_metadata = client.get_file_and_metadata(filename)
            print "copying: ", filename
            dest_path_parent = os.path.dirname(dest_path)
            if not os.path.exists(dest_path_parent):
                os.makedirs(dest_path_parent)

            with open(dest_path, "w") as out:
                out.write(src_file.read())
            changed = True

    new_cursor = delta["cursor"]
    with open(".cursor", "w") as f:
        pickle.dump(new_cursor, f);

    return changed

def run_pelican():
    class Args:
        def __init__(self):
            self.path = None
            self.settings = None
            self.output = None
            self.markup = None
            self.theme = None
            self.delete_outputdir = None

    args = Args()
    args.path='content'
    args.settings='pelicanconf.py'

    pel = pelican.get_instance(args)
    pel.run()

def ftp_mirror():
    check_call(['lftp', conf.FTP_SERVER, '-u', '{},{}'.format(conf.FTP_USER,conf.FTP_PASS),
                '-e', 'set ssl-allow no ; mirror -R output {} ; quit'.format(conf.FTP_REMOTE_PATH)]) 
    
if __name__ == '__main__':
    print "Initializing Dropbox client"
    client = init_dropbox_client()
    print "Synchronizing with Dropbox"
    if dropbox_synchronize(client):
        print "Generate static site"
        run_pelican()
        print "Create FTP mirror"
        ftp_mirror()
    else:
        print "Up to date!"
