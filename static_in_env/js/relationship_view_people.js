function show() {

    'use strict';

    // Generic setup
    var margin = { top: 20, bottom: 20, right: 120, left: 120 },
        width = 1535 - margin.left - margin.right,
        height = 1000 - margin.top - margin.bottom;

    var chart = d3.select(".chart")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + (width / 2 + 100) + "," + height / 2 + ")")
        .attr("class", "rotated");

    // generic functions
    var tree = d3.tree()
        .size([360, 400])
        .separation(function (a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

    var stratify = d3.stratify();
    var colorScale = d3.scaleSequential(d3.interpolateSpectral).domain([0, 12]);

    var root;        // initial set of loaded data
    var currentRoot; // the currentData being shown

    // load the data
    d3.csv('/static/csv/relationship_view_people.csv', function (loaded) {
        // convert the loaded data to a nested structure, and convert
        // it to a tree with the specific settings.
        root = stratify(loaded);
        tree(root);

        // assign a group to the descendants of level 2, which we use for coloring
        var colorGroups = root.descendants().filter(function (node) { return node.depth % 2 == 0 && node.depth != 0 });


        var neighPeople = root.descendants().filter(function (node) { return node.depth % 2 == 0 && node.depth != 0 });

        //alert(neighPeople[Math.floor(Math.random() * neighPeople.length)].data.name);
        //neighPeople[0].data.name

        var tempStr = neighPeople[0].data.url

        //alert(tempStr);
        tempStr = tempStr.substring(tempStr.length - 4, tempStr.length - 2)

        setTimeout(replaceSimPeople, 3, neighPeople[0].data.name, tempStr)

        tempStr = window.location.href
        tempStr = tempStr.substring(tempStr.length - 3, tempStr.length - 1)

        setTimeout(replaceSimRate, 3, tempStr)



        var tempStr1 = neighPeople[0].data.description
        var tempStr2 = neighPeople[0].data.name
        var tempAry = neighPeople[0].data.url.split("/")
        //alert(tempAry);
        var tempStr3 = "/relationship_view_people/" + tempAry[tempAry.length - 2]
        var tempStr4 = neighPeople[0].data.url


        setTimeout(replaceRefInfo, 3, tempStr1, tempStr2, tempStr3, tempStr4)



        //TODO
        var neighMovie = root.descendants().filter(function (node) { return node.depth % 2 == 1 });


        //TODO
        var tempStr = neighMovie[0].data.url

        //alert(tempStr);
        tempStr = tempStr.substring(tempStr.length - 4, tempStr.length - 2)

        setTimeout(replaceSimPeople2, 3, neighMovie[0].data.name, tempStr)




        var tempStr11 = neighMovie[0].data.description
        var tempStr22 = neighMovie[0].data.name
        var tempAry2 = neighMovie[0].data.url.split("/")
        //alert(tempAry);
        var tempStr33 = "/relationship_view_movie/" + tempAry2[tempAry2.length - 2]
        var tempStr44 = neighMovie[0].data.url
        setTimeout(replaceRefInfo2, 3, tempStr11, tempStr22, tempStr33, tempStr44)





        colorGroups.forEach(function (group, i) {
            group.descendants().forEach(function (node) { node.data.group = i; })
        });



        // the root and rootKV, are here merely for reference, to make sure we
        // have the correct number of records at any time. Lets clone the root
        // element, so we have a working copy.
        // currentRoot =_.cloneDeep(root);
        currentRoot = _.cloneDeep(root);


        var hiddenNodes = currentRoot.descendants().filter(function (node) { return node.depth >= 1 });
        hiddenNodes.forEach(function (group, i) {
            group._children = group.children;
            group.children = null;
        });

        // render the graph based on the currentRoot
        update();

        // d3.select("svg")
        //     .attr("style", "outline: thin solid red;")   //This will do the job
        //     .attr("width", 1600)
        //     .attr("height", 800);

        // d3.select("svg")
        //     .append('rect')
        //     .attrs({ x: 10, y: 10, width: 80, height: 80, fill: 'red' })
        //     .transition()
        //     .duration(5000)
        //     .attrs({ x: 460, y: 150, width: 40, height: 40, fill: 'blue' });



        // allNodes = document.getElementsByTagName("g");

        // for (item in allNodes) {
        //     if (item.children) {
        //         item._children = item.children;
        //         item.children = null;

        //         // highlight the selected circle
        //         d3.select(item).select("circle").style("stroke", "red");
        //         d3.select(item).select("circle").style("stroke-width", "2");
        //     }
        // }



    });

    // draw or update the
    function update() {

        // calculate the x,y coordinates of the currentRoot
        tree(currentRoot);

        // create KV for simple access
        var currentRootKV = currentRoot.descendants().reduce(function (kv, el) { kv[el.data.id] = el; return kv }, {});
        //currentRootKV = currentRootKV[1];

        // the currentRoot contains the correct XY positions for all the nodes
        // minus the ones that need to be hidden. We don't want to limit the
        // number of nodes for our data elements, since that causes text and lines to
        // `jump` around. So we need to make sure we have the same amount of elements
        // and hide rendering the hidden ones.

        var toRender = root.descendants().map(function (el) {
            if (currentRootKV[el.data.id]) {
                var newNode = currentRootKV[el.data.id];
                return newNode;
            } else {
                // if the child is not in the KV map, it is hidden. We
                // now need to set its position to the calculated position of
                // the first visible parent. In other words, the first one
                // which is in the currentRootKV map.
                var fromRoot = _.cloneDeep(el);
                var parent = fromRoot.parent;
                while (!currentRootKV[parent.data.id]) {
                    parent = parent.parent;
                }
                var newParent = currentRootKV[parent.data.id];

                fromRoot.hidden = true;
                fromRoot.x = newParent.x;
                fromRoot.y = newParent.y;

                // we also set the parents x,y since the lines need to
                // be drawn from this position.
                fromRoot.parent.x = newParent.x;
                fromRoot.parent.y = newParent.y;

                return fromRoot;
            }
        });

        // now that we have to correct data, create the links
        var links = chart.selectAll(".link")
            .data(toRender.slice(1));

        var linksEnter = links.enter().append("path")
            .attr("class", "link")
            .attr("d", diagonal({ x: 0, y: 0, parent: { x: 0, y: 0 } }))
            .style("stroke", function (d) { return colorScale(d.data.group) });

        links.merge(linksEnter)
            .transition().duration(2000).attr("d", diagonal);

        // create the groups that hold the circle and the text elements
        var nodes = chart.selectAll(".node").data(toRender);

        var nodesEnter = nodes.enter().append("g")
            .attr("class", "node")
            .on("click", click)

        nodesEnter.append("circle")
            .attr("r", 2.5)
            .style("fill", function (d) { return colorScale(d.data.group) });

        nodesEnter.append("text")
            .attr("dy", ".31em")

        // combine the updated and new nodes
        var nodesUpdate = nodes.merge(nodesEnter);

        // transition the nodes (circles & text)
        nodesUpdate.transition().duration(2000)
            .attr("transform", function (d) { return "translate(" + project(d.x, d.y) + ")"; })
            .style("opacity", function (d) { return !d.hidden ? 1 : 0 })
            .on("end", function (d) { d.hidden ? d3.select(this).attr("display", "none") : "" })
            .on("start", function (d) { !d.hidden ? d3.select(this).attr("display", "") : "" });

        nodesUpdate.select("text")
            .on('click', function (d, i) {
                //alert(d.data.url);
                window.open(d.data.url);
            })
            .attr("x", function (d) { return d.x < 180 === !d.children ? 6 : -6; })
            .text(function (d) { return d.data.name; })
            // we could also tween the anchor see chapter 2
            .style("text-anchor", function (d) {
                // for the right side
                if (d.x < 180 && d.children) return "end"
                else if (d.x < 180 && !d.children) return "start"
                // for the left side
                else if (d.x >= 180 && !d.children) return "end"
                else if (d.x >= 180 && d.children) return "start"
            })
            .style("font-size", "20px")
            .transition().duration(2000)
            .attr("transform", function (d) {
                // called once to determine the target value, and tween the values
                return "rotate(" + (d.x < 180 ? d.x - 90 : d.x + 90) + ")";
            });

    }

    // on click hide the children, and color the specific node
    function click(d) {
        if (d.children) {
            d._children = d.children;
            d.children = null;

            // highlight the selected circle
            d3.select(this).select("circle").style("stroke", "red");
            d3.select(this).select("circle").style("stroke-width", "2");
        } else {
            d.children = d._children;
            d._children = null;

            // reset the highlight
            d3.select(this).select("circle").style("r", 2.5);
            d3.select(this).select("circle").style("stroke", "");
        }
        update();
    }

    // draw a curve line between d and it's parent
    function diagonal(d) {
        return "M" + project(d.x, d.y)
            + "C" + project(d.x, (d.y + d.parent.y) / 2)
            + " " + project(d.parent.x, (d.y + d.parent.y) / 2)
            + " " + project(d.parent.x, d.parent.y);
    }

    // convert the x,y to a position on the circle
    function project(x, y) {
        var angle = (x - 90) / 180 * Math.PI, radius = y;
        return [radius * Math.cos(angle), radius * Math.sin(angle)];
    }
}

function replaceSimPeople(str1, str2) {
    while (!window.simNameE) {
        simNameE = document.getElementById("simName")
    }


    simNameE.innerText = simNameE.innerText.replace("R1", str1).replace("R2", str2);
}



function replaceSimPeople2(str1, str2) {
    while (!window.simNameE) {
        simNameE = document.getElementById("simName")
    }


    simNameE.innerText = simNameE.innerText.replace("R3", str1).replace("R4", str2);
}





function replaceSimRate(str1) {
    while (!window.simRateE) {
        simRateE = document.getElementById("simRate")
    }

    //alert(str1);

    simRateE.innerText = simRateE.innerText.replace("R1", str1);
}




function replaceRefInfo(str1, str2, str3, str4) {


    while (!window.refInfoE) {
        refInfoE = document.getElementById("refInfo")
    }

    //alert(str1);

    //simRateE.innerText = simRateE.innerText.replace("R1", str1);
    refInfoE.querySelector("#refImg").src = str1;
    refInfoE.querySelector("#refName").innerText = str2;
    refInfoE.querySelector("#refDes").href = str3;
    refInfoE.querySelector("#refLink").href = str4;

}

function replaceRefInfo2(str1, str2, str3, str4) {

    while (!window.refInfoE2) {
        refInfoE2 = document.getElementById("refInfo2")
    }

    //alert(str1);

    //simRateE.innerText = simRateE.innerText.replace("R1", str1);
    refInfoE2.querySelector("#refImg2").src = str1;
    refInfoE2.querySelector("#refName2").innerText = str2;
    refInfoE2.querySelector("#refDes2").href = str3;
    refInfoE2.querySelector("#refLink2").href = str4;

}