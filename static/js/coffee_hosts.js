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
