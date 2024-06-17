//written by fefe33
//wifi signal tracker chart

ChartManager = ()=>{
	//select the canvas element
	const ctx = document.getElementById('container');
	const colors = ['pink', 'lightred','red', 'darkred', 'lightgreen', 'green', 'darkgreen', 'lightyellow', 'yellow','darkyellow', 'lightorange', 'orange', 'darkorange', 'lightblue','blue', 'darkblue', 'purple','cyan', 'black', 'grey']
	//this function reads through an array of 2 element arrays (x, y). 
	//loop through an array of arrays, if a non-sequential x value is detected, insert x the correct x value and make its y value 0. continue algorithm from current position + 1
	let fillTheBlank = (a)=>{
		//start at position 1
		for (i=1;i<a.length;i++){
			console.log(a[i], a[i-1])
			//if the x value at a[i] is not 1 more than a[i-1]
			if (a[i][1] !== a[i-1][1]+1) {
				//get the difference
				dif = a[i][1] - a[i-1][1]
				//get the valu of a[i-1][1], saving it to s
				s = a[i-1][1]+1
				//get the current value of i-1
				//insert array [s, 0], <dif> times, incrementing s with each insertion
				console.log('difference: ', dif)
				if (dif>1) {
					for (j=0;j<dif-1;j++) {
						a.splice(i, 0, [0, s])
						s++;
						i++;
					}
				} else {
					a.splice(i, 0, [0,s])
					i++
				}
			}
		}
		return a
	}
	
	let getColor = (n)=>{return colors[n % colors.length]}
	//function to retrieve and parse the signal data 
	let buildChart = async ()=>{
	
		ds = await fetch('/log/sig', {method:'POST'}).then(async (r)=>{return await r.json()})
		cnt = 0
		datasets = []
		for (ii of ds.bssids) {
			let v = []
			//plug each ds.bssid value in as key in ds.dataset. iter through each resulting array saving valyes to array v
			for (j of ds.dataset[ii].data) {	
				v.push(j)	
			}
			//if the dataset doesnt start at 0,append zeroes to the begining of the values array ds.dataset[i]['discovered_at'] times
			if (ds.dataset[ii].discoveredAt!==0) {
				for (j=0;j<ds.dataset[ii].discoveredAt;j++) {
					v.unshift([0, j])
				}
			}
			// if the dataset doesnt match the total scan length assure the set of values isnt missing any values intermittently
			if (v.length !== ds.total_scans) {
				fillTheBlank(v)
				console.log('post alg: ', v)
				//make v only its y values
			} 
			nv = []
			for (j of v) {
				nv.push(j[0])
			}
			datasets.push(makeDataSet(ii, nv, getColor(cnt)))
			
			cnt++
		}
		console.log(datasets)
		//build the chart and return its reference object
		//convert labels to dateTime format
		labels = []
		for (i of ds.labels) {
			d = new Date(0)
			d.setUTCSeconds(i)
			d = d.toString().split(' ')
			d = `${d[1]} ${d[2]} ${d[3]} ${d[4]}`
			labels.push(d)
		}

		return makeChart(labels, datasets)
	}
	//create a new dataset.
		//the label here is for the line of the dataset
		//data arg is an array of numerical values
		//the color is the color of the line representing that dataset

	let makeDataSet = (label, data, color)=> {
		return {
			label:label,
			borderColor:color,
			data:data,
			borderWidth:1,
		}
	}
	//xLabels are labels along x axis. updates 
	let makeChart = (xLabels, datasets)=> { 
		return new Chart(ctx, {
			type: 'line',
			data: {
			labels: xLabels,
			//datasets
			datasets: datasets
			},
			options: {
			scales: {
				y: {
				beginAtZero: true,
				}
			}
			}
		});
	}
	//appends 1 label to x axis and adds 1 value to each existing dataset, interpreting null values as zero
	//takes xLabel and object as args

	//the object keys should reference the predefined dataset name with the new value to append as the value. values not inluded will be set to zero
	let appendToChart = (chart, xLabel, obj)=> {
		//get the xLabel and push it to the x axis
		chart.data.labels.push(xLabel)
		for (i of chart.data.datasets) {
			//valid keys in the input object are defined by valid dataset labels in the chart.data.datasets array.	 
			//values of matching keys are pushed into array of values of appropriate dataset. labels that dont exist as keys in the input object append zero
			if (Object.keys(obj).includes(i.label)){
				i.data.push(obj[i.label])
			} else {
				i.data.push(0)
			}
		}
		chart.update()
		

	}	

	return {'makeChart': makeChart, 'makeDataSet':makeDataSet, 'appendToChart':appendToChart, 'renderChart':buildChart, 'fillTheBlank': fillTheBlank}
}
let run = ()=> {
	cm = ChartManager()
	chart = cm.renderChart()
	return {'manager':cm, 'chart': chart}
}
app = run()
