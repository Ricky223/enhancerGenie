#!/usr/bin/env python
# coding: utf-8
import logging
import os
import uuid
import ast
import shutil
import hashlib
from flask import Response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, verify_jwt_in_request, get_jwt_identity
from pybedtools import BedTool
import distanceBased
import eQTLbased
import chromatinLoopBased
import abcBased
import mergeMethods
import datetime
import threading
import pandas as pd
from flask_mail import Mail, Message
from flask import Flask, flash, request, render_template, url_for, send_file, jsonify, send_from_directory
from werkzeug.utils import secure_filename, redirect
from Process import Process
import traceback
import json
from db import user, chart
import bcrypt
from flask import request, jsonify
import pymongo.errors
from db.connect import client

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'enhancergenie@gmail.com'
app.config['MAIL_PASSWORD'] = 'cbcaufeqxfziaxrr'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.secret_key = '12345'
mail = Mail(app)

app.config['JWT_SECRET_KEY'] = 'THIS_IS_SO_PRIVATE'
jwt = JWTManager(app)

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

# exceptions for file verification
class TissueMismatchWarning(Warning):
    pass
class FewEnhancersWarning(Warning):
    pass
class IncorrectFormatError(Exception):
    pass


def my_scheduled_job():
    logging.info("Scheduler running")
    directory_path = 'temp/'

    # get the current time
    current_time = datetime.datetime.now()

    # loop through all the files in the directory
    for file in os.listdir(directory_path):

        # get the full file path
        file_path = os.path.join(directory_path, file)

        # get the file's creation time and modified time
        created_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
        modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

        # check if the file was created or modified more than 8 minutes ago
        if (current_time - modified_time).total_seconds() > 900 or (current_time - modified_time).total_seconds() > 900:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                logging.info("deleted folder ", file_path)
            elif os.path.isfile(file_path) or os.path.islink(file_path):
                if (file_path != 'temp/tempr'):
                    os.remove(file_path)
                    logging.info("deleted file ", file_path)


def my_method():
    # your code here
    my_scheduled_job()


def run_method():
    print("started")
    # FIXME: Temporary comment out this line help to connect the frontend and backend
    my_method()
    threading.Timer(60, run_method).start()


run_method()


def target():
    raise ValueError('Something went wrong...')


def createUniqueEnhancerID(df):
    return str(df[0]) + ':' + str(df[1]) + '-' + str(df[2])


def cleanInputFile(inputFilename):
    # store enhancer input file as data frame
    inputDf = pd.read_csv(inputFilename, sep='\t', header=None)
    if len(inputDf.columns) < 4:
        # if enhancerDF has 3 columns, add new column containing a unique identifier
        inputDf[3] = inputDf.apply(createUniqueEnhancerID, axis=1)
    else:
        # if > 4 columns, remove the extra columns
        inputDf = inputDf[[0, 1, 2, 3]]
    # sort enhancers in ascending order based on chromosome and positions
    inputDf = inputDf.sort_values(by=[0, 1, 2], ascending=True)
    # write cleaned up enhancer data frame to file
    rawInputFile = 'temp/rawBed' + str(uuid.uuid4()) + '.bed'
    inputDf.to_csv(rawInputFile, sep="\t", index=False, header=None)
    return rawInputFile

def verifyFile(inputFilename, tissue):
    try:
        inputDf = pd.read_csv(inputFilename, sep='\t', header=None)
    except Exception as e:
        raise IncorrectFormatError(f"File is empty : {e}")

    if len(inputDf.columns) < 3:
        raise IncorrectFormatError("File must have at least 3 columns")
    if (inputDf[1].dtype != 'int64') or (inputDf[2].dtype != 'int64'):
        raise IncorrectFormatError("Columns are incorrect data type")

    try:
        # attempt to create a BedTool object from the file
        bed = BedTool(inputFilename)
        # if the file is successfully read, it's probably the right format
    except Exception as e:
        raise IncorrectFormatError(f"File is not in the correct format : {e}")

    if not tissueInFilename(inputFilename, tissue):
        raise TissueMismatchWarning("Tissue does not appear in filename")
    if inputDf.shape[0] < 50:
        raise FewEnhancersWarning("It is recommended to include at least 50 enhancers for better results")


# return true if filename contains tissue
def tissueInFilename(filename, tissue):
    # common names for each tissue
    additionalNames = {
        "aorta": ["artery"],
        "left-ventricle": ["left-chamber"],
        "liver": ["hepat"],
        "lung": ["pulmon"],
        "small-intestines": ["small-intestine", "small-bowel"],
        "dorsolateral-prefrontal-cortex": ["frontal-lobe-cortex", "DLPC"],
        "psoas-muscle": ["iliopsoas"],
        "right-ventricle": ["right-chamber"],
        "thymus": ["lymph"],
        "subcutaneous-adipose": ["subcutaneous-fat"],
        "omentum-visceral-adipose": ["visceral-fat"],
        "coronary-artery": ["heart-artery"],
        "tibial-artery": ["leg-artery"],
        "basal-ganglia-caudate": ["caudate-nucleus", "BGC"],
        "basal-ganglia-nucleus-accumbens": ["nucleus-accumben", "BGNA"],
        "basal-ganglia-putamen": ["putamen", "BGP"],
        "spinal-cord-cervical-c1": ["cervical-spinal-cord"],
        "brain-cortex": ["cerebral-cortex"],
        "breast-mammary": ["breast", "mammary"],
        "sigmoid-colon": ["pelvic-colon"],
        "transverse-colon": ["cross-colon"],
        "esophagus-GE-junction": ["gastroesophageal", "EGEJ"],
        "renal-cortex": ["kidney-cortex"],
        "skeletal-muscle": ["striat"],
        "pituitary": ["master-gland"]
    }

    stringsToCheck = [tissue]
    # add additional names, if there are any
    if tissue in additionalNames:
        stringsToCheck.extend(additionalNames[tissue])

    for string in stringsToCheck:
        parts = string.lower().split('-')
        # Check if all parts of tissue name appear in the filename
        if all(part.lower() in filename.lower() for part in parts):
            return True
    return False


# executeFunc
# algorithms - array of strings [distance, eqtl, chiaPet, abc]
# assembly - string, either "GRCh38" (GRCh38/hg38) or "GRCh37" (GRCh37/hg19)
def executeFunc(inputFilename, organ, algorithms, assembly, fp):
    # GRCx##-mapping.csv: maps organ to database filenames for each algorithm
    mappingDf = pd.read_csv('database/' + assembly + '-mapping.csv')
    # get organ files from row of df that matches organ chosen
    organFiles = mappingDf[mappingDf['organSelected'] == organ]
    # get filenames string from their data frame entry
    chiaDBfile = organFiles['peakachuFilename'].values[0]
    eqtlDBfile = organFiles['gtexFilename'].values[0]
    eqtlHelpDBfile = organFiles['gtexHelperFilename'].values[0]
    abcDBfile = organFiles['abcFilename'].values[0]

    # ensure the tissue works for the algorithms selected
    if (eqtlDBfile == "none" or eqtlHelpDBfile == "none") and "eqtl" in algorithms:
        print("ERROR: Selected tissue does not have working database for eQTL algorithm. (This is a problem "
              "with the tissue options in the frontend)\n")
        return
    if chiaDBfile == "none" and 'chiaPet' in algorithms:
        print("ERROR: Selected tissue does not have working database for chromatin loop algorithm. (This "
              "is a problem with the tissue options in the frontend)\n")
        return
    if abcDBfile == "none" and 'abc' in algorithms:
        print("ERROR: Selected tissue does not have working database for activity by contact algorithm. (This "
               "is a problem with the tissue options in the frontend)\n")
    # special case: renal-cortex organ is the only one that doesn't work for both assembly versions!
    if assembly == 'GRCh37' and organ == 'renal-cortex':
        print("ERROR: special case! Assembly GRCh37 does not work for tissue 'renal-cortex'! This is the ONLY tissue "
              "that doesn't work for both 37 and 38\n")
        return
    # special case: abc algorithm does not work for assembly 38!
    if assembly == 'GRCh38' and 'abc' in algorithms:
        print("ERROR: special case! ABC algorithm does not work for assembly GRCh38!\n")
        return

    temp = "temp/"
    myuuid = str(uuid.uuid4())
    imagesFileName = temp + 'images-' + myuuid
    os.mkdir(imagesFileName[0:len(imagesFileName)])
    # make directories for each algorithm
    chiaOutputFile = imagesFileName + '/peakachu_linked' + myuuid + '.bed'
    distanceOutputFile = imagesFileName + '/distance_linked' + myuuid + '.bed'
    eqtlOutputFile = imagesFileName + '/eqtl_linked' + myuuid + '.bed'
    abcOutputFile = imagesFileName + '/abc_linked' + myuuid + '.bed'

    rawInputFile = cleanInputFile(inputFilename)

    # run each algorithm in parallel
    if "chiaPet" in algorithms:
        p1 = Process(target=chromatinLoopBased.startPoint, args=[rawInputFile, chiaDBfile, chiaOutputFile, assembly])
        p1.start()
    if "distance" in algorithms:
        p2 = Process(target=distanceBased.startPoint, args=[rawInputFile, distanceOutputFile, assembly])
        p2.start()
    if "eqtl" in algorithms:
        p3 = Process(target=eQTLbased.startPoint,
                     args=[rawInputFile, eqtlDBfile, eqtlHelpDBfile, eqtlOutputFile, assembly])
        p3.start()
    if "abc" in algorithms:
        p4 = Process(target=abcBased.startPoint, args=[rawInputFile, abcDBfile, abcOutputFile])
        p4.start()

    if "chiaPet" in algorithms:
        p1.join()
        if p1.exception:
            if "chromosome sort ordering" in str(p1.exception):
                raise Exception("The file provided does not belong to the associated organ")
            else:
                raise Exception("Chromatin loop: Something went wrong with the file, please check your upload file")
    if "distance" in algorithms:
        p2.join()
        if p2.exception:
            if "chromosome sort ordering" in str(p2.exception):
                raise Exception("The file provided does not belong to the associated organ")
            else:
                raise Exception("Distance: Something went wrong with the file, please check your upload file")
    if "eqtl" in algorithms:
        if p3.exception:
            if "chromosome sort ordering" in str(p3.exception):
                raise Exception("The file provided does not belong to the associated organ")
            else:
                raise Exception("eQTL: Something went wrong with the file, please check your upload file")
        p3.join()
    if "abc" in algorithms:
        if p4.exception:
            if "chromosome sort ordering" in str(p4.exception):
                raise Exception("The file provided does not belong to the associated organ")
            else:
                raise Exception(
                    "Activity by Contact: Something went wrong with the file, please check your upload file")
        p4.join()

    # returns chart.py json object
    charts_json = mergeMethods.startPoint(chiaOutputFile, distanceOutputFile, eqtlOutputFile, abcOutputFile,
                                          imagesFileName + '/', algorithms)

    zipFile = shutil.make_archive(imagesFileName, 'zip', imagesFileName)

    # store result here
    chart.insert_history(fp, charts_json, assembly, organ, algorithms, zipFile)

    # imagesFileName = imagesFileName[len(temp) - 1:len(imagesFileName)]
    # os.remove(chiaOutputFile)
    # os.remove(distanceOutputFile)
    # os.remove(eqtlOutputFile)

    os.remove(rawInputFile)
    return charts_json


def runInParallel(*fns):
    proc = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()


@app.route('/api/test')
def testApi():
    return jsonify({"hello": "world"})


# In[3]:
@app.route('/api/database_download/<filename>')
def database_download(filename):
    path = 'temp'
    zipname = filename + '.zip'
    with open(os.path.join(path, zipname), 'rb') as f:
        data = f.readlines()
    # os.remove(os.path.join(path, zipname))
    # shutil.rmtree(os.path.join(path,filename))
    return Response(data, headers={
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename=%s;' % zipname
    })


@app.route('/api/download/<filename>')
def download(filename):
    path = 'static'
    return send_file(os.path.join(path, filename), as_attachment=True)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['bed', 'gz']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/api/upload', methods=['GET', 'POST'])
# def hello():
#     try:
#         if request.method == 'GET':
#             return render_template('index1.html')
#         elif request.method == 'POST':
#             organ = request.form['organ']
#             if (organ == 'Select a tissue'):
#                 # return redirect("/",code=302)
#                 raise Exception('tissue name not supported')
#
#             email = request.form['email']
#             # check if the post request has the file part
#             if 'file' not in request.files:
#                 raise Exception('No file part')
#
#             file = request.files['file']
#             if file.filename == '':
#                 flash('No selected file')
#                 raise Exception('No Selected file')
#
#             # TODO: Current fp does not consider assembly, tissue, or algorithm select. It should!
#             fp = history.compute_sha256(file)
#
#             historyResult = history.input_file_exists(fp)
#
#             if (verify_jwt_in_request(optional=True)):
#                 user.insert_fp_to_user_history(get_jwt_identity(), fp)
#
#             if historyResult:
#                 result = history.get_existing_file(historyResult["file"])
#                 byte_stream = io.BytesIO(result.read())
#
#                 with zipfile.ZipFile(byte_stream, 'r') as zip_ref:
#                     zip_ref.extractall(f"./temp/{result.filename}")
#                 return jsonify({"filename": f"/{result.filename}", "hash": fp}), 200
#             else:
#                 assembly = request.form['assembly']
#
#                 if file and allowed_file(file.filename):
#                     filename = "temp/" + secure_filename(file.filename)
#                     file.save(filename)
#
#                     algorithms = request.form['algorithms']
#                     result = executeFunc(filename, organ, algorithms, assembly)
#
#                     if email != '':
#                         msg = Message('Your enhancerGenie file Download', sender='enhancergenie@gmail.com',
#                                       recipients=[email])
#                         msg.html = render_template('emailFinal.html', filename=result)
#                         mail.send(msg)
#                         logger.info('email sent to ' + email)
#                         flash('A link to download the results as sent in an email sent to ' + email)
#
#                     # zipname = f"./temp{images}.zip"
#                     # with open(zipname, 'rb') as f:
#                     #     f.readlines()
#                     #
#                     # # Add history to db
#                     # file_id = history.insert_result_zip(zipname, fp)
#                     # history.insert_history_document(fp, file_id, assembly, organ, algorithms)
#                     return jsonify(result), 200
#                     # return jsonify({"filename": images, "hash": fp}), 200
#                 else:
#                     raise Exception('file  is not properly formatted')
#
#             # TODO: Need to add hash to User's "history" attr
#
#
#     except Exception as e:
#         logger.error(str(e))
#         flash(str(e), 'error')
#         return jsonify({"status": "error", "message": traceback.format_exc()}), 500

# New Upload
@app.route('/api/upload', methods=['GET', 'POST'])
def hello():
    try:
        organ = request.form['organ']
        assembly = request.form['assembly']
        algorithms = request.form['algorithms']

        if organ == 'Select a tissue':
            # return redirect("/",code=302)
            raise Exception('tissue name not supported')

        email = request.form['email']
        # check if the post request has the file part
        if 'file' not in request.files:
            raise Exception('No file selected')

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            raise Exception('No Selected file')

        fp = chart.compute_combined_sha256(file, assembly, organ, algorithms)

        chartResult = chart.input_selection_exists(fp)

        if verify_jwt_in_request(optional=True):
            user.insert_fp_to_user_history(get_jwt_identity(), fp)

        if email != '':
            msg = Message('Your enhancerGenie result', sender='enhancergenie@gmail.com',
                            recipients=[email])
            # msg.html = render_template('emailFinal.html', filename=result)
            # TODO: Make hostname based on current server
            msg.body = f"Here is your result: http://localhost:3000/chart_results/{fp}"
            mail.send(msg)
            logger.info('email sent to ' + email)
            flash('A link to download the results as sent in an email sent to ' + email)

        if chartResult:
            # if found, return data in there
            return jsonify({"result": chartResult["data"], "hash": fp}), 200
        else:
            if file and allowed_file(file.filename):
                filename = "temp/" + secure_filename(file.filename)
                file.save(filename)

                result = executeFunc(filename, organ, algorithms, assembly, fp)

                # Add result to db
                # chart.insert_history(fp, result, assembly, organ, algorithms)
                # return jsonify(result), 200
                return jsonify({"result": result, "hash": fp}), 200
            else:
                raise Exception('file  is not properly formatted')

    except Exception as e:
        logger.error(str(e))
        flash(str(e), 'error')
        return jsonify({"status": "error", "message": traceback.format_exc()}), 500


@app.route('/api/tissues', methods=['GET'])
def tissues():
    try:
        f = open('tissues.json')
        tissues = json.load(f)
        f.close()
        return jsonify(tissues)
    except Exception as e:
        return jsonify({"status": "error", "message": traceback.format_exc()}), 500


@app.route('/temp/<path:path>')
@app.route('/results/temp/<path:path>')
def send_image(path):
    return send_from_directory('temp', path)


@app.route('/api/checkFilesExist', methods=['POST'])
def check_files_exist():
    try:
        file_paths = request.json

        if not isinstance(file_paths, list):
            return jsonify({"error": "Invalid input format"}), 400

        existing_files = [path for path in file_paths if os.path.isfile(path)]

        return jsonify({"existingFiles": existing_files})

    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while processing the request"}), 500


@app.route("/api/history", methods=['GET'])
def get_history():
    # TODO: Return this data from db based on provided access_token of user

    return jsonify({
        "id": 1,
        "assembly": "GRCh37",
        "tissue": "Liver",
        "algorithms": ["distance", "eqtl"],
        "date": "Dec 13 2:16 PM"
    },
        {
            "id": 2,
            "assembly": "GRCh37",
            "tissue": "Liver",
            "algorithms": ["distance", "eqtl"],
            "date": "Dec 13 2:16 PM"
        },
        {
            "id": 3,
            "assembly": "GRCh37",
            "tissue": "Liver",
            "algorithms": ["distance", "eqtl"],
            "date": "Dec 13 2:16 PM"
        })

# new metadata
@app.route("/api/history/metadata", methods=['POST'])
def get_history_metadata():
    if verify_jwt_in_request(optional=True):
        username = get_jwt_identity()
        fps = user.get_user_history(username)
    else:
        data = request.get_json()
        fps = data["fps"]

    result = []

    query = request.args.get("query")
    if query == None:
        query = ""

    page = request.args.get("page")
    if page == None:
        page = 1

    # TODO: Add metadata to result list
    res, count = chart.get_multiple_history(fps, query, int(page))
    for doc in res:
        if doc != None:
            oid_str = str(doc['_id'])
            int_val = int(hashlib.sha1(oid_str.encode()).hexdigest(), 16)
            result.append({
                "id": int_val,
                "assembly": doc["assembly"],
                "tissue": doc["tissue"],
                "algorithms": ast.literal_eval(doc["algorithms"]),
                "fingerprint": doc["fingerprint"]
            })

    return jsonify({
        "count": count,
        "results": result,
    })

@app.route("/api/history/delete", methods=['POST'])
def remove_history_item():
    if verify_jwt_in_request(optional=True):
        username = get_jwt_identity()
        data = request.get_json()
        user.delete_history_item(username, data["fp"])
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Must be authorized"}), 401


# New History
@app.route("/api/history/results", methods=['POST'])
def get_history_results():
    fp = request.get_json()["fp"]

    # This only return JSON data
    result = chart.get_existing_file_from_hash(fp)
    if result is None:
        return jsonify({"error": "did not find a file with provided fp"})

    return jsonify(result), 200


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json

    # get user information
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 401

    # check if username is already exists
    user_collection = client['Users']
    if user_collection.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400

    # encrypt user password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # store user information
    try:
        user_collection.insert_one({'username': username, 'password': hashed_password})
        return jsonify({'message': 'User registered successfully'}), 200
    except pymongo.errors.PyMongoError as e:
        print(e)
        return jsonify({'error': 'Failed to register user'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    # Get user information from database
    user_collection = client['Users']
    user = user_collection.find_one({'username': username})

    if not user:
        return jsonify({'error': 'Username does not exist'}), 402

    stored_password = user.get('password')
    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
        access_token = create_access_token(identity=username)
        return jsonify({'message': 'Login successful', 'token': access_token}), 200
    else:
        return jsonify({'error': 'Wrong password'}), 401


@app.route('/api/download', methods=['POST'])
def download_file():
    data = request.json
    fp = data['fingerprint']

    file = chart.get_zip_file(fp)
    if file is not None:
        return Response(
            file.read(),
            mimetype='application/zip',
            headers={'Content-Disposition': 'attachment; filename="%s.zip"' % file.name}
        )
    else:
        return {'message': 'File not found'}, 404

