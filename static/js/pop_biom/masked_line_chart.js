function generateMaskedLineChart(loc, data, layout, color, title) {
  var margin = layout.margin,
      width = layout.width,
      height = layout.height;

  var parseDate = d3.time.format("%Y").parse;

  var x = d3.time.scale()
      .range([0, width]);

  var y = d3.scale.linear()
      .range([height-50, 0]); // leave 50 displaying the title

  var color = d3.scale.ordinal().range(color);

  var xAxis = d3.svg.axis()
      .scale(x)
      .ticks(d3.time.year, 1) // step by 1 year
      .orient("bottom");

  var line = d3.svg.line()
      .x(function(d) { return x(+d.Year); })
      .y(function(d) { return y(d.count); });

  var svg = d3.select(loc).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  color.domain(d3.keys(data[0]).filter(function(key) { return key !== "Year"; }));

  $.each(data, function(i, d) {
    d.Year = parseDate(d.Year);
  });

  var risks = color.domain().map(function(name) {
    return {
      name: name,
      counts: data.map(function(d) {
        return {Year: d.Year, count: +d[name]};
      })
    };
  });

  $.each(risks, function(i, d){
    d.counts = d.counts.sort(function(a, b) { 
      if (a.Year > b.Year) return 1;
      if (a.Year < b.Year) return -1;
      return 0;
    });
  });

  x.domain(d3.extent(data, function(d) { return +d.Year; }));

  y.domain([
    d3.min(risks, function(c) { return d3.min(c.counts, function(v) { return v.count; }); }),
    d3.max(risks, function(c) { return d3.max(c.counts, function(v) { return v.count; }); })
  ]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  var risk = svg.selectAll(".risk")
      .data(risks)
    .enter().append("g")
      .attr("class", "risk");

  risk.append("path")
      .attr("class", "line")
      .attr("d", function(d) { return line(d.counts); })
      .style("stroke", function(d) { return color(d.name); });

  risk.append("text")
      .datum(function(d) { return {name: d.name, value: d.counts[d.counts.length - 1]}; })
      .attr("transform", function(d) { return "translate(" + x(+d.value.Year) + "," + y(d.value.count) + ")"; })
      .attr("x", 3)
      .attr("dx", "2.5em")
      .attr("dy", ".35em")
      .attr("fill", function(d) { return color(d.name); })
      .text(function(d) { return d.name; });

  for (var ind = risks[0].counts.length - 1; ind >= 0; ind--) {

    risk.append("rect")
      .datum(function(d) { return {name: d.name, value: d.counts[ind]}; })
      .attr("transform", function(d) { return "translate(" + x(+d.value.Year) + "," + y(d.value.count) + ")"; })
      .attr("x", -20)
      .attr("y", -8)
      .attr("width", 40) // magic number for masking some of the line
      .attr("height", 16) // again, magic number
      .style("opacity", 1)
      .style("fill", "white"); // white, or whatever the background color is

    risk.append("text")
      .datum(function(d) { return {name: d.name, value: d.counts[ind]}; })
      .attr("transform", function(d) { return "translate(" + x(+d.value.Year) + "," + y(d.value.count) + ")"; })
      .attr("x", 3)
      .attr("dx", "-1em")
      .attr("dy", "0em")
      .attr("fill", function(d) { return color(d.name); })
      .text(function(d) { return d.value.count+'%'; });
  };

  svg.append("text")
      .text(title)
      .attr("x", width/2)
      .attr("y", 0)
      .style("font-size", "1.9em")
      .attr("dx", "-2.5em")
      .attr("dy", "-2em");
}