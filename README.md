# auth-file-server

Simple file browser with video streaming.

The major inspriation for this project was just how bad Plex is when run on a Raspberry Pi. Whereas a single thread from this server can deliver a 170 MB video in seconds on LAN, Plex would deadlock the CPU indefinitely with video transcoding. The Pi is just not cut out for that sort of processing load. This project is meant to be a lightweight replacement that functions entirely in browser with no special client code.

The two largest projects on which this project builds are:

[Wildog's flask file server](https://github.com/Wildog/flask-file-server) and [this Flask-Login tutorial](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login). Aside from getting these projects talking to each other, additional features have been added. These include:

- Vastly improved user management
    - Passwords are sha-256 hashed and stored in a secure sql db. "Secure" means that it survived a penetration test that includes, among other things, sql injection attacks.
    - CLI database manager
    - Separate user directories
    - User review process
- Web page theme integration
- Video playback with html5 video tag

Note: Since the main motivation for this server is avoidance of on-demand transcoding the server makes no attempt to deliver a video that your browser can actually *play*. I've found that the .webm container format with libvp8 video codec and libopus audio codec is compatible with Firefox and Chromium as deployed on Fedora Linux. This encoding is supported by Chromium (and therefore Chrome) on any OS as per [the official Chromium docs](https://www.chromium.org/audio-video/). If you want your server to deliver properly encoded video and audio it is up to you to schedule a Cron job or other means to transcode your library using something like ffmpeg.

## Install notes

Clone to your RPi (or similar environment). Then:

1. Create a Python 3 environment and install requirements (the code for performing this operation is also present within `run.sh`)

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
