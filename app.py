import hashlib
import os
import pdb
import sys
import uuid
import json
import csv
import io
import zipfile
import pymysql
import pandas as pd
from flask import (Flask, abort, jsonify, redirect, request, send_file,
                   session, url_for)
from flask_cors import CORS

HR_dir = 'HR_data/'
TH_dir = 'TH_data/'

app = Flask(__name__)
app.secret_key = 'IoT&EmotiBit%RestAPI_IoT&EmotiBit%RestAPI_IoT&EmotiBit%RestAPI'
CORS(app)

conn = pymysql.connect(
    host='db',
    user='root',
    password='NotStrongPassword',
    db='emotibit',
    charset='utf8mb4'
)

cursor = conn.cursor()
cursor.execute("USE emotibit")
cursor.close()

print(f'\nConnection with DB is successful\n', file=sys.stdout)


@app.route('/', methods=['GET'])
def home():
    return {
        'message': 'Server up and running!',
        'endpoints': {
            'workouts': '/workouts'
        }
    }

@app.route('/login', methods=['GET'])
def login():
    email = request.form.get('email')
    email = 'lacami01@louisville.edu'
    password = request.form.get('password')
    password = 'password'

    # Validate the user's credentials
    if validate_user(email, password):
        # Generate a unique access token for the user
        access_token = str(uuid.uuid4())

        # Store the access token in the session
        session['access_token'] = access_token

        # Return the access token to the client
        response = {'access_token': access_token}
        return response

    else:
        # Return an error message to the client
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/workouts/', methods=['GET', 'POST'])
def get_workouts():
    global conn
    if request.method == 'GET':
        try:
            page = request.args.get('page', default=1, type=int)
            limit = request.args.get('limit', default=5, type=int)
            start_index = (page - 1) * limit
            end_index = start_index + limit

            cursor = conn.cursor()
            query = "SELECT * FROM WORKOUTS LIMIT %s OFFSET %s"
            cursor.execute(query, [limit, (page-1)*limit])
            workouts = []
            for row in cursor:
                workouts.append({
                    'id': row[0],
                    'extension': row[1]
                })

            current_workouts = workouts
            response = {'workouts': current_workouts}
            response['current_page'] = page
            response['results_per_page'] = limit
            response['total_workouts'] = len(workouts)
            response['total_pages'] = int(
                len(workouts) / limit) + (len(workouts) % limit > 0)

            return response
        except Exception as ee:
            print(f'\nError: {ee}\n', file=sys.stderr)
            abort(404)

    if request.method == 'POST':
        try:
            conn.ping()
            uploaded_file_HR = request.files.get('HRFile')
            uploaded_file_TH = request.files.get('THFile')
            # print(
            #     f'For HR we received : {uploaded_file_HR.filename.split(".")[1]}', file=sys.stderr)
            # print(
            #     f'For TH we received : {uploaded_file_TH.filename}', file=sys.stderr)
            
            try:
                # Create new workout
                cursor = conn.cursor()
                query = "INSERT INTO WORKOUTS()VALUES()"
                cursor.execute(query)
                workout_id = cursor.lastrowid

                # Add HR registers to database
                data = pd.read_csv(uploaded_file_HR)
                for index, row in data.iterrows():
                    query = "INSERT INTO HR_DATA (bpm, workout_id) VALUES (%s, %s)"
                    cursor.execute(query, [row["HR"], workout_id])

                # Add TH registers to database
                data = pd.read_csv(uploaded_file_TH)
                for index, row in data.iterrows():
                    query = "INSERT INTO TH_DATA (temperature, workout_id) VALUES (%s, %s)"
                    cursor.execute(query, [row["TH"], workout_id])

                cursor.close()
                conn.commit()
                # HR_csv = csv.reader(io.StringIO(uploaded_file_HR.stream.read().decode('utf-8')))
                # next(HR_csv)
                # for row in HR_csv:
                #     print(f'\n{row}')
                # print(HR_csv, file=sys.stderr)
                # # for row in HR_csv:
                # #     print(f'\n{row}', file=sys.stderr)
                uploaded_file_HR.stream.seek(0)
                uploaded_file_TH.stream.seek(0)
                uploaded_file_HR.save(f'{HR_dir}{workout_id}.{uploaded_file_HR.filename.split(".")[1]}')
                uploaded_file_TH.save(f'{TH_dir}{workout_id}.{uploaded_file_TH.filename.split(".")[1]}')
                

                return jsonify({
                    'id': workout_id,
                    'message': 'Workout created'
                }, 201)

            except Exception as ee:
                conn = pymysql.connect(
                    host='db',
                    user='root',
                    password='NotStrongPassword',
                    db='emotibit',
                    charset='utf8mb4'
                )
                print(f'\nError: {ee}\n', file=sys.stderr)
                abort(500)

            # Add TH registers to database

            return jsonify({'message': 'Workout has been created'}), 200
        except Exception as ee:
            print(f'{ee}', file=sys.stderr)
            print(f'\nError: {ee}\n', file=sys.stderr)
            abort(404)

@app.route('/workouts/<int:workout_id>/', methods=['GET'])
def get_workout_file(workout_id):
    try:
        with zipfile.ZipFile(f'workout_{workout_id}.zip', "w") as my_zip:
            my_zip.write(f'{HR_dir}{workout_id}.csv')
            my_zip.write(f'{TH_dir}{workout_id}.csv')

        response = send_file(
            f'workout_{workout_id}.zip',
            download_name = f'workout_{workout_id}.zip',
            as_attachment = True
        )
        return response, 200
    
    except Exception as ee:
        print(f'\nError: {ee}\n', file=sys.stderr)
        abort(404)
    finally:
        try:
            os.remove(f'workout_{workout_id}.zip')
        except Exception:
            pass

@app.route('/workout/<int:workout_id>/HR/', methods=['GET'])
def get_workout_HRdata(workout_id):
    global conn
    try:
        conn.ping()
        query = """SELECT ww.id, hrd.bpm
            FROM HR_DATA as hrd, WORKOUTS as ww
            WHERE hrd.workout_id = ww.id AND ww.id = %s
            ORDER BY hrd.id ASC"""
        cursor = conn.cursor()
        cursor.execute(query, [workout_id])
        HR_data = []
        for row in cursor:
            HR_data.append({
                'bpm': row[1]
            })
        return jsonify({'data': HR_data}, 200)
    except Exception as ee:
        conn = pymysql.connect(
            host='db',
            user='root',
            password='NotStrongPassword',
            db='emotibit',
            charset='utf8mb4'
        )
        print(f'\nError: {ee}\n', file=sys.stderr)
        abort(404)

@app.route('/workout/<int:workout_id>/TH/', methods=['GET'])
def get_workout_THdata(workout_id):
    global conn
    try:
        conn.ping()
        query = """SELECT ww.id, temp.temperature
            FROM TH_DATA as temp, WORKOUTS as ww
            WHERE temp.workout_id = ww.id AND ww.id = %s
            ORDER BY temp.id ASC"""
        cursor = conn.cursor()
        cursor.execute(query, [workout_id])

        TH_data = []
        for row in cursor:
            TH_data.append({
                'temperature': row[1]
            })

        return jsonify({'data': TH_data}, 200)

    except Exception as ee:
        conn = pymysql.connect(
            host='db',
            user='root',
            password='NotStrongPassword',
            db='emotibit',
            charset='utf8mb4'
        )
        print(f'\nError: {ee}\n', file=sys.stderr)
        abort(404)

@app.route('/workouts/re/<int:workout_id>/<string:type>/', methods=['GET'])
def get_workout_and_redirect(workout_id, type):
    try:
        if type.upper() == 'HR':
            response = send_file(
                f'{HR_dir}{workout_id}.csv', download_name=f'{workout_id}_HR.csv', as_attachment=True)
        elif type.upper() == 'TH':
            response = send_file(
                f'{TH_dir}{workout_id}.csv', download_name=f'{workout_id}_TH.csv', as_attachment=True)
    except Exception as ee:
        print(f'\nError: {ee}\n', file=sys.stderr)
        abort(404)

    return redirect(url_for('home'))


@app.errorhandler(404)
def not_found(error):
    # Create a JSON response with an error message
    response = jsonify({'error': 'Not Found'})
    # Set the status code of the response
    response.status_code = 404
    # Return the response
    return response


def validate_user(email, password):
    cursor = conn.cursor()
    sql = "SELECT id, password_hash, password_salt FROM accounts WHERE email=%s"
    cursor.execute(sql, [email])
    result = cursor.fetchone()
    cursor.close()

    if (result):
        salt_hashed = result[2]
        passwd = password+salt_hashed
        password_hash = hashlib.sha256(passwd.encode())
        if (password_hash.hexdigest() == result[1]):
            return True
        else:
            return False
    else:
        print(f'No Result', file=sys.stderr)
        return False


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
