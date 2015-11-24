function generateOverlappedBarChart(loc, participated, data, layout, title) {
  var margin = layout.margin,
      width = layout.width,
      height = layout.height;

  var x = d3.scale.ordinal().rangeRoundBands([0, width], .5);
  var y = d3.scale.linear().range([height, 0]);

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")
      .ticks(10);

  var svg = d3.select(loc).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", 
            "translate(" + margin.left + "," + margin.top + ")");

  $.each(participated, function(i, item) {
    item.date = +item._id;
    item.value = +item.count;
    item.rate = Math.floor((item.count/data[i].count) * 100);
  });

  x.domain(data.map(function(d) { return d.date; }).sort());
  y.domain([0, d3.max(data, function(d) { return d.value; })]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", ".6em")

  var bar = svg.selectAll("bar")
      .data(data)
      .enter()

   bar.append("rect")
      .style("fill", "grey")
      .style("opacity", 0.1)
      .attr("x", function(d) { return x(d.date); })
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.value); })
      .attr("height", function(d) { return height - y(d.value); });

   svg.append("text")
      .text(title)
      .attr("x", width/2)
      .attr("y", 0)
      .attr("dx", "-4em")
      .attr("dy", "-2em");

   x.domain(participated.map(function(d) { return d.date; }).sort());

   participated = participated.sort(function(a, b){
    if (a._id > b._id) return 1;
    if (a._id < b._id) return -1;
    return 0;
   });

   svg.selectAll("bar")
      .data(participated)
      .enter().append("rect")
      .style("fill", "steelblue")
      .style("opacity", 0.9)
      .attr("x", function(d) { return x(d.date); })
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.value); })
      .attr("height", function(d) { return height - y(d.value); });

   svg.selectAll("bar")
      .data(participated)
      .enter().append("text")
      .attr("x", function(d, i) { return 1.5*x.rangeBand()+x.rangeBand()*2*i;})
      .attr("y", 0)
      .attr("dx", "-1em")
      .attr("dy", "-.3em")
      .text(function(d) { return d.rate+'%'; });
}