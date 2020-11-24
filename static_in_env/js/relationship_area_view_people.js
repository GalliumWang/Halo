function show() {

    'use strict';

    // Generic setup
    var margin = { top: 20, bottom: 20, right: 20, left: 20 },
        width = 1600 - margin.left - margin.right,
        height = 900 - margin.top - margin.bottom;

    var chart = d3.select(".chart")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + ","
            + margin.top + ")");

    var div = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("display", "none")
        .style("opacity", "1");


    d3.text('/static/csv/relationship_area_view_people.csv', function (raw) {
        var data = d3.dsvFormat("\t").parse(raw)

        // convert population and arrea to a number
        data = data.map(function (el) {
            el.rate = +el.rate;
            el.rate1 = +el.rate1;
            el.rate2 = el.rate2;

            if (el.Density === Infinity) el.Density = 0;
            return el;
        });

        // group entries using nest and create hierarchy per continent
        var entries = d3.nest()
            .key(function (d) { return d.layer; })
            .entries(data);

        // setup the tree generator
        var tree = d3.treemap()
            .size([width, height])
            .padding(2)
            .tile(d3.treemapSquarify.ratio(1))
        // we can change how the treemap is rendered
        // .tile(d3.treemapSquarify.ratio(3));
        // .tile(d3.treemapSquarify.ratio(1));
        // .tile(d3.treemapResquarify);

        // create a colorScale which maps the continent
        // name to a color from the specified interpolator
        var colorScale = d3.scaleOrdinal()
            .domain(entries.map(function (el) { return el.key }))
            .range(d3.range(0, entries.length + 1)
                .map(function (i) { return d3.interpolateWarm(i / entries.length); }))

        // use the color scale to add a legend
        var legend = chart.append("g")
            .attr("class", "legend")
            .attr("transform", "translate(0 " + height + ")")


        legend.selectAll("rect")
            .data(colorScale.domain())
            .enter()
            .append("rect")
            .attr("x", function (d, i) { return i * 100 })
            .attr("fill", colorScale)
            .attr("width", 100)
            .attr("height", 20)

        legend.selectAll("text")
            .data(colorScale.domain())
            .enter()
            .append("text")
            .attr("x", function (d, i) { return i * 100 })
            .attr("dy", 15)
            .attr("dx", 2)
            .text(function (d) { return d })


        // generate a population oriented tree.
        var properties = ['rate', 'rate1', 'rate2'];

        // trigger the first property
        //onclick();
        onclick_gcn1();

        function update(property) {

            var root = d3.hierarchy({ values: entries }, function (d) { return d.values; })
                .sum(function (data) { return data[property]; })
                .sort(function (a, b) { return b.value - a.value; });

            // convert it to a tree
            tree(root);

            var properties_to_display_name = { "rate": "GCN1", "rate1": "GCN2", "rate2": "GCN3" }

            // add a header
            var header = d3.select("h1").text(properties_to_display_name[properties[2]]);

            // we only print out the leaves, leaves are the nodes
            // without children.
            // Object consistency: https://bost.ocks.org/mike/constancy/
            var groups = chart.selectAll(".node").data(root.leaves(), function (d) { return d.data['name'] })

            // for the newgroups we add a g, and set some behavior.
            var newGroups = groups
                .enter()
                .append("g")
                .attr("class", "node")
                .on("mouseover", mouseover)
                .on("mousemove", mousemove)
                .on("mouseout", mouseout)
                .on("click", onclick);

            var button1 = document.getElementById("btn1").onclick = onclick_gcn1;
            var button1 = document.getElementById("btn2").onclick = onclick_gcn2;
            var button1 = document.getElementById("btn3").onclick = onclick_gcn3;




            // for the newgroups we also add a rectangle, which is filled.
            // with the color of the continent, and has a simple black border.
            newGroups.append("rect")
                .style("fill", function (d) { return colorScale(d.parent.data.key) })
                .style("stroke", "black")
                .attr("width", function (d, i) { return d.x1 - d.x0 })
                .attr("height", function (d, i) { return d.y1 - d.y0 });

            // and we append the foreignObject, with a nested body for the text
            newGroups.append("foreignObject")
                .append("xhtml:body")
                .style("margin-left", 0)
                .style("background", "rgba(0, 0, 0, 0)");

            // we position the new and updated groups based on the calculated d.x0 and d.y0
            var allGroups = groups.merge(newGroups)
            //var allGroups = newGroups
            //var allGroups = groups

            allGroups.transition().duration(2000)
                .attr("transform", function (d) { return "translate(" + d.x0 + " " + d.y0 + ")" })

            // When we update it could mean changing the size of the rectangle
            allGroups.select("rect")
                .transition().duration(2000)
                .attr("width", function (d, i) { return d.x1 - d.x0 })
                .attr("height", function (d, i) { return d.y1 - d.y0 })

            // When updating we should change the size of the foreign object
            allGroups.select("foreignObject")
                .transition().duration(2000)
                .attr("width", function (d) { return d.x1 - d.x0 })
                .attr("height", function (d) { return d.y1 - d.y0 })

            allGroups.select("foreignObject").select("body")
                .style("margin-left", 0)
                .transition().duration(2000)
                .tween("custom", function (d, i) {

                    // need to get the current height. We get this from the element
                    // itself, since the bound data can be changed.
                    var oldHeight = 0;

                    // this can be undefined for the first run
                    var currentDiv = d3.select(this).select("div").node();
                    if (currentDiv) {
                        var height = currentDiv.getAttribute("data-height");
                        oldHeight = height ? height : 0;
                    }

                    // calculate the new height and setup a interpolator
                    var newHeight = (d.y1 - d.y0);
                    var interpolator = d3.interpolateNumber(oldHeight, newHeight);

                    // assign to variable, so we can access it in the custom tween
                    var node = this;
                    return function (t) {
                        d3.select(node).html(function (d) {
                            var newHeight = interpolator(t);
                            return '<div data-height="' + newHeight + '"  style="height: ' + newHeight + '" class="node-name"><p style="font-size:20px;">' + d.data['name'].split(" ")[0] + '</p></div>'
                        })
                    }
                });
        }

        // simple listeners which show an overlay div at an absolute location


        function onclick(d) {
            // var currentProp = properties.shift();
            // properties.push(currentProp);
            // update(currentProp);
            window.open(d.data["url"], "_blank");
            mouseout()

        }

        function onclick_gcn1() {
            var currentProp = "rate";
            update(currentProp);
        }

        function onclick_gcn2() {
            var currentProp = "rate1";
            update(currentProp);
        }

        function onclick_gcn3() {
            var currentProp = "rate2";
            update(currentProp);
        }

        function mouseover(d) {
            div.style("display", "inline");
            div.html("<ul>" +
                "<li><strong>Name:</strong> " + d.data['name'] + " </li>" +
                "<li><strong>GCN1:</strong> " + d.data['rate'] + " </li>" +
                "<li><strong>GCN2:</strong> " + d.data['rate1'] + " </li>" +
                "<li><strong>GCN3:</strong> " + d.data['rate2'] + " </li>" +
                "</ul>" + "<img width=\"200px\" referrerpolicy=\"no-referrer\" src=\"" + d.data['img_url'] + "\">")
        }

        function mousemove(d) {
            div
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY + 20) + "px");
        }


        function mouseout() {
            //div.style("display", "inline");
            div.style("display", "none");
        }
    });
}

