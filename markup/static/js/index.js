//this program continually requests data from the server writes it as rows to the table
let main = ()=> {
	//this writes a single row to the HTMLdocument
	let writeRow = (bssid, ssid, mode, channel, timestamp)=>{
		row = document.createElement('tr')
		//arrays for cells and td
		td = []
		h2 = []
		//push the elements onto the arrays
		for (i=0;i<5;i++) {
			cell = document.createElement('td')
			cell.classList.add('styleCell')
			text = document.createElement('h2')
			h2.push(text)
			td.push(cell)
		}
		//add the text to the h2s
		h2[0].innerText = bssid
		h2[1].innerText = ssid
		h2[2].innerText = mode
		h2[3].innerText = channel
		h2[4].innerText = timestamp
		//append each h2 to each cell then append to the the body
		tbody = document.querySelector('#append_rows')
		for (i=0;i<5;i++) {
			td[i].appendChild(h2[i])
			row.appendChild(td[i])
		}
		tbody.appendChild(row)
	}
	//this fetches the data from the endpoint
	let getDevices = async ()=>{
		res = await fetch('/log/ap', {method:'POST', headers: {'Content-Type':'appication/json'}})
		return await res.json()
	}
	//this clears the table of all rows
	let clearTable = ()=> {
		tbody = document.querySelector('#append_rows')
		tbody.innerHTML = ''
	}
	//function to request deviced, clear old table rows, and write new ones
	let refreshTable = async ()=> {
		//requests the data
		devices = await getDevices()
		//clear the table
		clearTable()
		//quick function to convert utc seconds to datetime value
		let UTCtoASCII = (t)=>{
			d = new Date(0), o = ''
			d.setUTCSeconds(t)
			d = d.toString()
			d = d.split(' ')
			//concatinate the first 5 elements of the array with spaces
			for (i=0;i<5;i++) {
				o = o + d[i] + ' '
			}
			return o
		}

		//iter through each, writing the appropriate values to the table 		
		for (i of devices['devices']) {
			writeRow(i[0],i[1],i[2],i[3],UTCtoASCII(i[4]))
		}
		console.log('values refreshed')
	}

	//this refreshes the table every <defaultRate> seconds
	return {'refresh':refreshTable}
	
}

function run() {
	let m = main()
	//call once then set the interval (default set in main argument)
	m['refresh']()
	let z = setInterval(m['refresh'], parseInt(document.querySelector('#append_rows').getAttribute('data-defaultRate'))*1000)
}
run()

// add the button listener
document.querySelector('button').onclick = ()=>{
	window.location = '/signal'
}
