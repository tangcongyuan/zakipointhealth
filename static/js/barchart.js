function generateBarChart(data, margin, width, height){
  var x = d3.scale.ordinal().rangeRoundBands([0, width], .5);
  var y = d3.scale.linear().range([height, 0]);

  var xAxis = d3.svg.axis()
                .scale(x)
                .orient("bottom");

  var yAxis = d3.svg.axis()
                .scale(y)
                .orient("left")
                .ticks(10);

  var svg = d3.select("body").append("svg")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.top + margin.bottom)
              .append("g")
              .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  $.each(data, function(i, item) {
    item.date = +item._id;
    item.value = +item.count;
  });

  x.domain(data.map(function(d) { return d.date; }).sort());
  y.domain([0, d3.max(data, function(d) { return d.value; })]);

  svg.append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")")
  .call(xAxis)
  .selectAll("text")
  .style("text-anchor", "end")
  .attr("dx", ".5em")

  var bar = svg.selectAll("bar")
         .data(data)
         .enter()

  bar.append("rect")
     .style("fill", "steelblue")
     .attr("x", function(d) { return x(d.date); })
     .attr("width", x.rangeBand())
     .attr("y", function(d) { return y(d.value); })
     .attr("height", function(d) { return height - y(d.value); });

  bar.append("text")
     .attr("x", function(d, i) { return 1.5*x.rangeBand()+x.rangeBand()*2*i;})
     .attr("y", 0)
     .attr("dx", "-.7em")
     .attr("dy", "-.3em")
     .text(function(d) { return d.value; });

  svg.append("text")
     .text("Total Population")
     .attr("x", width/2)
     .attr("y", 0)
     .attr("dx", "-3.5em")
     .attr("dy", "-2em");
}