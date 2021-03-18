$( document ).ready(function() {
    var width = 900;
    var height = 500;

    var prevCity = "New York";
    var prevTemp = 3000;

    var svg = d3.select("#map")
    .append("svg")
    .attr("width", width)
    .attr("height", height);
    
    var body = d3.select("body")
    
    var div = d3.select("body")
		    .append("div")   
    		.attr("class", "tooltip")               
    		.style("opacity", 0);

    var projection = d3.geo.albersUsa()
		.translate([width/2, height/2])    // translate to center of screen
		.scale([1000]);

    var path = d3.geo.path().projection(projection);

    var mapGroup = svg.append("g");
    var circleGroup = svg.append("g");

    d3.json("Data/us.json",function(us){
        mapGroup
        .selectAll("path")
        .data(topojson.feature(us, us.objects.states).features)
        .enter()
        .append("path")
        .attr("d", path)
        .style("stroke", "#000")
	    .style("stroke-width", "1")
        .attr("fill","white");
    });
    
    // We're ready, draws inital cirlle with base values

    //drawCircle({v:[1,1]},svg);
    setText({"city":["Boston"],"prcp":0,"temp":20,"year":2010,"season":"fall","color":[[255,100,255]]})
    // Loop
	var interval = function() {
    	setTimeout(function() {
        
        // AJAX call that gets data from the provided url (port 3000 for us)
        $.ajax({
        	url: "http://localhost:3000/",
        	cache: false,
        	data: "",

        }).done(function(data) {
            // updates the circle with the current data
            //drawCircle(data,svg);
            setText(data);
            interval();
        });
    	}, 100// Interval time
    );
	};

	interval();

    function setText(data){
        d3.select("#city").transition().duration(2000).text(data.city);
        document.getElementById("year").innerHTML = data.year;
        document.getElementById("season").innerHTML = data.season;
        document.getElementById("temp").innerHTML = data.temp;
        document.getElementById("prcp").innerHTML = data.prcp;
        
        if(prevTemp != data.temp[0]){
            body.transition()
            .duration(1000)
            .style("background-color", d3.rgb(data.color[0][0],data.color[0][1],data.color[0][1]));
        }
        

        if(prevCity != data.city[0]){
            console.log("Drawing New Circles")
            drawCircle(data.city[0]);
        }

        prevTemp = data.temp[0];
        prevCity = data.city[0];
    
    }

    function drawCircle(city){
        d3.csv("Data/stations.csv", function(stations){
            circleGroup.selectAll("circle")
                .data(stations)
                .enter()
                .append("circle")
                .attr("class","aCircle")
                .attr("cx", function(d) {
                    return projection([d.lon, d.lat])[0];
                })
                .attr("cy", function(d) {
                    return projection([d.lon, d.lat])[1];
                })
                .attr("r", 8)
                .attr("fill",function(d){
                    if(d.CommonName == city){
                        console.log(d.CommonName)
                        return "red"
                    }else{
                        return "grey"
                    }
                })
                .on("mouseover", function(d) {      
                    div.transition()        
                         .duration(200)      
                       .style("opacity", .9);      
                       div.text(d.CommonName)
                       .style("left", (d3.event.pageX) + "px")     
                       .style("top", (d3.event.pageY - 28) + "px");    
                })   
            
                // fade out tooltip on mouse out               
                .on("mouseout", function(d) {       
                    div.transition()        
                       .duration(500)      
                       .style("opacity", 0);   
                });

                circleGroup.selectAll("circle").transition().duration(500).attr("fill",function(d){
                    if(d.CommonName == city){
                        console.log(d.CommonName)
                        return "red"
                    }else{
                        return "grey"
                    }
                });
            });


    }
});	



// Draws and updates circle
