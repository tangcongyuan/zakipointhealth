function generateStackedBarChart(loc, data, layout, color){
  // data is in JSON format
  var margin = layout.margin,
       width = layout.width,
      height = layout.height;
      
  var color = d3.scale.ordinal().range(color);

  var x = d3.scale.ordinal()
      .rangeRoundBands([0, width], .5);

  var y = d3.scale.linear()
      .rangeRound([height, 0]);

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom");

  var svg = d3.select(loc).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  //color.domain(d3.keys(data[0]).filter(function(key) { return key !== "Year"; }));
  if (data[0].between) {
      color.domain(["under_500", "between", "over_10k"]);
  }
  if (data[0]['$500-$10K']) {
      color.domain(["Under $500", "$500-$10K", "Over $10K"]);
  }
  if (data[0].outofNormal) {
      color.domain(["normal", "outofNormal", "critical"]);
  }

  $.each(data, function(i, d) {
    var y0 = 0;
    d.claims = color.domain().map(function(level) { return {level: level, y0: y0, y1: y0 += +d[level]}; });
    d.total = d.claims[d.claims.length - 1].y1;
    d.Year = d.Year.slice(2,4);
  });

  data = data.sort(function(a, b) { 
    if (a.Year > b.Year) return 1;
    if (a.Year < b.Year) return -1;
    return 0;
  });

  x.domain(data.map(function(d) { return d.Year; }));
  y.domain([0, d3.max(data, function(d) { return d.total; })]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  var claims = svg.selectAll("claims")
      .data(data)
      .enter().append("g")
      .attr("class", "g")
      .attr("transform", function(d) { return "translate(" + x(d.Year) + ",0)"; });

  claims.selectAll("rect")
      .data(function(d) { return d.claims; })
    .enter().append("rect")
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.y1); })
      .attr("height", function(d) { return y(d.y0) - y(d.y1); })
      .style("opacity", 0.9)
      .style("fill", function(d) { return color(d.level); });

  svg.selectAll("claims")
      .data(data)
      .enter().append("text")
      .attr("x", function(d, i) { return 1.5*x.rangeBand()+x.rangeBand()*2*i;})
      .attr("y", function(d, i) { return 20-margin.top; })
      .attr("fill", function(d) { if (d.over_10k) { return color("over_10k"); }
                                  if (d["Over $10K"]) { return color("Over $10K"); }
                                  if (d.critical) { return color("critical"); }
                                })
      .attr("dx", "-0.9em")
      .attr("dy", "0em")
      .text(function(d) { if (d.over_10k) { return d.over_10k+'%'; }
                          if (d["Over $10K"]) { return d["Over $10K"]+'%'; }
                          if (d.critical) { return d.critical+'%'; }
                        });

  svg.selectAll("claims")
      .data(data)
      .enter().append("text")
      .attr("x", function(d, i) { return 1.5*x.rangeBand()+x.rangeBand()*2*i;})
      .attr("y", function(d, i) { return 40-margin.top; })
      .attr("fill", function(d) { if (d.between) { return color("between"); }
                                  if (d["$500-$10K"]) { return color("$500-$10K"); }
                                  if (d.outofNormal) { return color("outofNormal"); }
                                })
      .attr("dx", "-0.9em")
      .attr("dy", "0em")
      .text(function(d) { if (d.between) { return d.between+'%'; }
                          if (d["$500-$10K"]) { return d["$500-$10K"]+'%'; }
                          if (d.outofNormal) { return d.outofNormal+'%'; }
                        });

  svg.selectAll("claims")
      .data(data)
      .enter().append("text")
      .attr("x", function(d, i) { return 1.5*x.rangeBand()+x.rangeBand()*2*i;})
      .attr("y", function(d, i) { return 60-margin.top; })
      .attr("fill", function(d) { if (d.under_500) { return color("under_500"); }
                                  if (d["Under $500"]) { return color("Under $500"); }
                                })
      .attr("dx", "-0.9em")
      .attr("dy", "0em")
      .text(function(d) { if (d.under_500) { return d.under_500+'%'; }
                          if (d["Under $500"]) { return d["Under $500"]+'%'; }
                        });

  if (data[0]['$500-$10K']) {
    var legend = svg.selectAll(".legend")
                    .data(color.domain().slice().reverse())
                    .enter().append("g")
                    .attr("class", "legend")
                    .attr("transform", function(d, i) { return "translate(20," + i * 20 + ")"; });

        legend.append("text")
            .attr("x", width+80)
            .attr("y", -50)
            .attr("dy", "0em")
            .style("text-anchor", "end")
            .style("fill", color)
            .text(function(d) { return 'claims ' + d; });

        svg.selectAll("claims")
            .data(data)
            .enter().append("text")
            .attr("x", function(d, i) { return 1.5*x.rangeBand()+x.rangeBand()*2*i;})
            .attr("y", function(d, i) { return 20-margin.top; })
            .attr("fill", "#F78181")
            .attr("dx", "-0.9em")
            .attr("dy", "0em")
            .text(function(d) { return d["Over $10K"]+'%'; });

        svg.selectAll("claims")
            .data(data)
            .enter().append("text")
            .attr("x", function(d, i) { return 1.5*x.rangeBand()+x.rangeBand()*2*i;})
            .attr("y", function(d, i) { return 40-margin.top; })
            .attr("fill", "#BDBDBD")
            .attr("dx", "-0.9em")
            .attr("dy", "0em")
            .text(function(d) { return d["$500-$10K"]+'%'; });

        svg.selectAll("claims")
            .data(data)
            .enter().append("text")
            .attr("x", function(d, i) { return 1.5*x.rangeBand()+x.rangeBand()*2*i;})
            .attr("y", function(d, i) { return 60-margin.top; })
            .attr("fill", "steelblue")
            .attr("dx", "-0.9em")
            .attr("dy", "0em")
            .text(function(d) { return d["Under $500"]+'%'; });
  }
}