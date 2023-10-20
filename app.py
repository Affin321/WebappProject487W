from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore, storage
from werkzeug.utils import secure_filename

app = Flask(__name__)
#This sets up the firebase inititlazaton to cloud firestore and storage
drec = credentials.Certificate("Firebasekey.json")
firebase_admin.initialize_app(drec, {
    'storageBucket': 'web-app-database-ec13c.appspot.com'
})
Database = firestore.client()
bucket = storage.bucket()


# This function allows the users to upload images onto firestore as well as the firestore database in order to
# display it as a image onto the flask web application
def upload_image(pyimg):
    if pyimg:
        filename = secure_filename(pyimg.filename)

        blob = bucket.blob(filename)
        blob.upload_from_file(pyimg, content_type=pyimg.content_type)

        # This code makes the images public onto the flask web app
        blob.make_public()

        return blob.public_url
    return None


# This code gives the route to the index to get all the collections, html templates as well as the files to display
# onto the webapp and firebase

@app.route('/', methods=['GET', 'POST'])
def index():
    Collectionsfromusers = Database.collection('items')
    accesstocollections = Collectionsfromusers

    if request.method == 'POST' and 'search' in request.form:
        phrase = request.form['search']
        accesstocollections = Collectionsfromusers.where('name', '==', phrase)

    # This part of the code checks if the name,desctription, and image are able to be sorted with a button on the header
    # of the flask web app
    List_factor = request.args.get('sort_by')
    if List_factor == 'name':
        accesstocollections = accesstocollections.order_by('name')
    elif List_factor == 'id':
        accesstocollections = accesstocollections.order_by('item_id_number')

    Tools = accesstocollections.stream()
    return render_template('index.html', items=Tools)


@app.route('/add_item', methods=['POST'])
def add_item():
    title = request.form['name']
    Info = request.form['description']
    Flask_url = request.form['ID']

    # This code gets the url from the web/image upload and displays it onto the flask web app
    jpeg = request.files['image']
    image_url = upload_image(jpeg)

    # This code gets the collections aspect of firebase and adds in documents with a specific name, description, and ID
    Defer = Database.collection('items')

    numbersort = int(Flask_url)

    Defer.document(Flask_url).set({
        'name': title,
        'description': Info,
        'image_url': image_url,
        'ID': Flask_url,
        'Sort': numbersort  # Add a numeric field for sorting
    })

    return redirect(url_for('index'))


# This function allows the route from the html template to be able to edit items to change their description and name within flask
@app.route('/edit_item/<item_id>', methods=['POST'])
def edit_item(item_id):
    Titleinfosave = request.form['name']
    new_description = request.form['description']

    Databaseitems = Database.collection('items').document(item_id)
    Databaseitems.update({
        'name': Titleinfosave,
        'description': new_description
    })

    return redirect(url_for('index'))

#This code allows a delete function within the flask web app
@app.route('/delete_item/<item_id>', methods=['POST'])
def delete_item(item_id):
    Database.collection('items').document(item_id).delete()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
