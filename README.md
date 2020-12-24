# auth-file-server

Essentially similar to an FTP server. Supports in-browser streaming / viewing of content, downloading, and user authentication and siloing.

The major inspriation for this was just how bad Plex is. Plex requires a client as well as server application and web content. Moreover Plex likes to force the server to perform video transcoding on demand, which effectively disables a Raspberry Pi, preventing it from responding to other server requests. This project is meant to be a relatively lightweight replacement that functions entirely in browser with no special client.

The two largest projects on which this project builds are:

[Wildog's flask file server](https://github.com/Wildog/flask-file-server) and [this Flask-Login tutorial](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login). On top of that, quite a lot of glue and additional functionality has been added. For example, the linked file server won't stream large files (ie videos) on Chrome correctly and this project makes the slight amendments necessary to fix that.
