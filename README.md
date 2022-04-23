# auth-file-server

Simple file browser with video streaming.

The major inspriation for this project was just how bad Plex is when run on a Raspberry Pi. Whereas a single thread from this server can deliver a 170 MB video in seconds, Plex would deadlock 4 cores indefinitely (with video transcoding). Bad Plex. This project is meant to be a lightweight replacement that functions entirely in browser with no special client code.

The two largest projects on which this project builds are:

[Wildog's flask file server](https://github.com/Wildog/flask-file-server) and [this Flask-Login tutorial](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login). Aside from getting these projects talking to each other, additional features have been added. These include:

- Vastly improved user management
    - Passwords are sha-256 hashed and stored in a secure sql db. "Secure" means that it survived a penetration test that includes, among other things, sql injection attacks.
    - CLI database manager
    - Separate user directories
    - User review process
- Web page theme integration
- Video playback with html5 video tag

Leveraging the video tag is a big improvement. The built in Chrome player struggles with large video files.

## Install notes

Clone to your RPi (or similar environment). Then:

1. Create a Python 3 environment and install requirements

        python3 -m venv ./pyenv
        source pyenv/bin/activate
        pip3 install -r requirements.txt

2. Create the database and server root directory

        ./scripts/db_manager.py --init

3. Start the server. Make sure that `run.sh` references an `.ini` configuration file that suits your system. Examine the configuration file before use.

        ./scripts/run.sh

4. Visit the website and sign up
5. Revisit the command line and approve new users

        ./scripts/db_manager -e <user-email> -a
        #or
        ./scripts/db_manager -u <user-name> -a
        #or
        ./scripts/db_manager -i <user-id> -a

And that's it. User directories can be found in server-root/<user-id>. You can select (or create your own) messages to display on the about page by altering stats.py.
