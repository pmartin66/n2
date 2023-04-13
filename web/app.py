
from flask import Flask, render_template, request, redirect, send_file
import boto3 
from pymysql import connections
import os
import random
import argparse


app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "passwors"
DATABASE = os.environ.get("DATABASE") or "employees"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = 3306 or int(os.environ.get("DBPORT")) 
bucket_name= os.environ.get("background") or "kuberneteslovers"
key_id= os.environ.get("key_id")
access_key= os.environ.get("access_key")
session_token=os.environ.get("session_token")
groupname=os.environ.get("group-name") or "group 13"
fileName= "image.jpg"

#Download the Image from s3 bucket
def download_file(fileName, bucket_name):
    
    directory = "/app/templates"
    if os.path.exists(directory) and os.path.isdir(directory):
        print("Directory exists")
    else:
        os.makedirs(directory)
    
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource('s3',
         aws_access_key_id= key_id,
         aws_secret_access_key= access_key,
         aws_session_token = session_token
         )
    # s3 = boto3.resource('s3',
    #      aws_access_key_id= 'ASIAYRPULG7I45DYOX3B',
    #      aws_secret_access_key= 'ovggdhJVxPGjQlTkSKiYLsLNMKWoAPGfFCLy2nYU',
    #      aws_session_token = 'FwoGZXIvYXdzEOf//////////wEaDBMS9QZwad+2q3EKaiLJAVDgAJeAOZl9DS3V/vcd8wjMKk03DLIfEYjBAgMYDDQpcX6pRqPBK+fDNBpcDg2NXC+QU3c9mhAs8DlagMJtByNKjNcnq3S+rEWyYgfuNJZ1fv58L7IoJLg70i7txcvon8H/EQzkrU3ZWjunm9wbokFg0sijj/rlsiphOmKYBtQmeAR5d8pSt08Dhg30qeTOlmpfCbOxLFCQzmFTTAgLGIIUeRoKeAD8qy9v0ltNSoviwXJhMvA/EwdW3282ZA164v9dXiNwRPJxUyjD49qhBjIt0IRUzHnPJjCADHT/0EX0Xbhf7HDpiqBG2/ZBsoy/ODjfHVLityMoy5coPTTK'
    #      )
    
    # s3.download_file('bucketURL', 'image.jpg', 'r/img/image.jpg')
    print({bucket_name})
    return s3.Bucket(bucket_name).download_file('image.jpg','/app/templates/image.jpg')
    # s3.Bucket(bucketURL).download_file(file_name, output)

    

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host= DBHOST,
    port=DBPORT,
    user= DBUSER,
    password= DBPWD, 
    db= DATABASE
    
)
output = {}
table = 'employee';

# Define the supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}


# Create a string of supported colors
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Generate a random color
COLOR = random.choice(["red", "green", "blue", "blue2", "darkblue", "pink", "lime"])


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', color=color_codes[COLOR], group=groupname)

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', color=color_codes[COLOR])
    
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']
    


  
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, color=color_codes[COLOR])

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes[COLOR])


@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql,(emp_id))
        result = cursor.fetchone()
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], color=color_codes[COLOR])

if __name__ == '__main__':
    download_file(fileName, bucket_name)
    # Check for Command Line Parameters for color
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =" + args.color)
        COLOR = args.color
        if COLOR_FROM_ENV:
            print("A color was set through environment variable -" + COLOR_FROM_ENV + ". However, color from command line argument takes precendence.")
    elif COLOR_FROM_ENV:
        print("No Command line argument. Color from environment variable =" + COLOR_FROM_ENV)
        COLOR = COLOR_FROM_ENV
    else:
        print("No command line argument or environment variable. Picking a Random Color =" + COLOR)

    # Check if input color is a supported one
    if COLOR not in color_codes:
        print("Color not supported. Received '" + COLOR + "' expected one of " + SUPPORTED_COLORS)
        exit(1)

    app.run(host='0.0.0.0',port=81,debug=True)
