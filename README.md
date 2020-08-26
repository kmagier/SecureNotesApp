# SecureNotesApp
Very simple app created for Data Security in IT classes.

Purpose of the project was to create a simple application allowing short notes publishing, with focus on security, i.e.: passwords protected with salt, form validation, using HTTPS protocol and self-signed certificates.

List of functionalities:
* User registration/login
* Adding/Editing/Deleting notes
* Uploading/Deleting files for notes
* Making notes public or private(public notes can be seen by every user)
* Subscribing/Unsubscribing notes
* Following/Unfollowing users
* User profiles with editable avatar and about me section
* Simple administrator panel for admin users to manage all users and notes
* Adding posts(announcements) for admin users

To run this application an .env file with environmental variables must be created containing following variables:
```
FLASK_ENV  
FLASK_DEBUG      
SECRET_KEY 
POSTGRES_DB       
POSTGRES_USER  
POSTGRES_PASSWORD
MAIL_USERNAME
MAIL_PASSWORD
MAIL_SERVER
MAIL_PORT
MAIL_USE_TLS
```
Also self-signed certificate and key are required.
