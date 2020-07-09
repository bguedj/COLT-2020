const start = () => {
	const urlFilter = getUrlParameter("break") || '';

	if (urlFilter === '') return 0;

	let found = '';
	d3.json('serve_coffee_hosts.json').then(data => {
		for (d of data) {
			if (d['UID'] === urlFilter) {
				found = d;
				break;
			}
		}
		if (found !== '') {
			d3.select("#break-id").text(" " + urlFilter);
			for (i = 0; i < 4; i++) {
				if (found["Hosts: Coffee Room " + i] !== "") {
					d3.select("#host-" + i).text(" Hosted by " + found["Hosts: Coffee Room " + i] + ".");		
				}
			}
			if (found["GRAD Student Coffee Room"] !== "") {
				d3.select("#host-5").text(" Hosted by " + found["GRAD Student Coffee Room"] + ".");	
			}
		}

	})

	if (urlFilter === "1C" || urlFilter === "2C") {
		d3.select("#baidu").style("visibility", "visible");
	}
	
}

const startshuff = () => {
	const urlFilter = getUrlParameter("break") || '';

	if (urlFilter === "1C" || urlFilter === "2C") {
		d3.select("#baidu").style("visibility", "visible");
	}
	
	d3.json('serve_zoom.json').then(data => {
		const coffees = data['coffees'];
		let names_links = [['Latte', coffees[0]], ['Macchiato', coffees[1]], ['Cortado', coffees[2]], ['Mocha', coffees[3]]];
		shuffleArray(names_links);
		for (i = 0; i < 4; i++) {
			d3.select("#room" + i).html('<a href="' + names_links[i][1] + '" target="_blank">"' + names_links[i][0] + '"</a>');
		}
	})
}

/* Randomize array in-place using Durstenfeld shuffle algorithm */
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        const temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}


