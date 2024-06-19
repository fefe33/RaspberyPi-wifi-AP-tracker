'''
    this app continually requests nearby networks and logs them to a database at a given frequency
    3 tables exist. one for all values collectively learned, one for the signal strength of each access point at a relative scan number, and one for all collective scans and their timestamps
    a separate server can be run to view detected changes and timestamps live
'''
import time, os, argparse, subprocess, sqlite3





class app:
    def __init__(self, dbpath, freq, debug):
        self.dbpath = dbpath
        self.frequency = freq
        self.debug = debug
        #total_scans is read from the db and set at runtime
        self.total_scans = 0
    # writes a data point to the signal table
    def add_signal(self, cursor, connection, bssid, signal, scan_number):
        cursor.execute('INSERT INTO signals VALUES ({},{},{})'.format(repr(bssid), signal, scan_number))
        connection.commit()
        return True


    #update a timestamp with the given db cursor        
    def update_timestamp(self, cursor, connection, bssid, timestamp):
        cursor.execute('UPDATE known SET last_seen={} WHERE bssid={}'.format(timestamp, repr(bssid)))
        connection.commit()
        return True
     #add a device using the given cursor and connection
    def write_device(self,cursor, connection, cmd):
        cursor.execute(cmd)
        connection.commit()
        return True
    #build the table in the database
    def build_db(self):
        #connect:
        Cx = sqlite3.connect(self.dbpath)
        c = Cx.cursor()
        #try to create the tables (if they havent already been created)
        try:
            #known table holds all discovered access point data
            c.execute('CREATE TABLE known (bssid TEXT PRIMARY KEY, ssid TEXT, mode TEXT, channel INTEGER, discovered_at INTEGER, last_seen NUMBER)')
            #signal table contains complete history of signal strength attained from each scan
            #scan_number is 
            c.execute('CREATE TABLE signals (bssid TEXT, signal INTEGER, scan_number INTEGER)')
            #create a table to hold global attribuites
            #contains a record of each scan and the time it occurred
            c.execute('CREATE TABLE global (scan_number INTEGER, timestamp INTEGER)')
            Cx.commit()
            #set the total number of scans to zero
            Cx.commit()
            c.close()
        except:
            if self.debug:
                print('table already exists.')
            c.close()
            pass
        return True
    #read all ssid and bssids from table
    def get_devices(self, cursor):
        cursor.execute('SELECT bssid FROM known')
        return cursor.fetchall()        
            
    #this gets nearby wifi access points with nmcli and parses the output
    def get_neighbors(self):
        #run the command to get nearby devices and wait for it to complete
        proc = subprocess.Popen(['nmcli', 'dev', 'wifi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        #get the output/errors
        out, err = proc.communicate()
        timestamp = time.time()
        lines = out.decode('utf-8').split('\n')[1:-1]
        try:
            if len(lines[0]) <= 2:
                print('networking not enabled')
                exit(-1)
        except:
            print('networking not enabled or nmcli not installed.')
            exit(-1)
        devices = []
        for i in lines:
            line = i.split(' ')
            b = []
            #get all nonzero length values
            for j in line:
                if len(j)>=1 and j!='*':
                    b.append(j)
            devices.append(b)
        ##write the values to the table
        if self.debug==True:
            print('devices: ', devices)
        bssids = [i[0] for i in devices]
        ssids = [i[1] for i in devices]
        #if the name is '--', its a hidden network. store its ssid as value 'HIDDEN'
        for i in ssids:
            if i == '--':
                if self.debug:
                    print('hidden network at {} detected'.format(bssids[ssids.index(i)]))
                i = 'HIDDEN'
        modes = [i[2] for i in devices]
        channels = [i[3] for i in devices]
        signals = [i[6] for i in devices]
        return {'len':len(bssids), 'bssids':bssids, 'ssids':ssids, 'modes':modes, 'channels':channels, 'signals':signals, 'timestamp': timestamp}
        #takes the object output from the above function and parses it to a list of SQL statements
    #documents the scan number and time of occurance
    def document_scan(self, cursor, connection, scan_number, timestamp):
        cursor.execute('INSERT INTO global VALUES ({},{})'.format(scan_number, timestamp))
        connection.commit()
        return True

    def run_commands(self, obj):
    
        makecmdknown = lambda t:'INSERT INTO known VALUES ({},{},{},{},{},{})'.format(repr(t[0]),repr(t[1]),repr(t[2]),t[3],t[4],t[5])
        cmds = []

        #connect to DB
        connection = sqlite3.connect(self.dbpath)
        cursor = connection.cursor()
        #get the total scans from the global table -- (the length of the global table)
        cursor.execute('SELECT * FROM global')
        scan_number = cursor.fetchall()
        scan_number = len(scan_number)


        print('scan number: ', scan_number)
        #write the signals to the signals table
        for i in range(obj['len']):
            self.add_signal(cursor, connection, obj['bssids'][i], obj['signals'][i], scan_number)
        #get known bssids
        logged_bssids = [i[0] for i in self.get_devices(cursor)]
        #if the scan_number isnt 0 and the obj['len'] doesnt match the number of records in the known table
        if scan_number != 0 and (obj['len'] != len(logged_bssids)):
            #find all the known bssids that arent in obj['bssids'] and add them to the signals table with a value of zero
            for i in logged_bssids:
                if i not in obj['bssids']:
                    self.add_signal(cursor, connection, i, 0, scan_number)
        
        if self.debug:
            print('known devices', logged_bssids)        
        for i in range(obj['len']):
            #if the bssid matches one of the one of the values in logged_bssid return continue
            cmds.append((obj['bssids'][i], obj['ssids'][i], obj['modes'][i], obj['channels'][i], scan_number, obj['timestamp']))
            #run the commands
        if self.debug:
            print(cmds) 
        #get the time and make count (in case of timestamp update)
        new_ts = time.time()
        n = 0 #counter
        for i in cmds:
            try:
                cmd = makecmdknown(i)
                #write the device to the known table
                self.write_device(cursor, connection, cmd)
                if self.debug:
                    print('added network: ', i[1])
            except:
                if self.debug:
                    print('bssid has already been logged. updating timestamp')
                success = self.update_timestamp(cursor,connection, obj['bssids'][n], repr(new_ts))
                if self.debug: 
                    print('update success: ',success)
            n += 1

        #document this scan's occurance
        self.document_scan(cursor, connection, scan_number, obj['timestamp'])
        cursor.close()               
        return True
    
    def run(self):
        application = app(self.dbpath, self.frequency, self.debug)
        application.build_db()
        while True:
            print('scan_success: ', application.run_commands(application.get_neighbors()))
            print('waiting {} seconds till next scan'.format(str(self.frequency)))
            time.sleep(self.frequency)


parser = argparse.ArgumentParser(
            prog='nearby.py',
            description='continually logs data about nearby access points to database, waiting a given time interval between scans'
        )
parser.add_argument('-i', '--interval', required=True, nargs=2, type=str, help='specifies the time waited between scans. use <interval> <unit> where units=[\'sec\', \'min\', \'hrs\', \'days\']')
parser.add_argument('-d','--database', nargs=1, type=str, help='specifies the path to where the database will be stored.')
parser.add_argument('--debug', nargs=1, type=str, help='more verbose output with debug-related info (use \'on\'/\'off\')')

conversions = {
        'sec':1,
        'min':60,
        'hrs':3600,
        'day':86400
        }

args = parser.parse_args()
#handle them
#try to get the debug flag
try:
    debug = args.debug[0]
    if debug == 'on':
        debug = True
    elif debug == 'off':
        debug=False
    else:
        Exception(KeyError('value not in [\'on\', \'off\']'))
except:
    debug = False
    print('no debug set. default=off')
#try to convert the interval
try:
    interval = int(args.interval[0])*conversions[args.interval[1]]
except:
    print('failed to parse scan interval. use <interval> <unit> where interval is of type int and unit=[\'sec\',\'min\',\'hrs\',\'day\']')
    exit(-1)

#try to get the database argument
filename = '/addressbook.db'
try:
    database = args.database[0] + filename
except:
    database = os.path.dirname(os.path.realpath(__file__))+filename
print('database: ', database)
main = app(database, interval, debug)
main.run()
