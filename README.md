# auth-file-server

Simple file browser with video streaming.

The major inspriation for this project was just how bad Plex is when run on a Raspberry Pi. Plex requires both a client and server and will deadlock a raspberry Pi performing on-demand video encoding. This project is meant to be a lightweight replacement that functions entirely in browser with no special client code.

The two largest projects on which this project builds are:

[Wildog's flask file server](https://github.com/Wildog/flask-file-server) and [this Flask-Login tutorial](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login). Aside from getting these projects talking to each other, additional features have been added. These include:

- Separate user directories
- CLI database management
- CSS theme integration
- Improved response to range headers

Install notes:

Clone to your RPi (or similar environment). Then:

1. Create a Python 3 environment and install requirements

        python3 -m venv pyenv
        source pyenv/bin/activate
        pip3 install -r requirements.txt

2. Create the database and server root directory

        ./db_manager.py --init

3. Start the server

        ./run.sh

4. Visit the website and sign up
5. Revisit the command line and approve new users

        ./db_manager -e <user-email> -a
        ./db_manager -u <user-name> -a
        ./db_manager -i <user-id> -a

And that's it. User directories can be found in server-root/<user-id>. You can select (or create your own) messages to display on the about page by altering stats.py.
