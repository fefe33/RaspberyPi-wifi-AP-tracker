#this is the server to display the discovered endpoints to users in HTML/CSS
from flask import Flask, render_template, redirect, request, session
import sqlite3, argparse, os, json
SECRET = os.urandom(64)

p = argparse.ArgumentParser()
p.add_argument('-db', '--database', nargs=1, type=str, help='path to parent dir of database(default is dir \'path_to/project_folder/database\')')
p.add_argument('-a','--addr', nargs=2, type=str, help='this is the address to serve on (if not using with wsgi)')
args = p.parse_args()

#host
try:
    host = args.addr[0]
    port = int(args.addr[1])
except:
    print('failed to parse address, setting to default (\'0.0.0.0:8080\'). --> if running with wsgi ignore these messages')
    host = '0.0.0.0'
    port = 8080
#database
try:
    database_path = args.database[0]
    #check that the database exists
    if 'addressbook.db' in os.listdir(database_path):
        database = database+'/addressbook.db'
except:
    print('failed to parse database. setting to default. see -h for help.')
    database = os.path.dirname(os.path.realpath(__file__))+'/addressbook.db'

database_path = os.path.dirname(os.path.realpath(__file__))+'/databases/addressbook.db'
#define the server
server = Flask(__name__, static_folder='markup/static', template_folder='markup/templates')
#set the secret key
server.secret_key = SECRET

#define the main route
@server.route('/', methods=['GET'])
def index():
    #returns the main page
    return render_template('index.html')
#chart route
@server.route('/signal')
def chart():
    return render_template('chart.html')

#route for access point data
@server.route('/log/ap', methods=['POST'])
def ap_log():
    #connnects to the database
    Cx = sqlite3.connect(database_path)
    c = Cx.cursor()
    #gets the devices:
    c.execute('SELECT bssid,ssid,mode,channel,last_seen  FROM known ORDER BY last_seen')
    devices = c.fetchall()
    c.close()
    print('returning request data')
    return json.dumps({'devices':devices})
#route for signal data
@server.route('/log/sig', methods=['POST'])
def sig_log():
    #connect to db
    Cx = sqlite3.connect(database_path)
    c = Cx.cursor()
    #get the total scans from the global table
    c.execute('SELECT * FROM global')
    scan_timestamps = [i[1] for i in c.fetchall()]
    total_scans = len(scan_timestamps)
    #
    #get bssids and write to var
    c.execute('SELECT bssid,discovered_at FROM known')
    bssids = c.fetchall()
    tms = [i[1] for i in bssids]
    bssids = [i[0] for i in bssids]
    dataset = dict()
    #for each bssid, select all non-bssid values from the signals table
    for i in range(len(bssids)):
        c.execute('SELECT signal,scan_number FROM signals WHERE bssid={}'.format(repr(bssids[i])))
        #convert the scan numbers to timestamps by fetching from the global table



        dataset[bssids[i]] = {'discoveredAt':tms[i], 'data':c.fetchall()}
    c.close()
    return json.dumps({'dataset':dataset, 'bssids':bssids, 'total_scans': total_scans, 'labels':scan_timestamps})

if '__main__' in __name__:
    server.run(host=host, port=port)
