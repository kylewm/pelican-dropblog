#Copyright (c) 2013 Kyle Mahan <kyle.mahan@gmail.com>
#This work is free. You can redistribute it and/or modify it under the
#terms of the Do What The Fuck You Want To Public License, Version 2,
#as published by Sam Hocevar. See the COPYING file for more details.

import pelican
import os
import pickle
from subprocess import check_call, check_output

import dropblogconf as conf

def init_dropbox_client():
    sess = dropbox.session.DropboxSession(conf.DROPBOX_APP_KEY, conf.DROPBOX_APP_SECRET, conf.DROPBOX_ACCESS_TYPE)
    try:
        with open(".access_token", "r") as f:
            access_token = pickle.load(f)
            sess.token = access_token
    except:
        request_token = sess.obtain_request_token()
        url = sess.build_authorize_url(request_token, oauth_callback="http://dropbox.com")
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
    # Sync files from Dropbox to this folder
    cursor = None
    if os.path.exists(".cursor"):
        with open(".cursor", "r") as f:
            cursor = pickle.load(f);
            
    changed = False
    delta = client.delta(cursor)
    #print "delta: ", delta
    
    files_to_remove = []
    dirs_to_remove = []
    
    for filename, delta_metadata in delta["entries"]:
        dest_path = "staging/" + filename
        if not delta_metadata:
            # file has been deleted
            if os.path.exists(dest_path):
                if os.path.isfile(dest_path):
                    files_to_remove.append(dest_path)
                elif os.path.isdir(dest_path):
                    dirs_to_remove.append(dest_path)
        elif not delta_metadata["is_dir"]:
            src_file, src_metadata = client.get_file_and_metadata(filename)
            print "copying: ", filename
            dest_path_parent = os.path.dirname(dest_path)
            if not os.path.exists(dest_path_parent):
                os.makedirs(dest_path_parent)

            with open(dest_path, "w") as out:
                out.write(src_file.read())
            changed = True

    for filename in files_to_remove:
        print "removing: ", filename
        os.remove(filename)
        changed = True
    
    for dirname in dirs_to_remove:
        print "removing dir: ", dirname
        os.rmdir(dirname)
        changed = True

    new_cursor = delta["cursor"]
    with open(".cursor", "w") as f:
        pickle.dump(new_cursor, f);

    return changed


def git_synchronize():
    staging_dir = 'staging'
    if not os.path.exists(staging_dir):
        check_call(['git', 'clone', conf.GIT_REPO, staging_dir])
        return True
    else:
        saved_dir = os.getcwd()
        os.chdir(staging_dir)
        start_rev = check_output(['git', 'rev-parse', 'HEAD'])
        check_call(['git', 'pull', conf.GIT_REPO, 'master'])
        new_rev = check_output(['git', 'rev-parse', 'HEAD'])
        os.chdir(saved_dir)
        return new_rev != start_rev


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
    args.path='staging/content'
    args.settings='staging/pelicanconf.py'
    args.output='staging/output'
    pel = pelican.get_instance(args)
    pel.run()


def ftp_mirror():
    check_call(['lftp', conf.FTP_SERVER, '-u', '{},{}'.format(conf.FTP_USER,conf.FTP_PASS),
                '-e', 'set ssl-allow no ; mirror -R staging/output {} ; quit'.format(conf.FTP_REMOTE_PATH)]) 


def synchronize():
    if conf.SOURCE is 'git':
        print "Synchronizing with Git repository"
        return git_synchronize()
    elif conf.SOURCE is 'dropbox':
        import dropbox.client, dropbox.session, dropbox.rest
        print "Initializing Dropbox client"
        client = init_dropbox_client()
        print "Synchronizing with Dropbox"
        return dropbox_synchronize(client)

    
if __name__ == '__main__':
    if synchronize():
        print "Generate static site"
        run_pelican()
        print "Create FTP mirror"
        ftp_mirror()
    else:
        print "Up to date!"
