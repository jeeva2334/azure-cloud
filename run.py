import os
from flask import Flask, request, redirect, url_for, render_template
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = Flask(__name__)
#global url
# Replace <your-storage-account-name> and <your-storage-account-key> with your actual Azure Storage account name and key
blob_service_client = BlobServiceClient.from_connection_string("<constr>")

# Replace <your-container-name> with the name of the container you want to upload the file to
container_client = blob_service_client.get_container_client("<container name>")

app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            return redirect(url_for('upload_file'))
        else:
            return redirect(url_for('login_error'))

    return render_template('login.html')



@app.route('/dashboard', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        blob_client = container_client.get_blob_client(filename)
        blob_client.upload_blob(file.read())
        
        return redirect(url_for('uploaded_file', filename=filename))
    return '''
        <!doctype html>
        <html>
            <body>
                <h1>Upload a file to Azure Blob Storage</h1>
                <form method=post enctype=multipart/form-data>
                    <input type=file name=file>
                    <input type=submit value=Upload>
                </form>
            </body>
        </html>
    '''

@app.route('/login-error')
def login_error():
    return render_template('login-error.html')

@app.route('/uploaded/<filename>')
def uploaded_file(filename):
    url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_client.container_name}/{filename}"
    return f'''
        <!doctype html>
        <html>
            <body>
                <h1>File {filename} uploaded successfully to Azure Blob Storage {url}</h1>
                <a href="{url}">URL to File</a>
            </body>
        </html>
    '''
if __name__ == '__main__':
    app.run(debug=True)