from application import create_app, db
import os

app = create_app() 

if not os.path.exists(os.path.join(app.static_folder, 'files')):
    os.mkdir(os.path.join(app.static_folder, 'files'))
    
if not os.path.exists(os.path.join(app.static_folder, 'avatars')):
    os.mkdir(os.path.join(app.static_folder, 'avatars'))
# app.static_folder ='static'
