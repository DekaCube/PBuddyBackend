import flask
import datetime
from flask import request, jsonify, abort, render_template, send_from_directory
from datetime import datetime
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

DYNAMO_TABLE = "packagebuddy"




app = flask.Flask("pbserver",static_folder='/static')
app.config["DEBUG"] = True

dummy_data = {
    "TrackingID" : "123456",
    "last_updated" : str(datetime.now()),
    "lat" : "26.36",
    "lon" : "-80.12",
    "max_temp" : 105,
    "current_temp" : 78,
    "max_gs" : "7.66",
}

error = {"error":"invalid or no ID"}

@app.route('/post', methods=['POST'])
def put():
    global table
    if request.method == "POST":
        args = request.form
        print(args)
        #TODO : ERROR HANDLING
        table = dynamo_connect()
        item = {
            "TrackingID":args["trackingID"],
            "last_updated" : args["last_updated"],
            "lat": str(args["lat"]),
            "lon": str(args["lon"]),
            "max_gs" : str(args["max_gs"]),
            "max_temp" : args["max_temp"],
            "current_temp": args["current_temp"]
        }
        table.put_item(Item=item)
        return '{"success":"true"}'
    
    


@app.route('/track', methods=['POST'])
def track():
    global table 
    if request.method == 'POST':
        arg = request.form.get("tracking")
        if arg == None:
            abort(404,description="Tracking ID does not exist")
        print("TrackingID = {}".format(arg))
        table = dynamo_connect()
        resp = table.query(KeyConditionExpression=Key('TrackingID').eq(arg))
        item = resp.get("Items")
        print('Item = {}'.format(item))
        if item != None and len(item) != 0:
            item = item[0]
        else:
            abort(404,description="Tracking ID does not exist")
        
        return render_template("index.html",content=item)
    abort(404,description="Tracking ID does not exist")

@app.route('/floating-labels.css')
def css():
    return send_from_directory("static","floating-labels.css")

@app.route('/package.png')
def image():
    return send_from_directory("static","package.png")

@app.route('/')
def main():
    return send_from_directory("static","index.html")

@app.route('/test', methods=['GET','POST'])
def home():
    if request.method == 'GET':
        query_parameters = request.args
        if query_parameters.get("tracking") == "123456":
            return jsonify(dummy_data)
        abort(404,description="Invalid or non-existant tracking parameter")

def dynamo_connect():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMO_TABLE)
    return table

table = dynamo_connect()
table.put_item(Item=dummy_data)
app.run()


