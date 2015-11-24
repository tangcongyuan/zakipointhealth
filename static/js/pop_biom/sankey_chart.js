function generateSankeyChart(loc, data, layout, color, title) {
  var units = "People";
  var margin = layout.margin,
      width = layout.width,
      height = layout.height;

  var formatNumber = d3.format(",.0f"),    // zero decimal places
      format = function(d) { return formatNumber(d) + " " + units; },
      color = d3.scale.ordinal().range(color);

  // append the svg canvas to the page
  var svg = d3.select(loc).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Set the sankey diagram properties
  var sankey = d3.sankey()
      .nodeWidth(30)
      .nodePadding(45)
      .size([width, height]);

  var path = sankey.link();

  var graph = {"nodes" : [], "links" : []};
  var years = new Set();

  $.each(data, function (i, d) {
    graph.nodes.push({ "name": d.SourceYear + ' ' + d.Source });
    graph.nodes.push({ "name": d.TargetYear + ' ' + d.Target });
    graph.links.push({ "source": d.SourceYear + ' ' + d.Source,
                     "target": d.TargetYear + ' ' + d.Target,
                     "value": +d.Count });
    years.add(d.SourceYear);
    years.add(d.TargetYear);
  });

  graph.nodes = graph.nodes.sort(function(a, b) { 
      if (a.name.slice(0,5) > b.name.slice(0,5)) return -1;
      if (a.name.slice(0,5) < b.name.slice(0,5)) return 1;
      if (a.name.slice(5,6) == 'H') return -1;
      if (a.name.slice(5,6) == 'L') return 1;
      if (a.name.slice(5,6) == 'M' && b.name.slice(5,6) == 'H') return 1;
      if (a.name.slice(5,6) == 'M' && b.name.slice(5,6) == 'L') return -1;
      return 0;
  });

  // return only the distinct / unique nodes
  graph.nodes = d3.keys(d3.nest()
    .key(function (d) { return d.name; })
    .map(graph.nodes));


  // loop through each link replacing the text with its index from node
  graph.links.forEach(function (d, i) {
    graph.links[i].source = graph.nodes.indexOf(graph.links[i].source);
    graph.links[i].target = graph.nodes.indexOf(graph.links[i].target);
  });

  //now loop through each nodes to make nodes an array of objects
  // rather than an array of strings
  graph.nodes.forEach(function (d, i) {
    graph.nodes[i] = { "name": d };
  }); 

  sankey
    .nodes(graph.nodes)
    .links(graph.links)
    .layout(32);

  // add in the links
  var link = svg.append("g").selectAll(".link")
    .data(graph.links)
    .enter().append("path")
    .attr("class", "link")
    .attr("d", path)
    .style("stroke-width", function(d) { return Math.max(1, d.dy); })
    .sort(function(a, b) { return b.dy - a.dy; });

  // add the link titles
  link.append("title")
    .text(function(d) { return d.source.name + " → " + d.target.name + "\n" + format(d.value); });

  // add in the nodes
  var node = svg.append("g").selectAll(".node")
    .data(graph.nodes)
    .enter().append("g")
    .attr("class", "node")
    .attr("transform", function(d) { 
    return "translate(" + d.x + "," + d.y + ")"; })
    .call(d3.behavior.drag()
    .origin(function(d) { return d; })
    .on("dragstart", function() { 
    this.parentNode.appendChild(this); })
    .on("drag", dragmove));     

  // add the rectangles for the nodes
  node.append("rect")
    .attr("height", function(d) { return d.dy; })
    .attr("width", sankey.nodeWidth())
    //.style("fill", function(d) { return d.color = color(d.name.replace(/ .*/, "")); })
    .style("fill", function(d, i) { return d.color = color(i%3); })
    .style("opacity", 0.9)
    .style("stroke", function(d) { return d3.rgb(d.color).darker(2); })
    .append("title")
    .text(function(d) { 
    return d.name + "\n" + format(d.value); }); 

  // add in the title for the nodes
  node.append("text")
    //.attr("x", -6)
    .attr("y", function(d) { return d.dy / 2; })
    //.attr("dx", "1em")
    .attr("dy", ".35em")
    .attr("text-anchor", "end")
    .attr("transform", null)
    .text(function(d) { return d.name.slice(4); })
    //.filter(function(d) { return d.x < width / 2; })
    .attr("x", 5+sankey.nodeWidth())
    .style("font-size", ".7em")
    .attr("text-anchor", "start");

  years = Array.from(years);

  svg.selectAll(".text")
    .data(years)
    .enter().append("text")
    .attr("x", function(d, i) { return (1.2*i)*(width/(years.length));})
    .attr("y", 50-margin.top)
    .attr("dx", ".1em")
    .style("font-size","0.8em")
    .text(function(d) { return d; });

  svg.selectAll(".text")
    .data(years)
    .enter().append("text")
    .attr("x", width/2)
    .attr("y", 20-margin.top)
    .attr("dx", "-6em")
    .style("font-size","0.9em")
    .text(title);

  // the function for moving the nodes
function dragmove(d) {
    d3.select(this).attr("transform", 
        "translate(" + d.x + "," + (
              d.y = Math.max(0, Math.min(height - d.dy, d3.event.y))
          ) + ")");
    sankey.relayout();
    link.attr("d", path);
  }
}