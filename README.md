<h1>wifi access point logger</h1>
<h2>by fefe33</h2>
<hr>
<h2>what does it do?</h2>
<p>includes 2 apps:</p>
<ol>
  <li><p>logserver.py (the app that logs the access points and other scan-related metadata to the database)</p></li>
  <li><p>statserver.py (the app that serves the web interface for viewing and tracking access points)</p></li>
</ol>
<p>the statistics server lets you view all access points discovered by the logger application, as well as see a chart over time of the signal strength history of each access point at the time of each scan.</p>

<h2>requirements:</h2>
<p>nmcli, python3, flask</p>
<p>this app was initially tested on a raspberry pi 4 (raspbian 32 bit to be precise), but should work on any PC with a functional wifi adapater running a linux distro that has nmcli installed and python support</p>
<h2>how to use</h2>
<h3>to use the logger:</h3>
<ul>
  <li><p>run python3 logserver.py -i/--interval [number] [unit] -d/--database [path/to/db/parentdir] </p></li>
</ul>
<h3>to use the server:</h3>
<ul>
  <li><p>run python3 statserver.py -db/--database [path/to/db/parentdir] --addr [host] [port] </p></li>
</ul>
<p>the program always uses a database called 'addressbook.db'. dont try to specifify the name of the database. it wont work and will default to a database in the adjacent 'databases' directory</p>
