document.addEventListener('DOMContentLoaded', function () {

    var id2node = {};
    for (var i=0; i<elements.nodes.length; i++) {
        id2node[elements.nodes[i].data.id] = elements.nodes[i];
    }

    var cy = window.cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
            {
                selector: 'node',
                style: {
                    'content': 'data(num)',
                    'background-color': 'data(color)',
                    'color': 'black',
                    'height': 'data(size)',
                    'width': 'data(size)'
                }
            },
            {
                selector: 'edge',
                style: {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'width': 1
                }
            }
        ],
    });

    var aniOpt = {
        duration: 200
    };

    /* Mouse over */
    var selectedNode = null;
    var showNodeDeps = function(node) {
        var data = node.target.data();
        if (selectedNode != null) {
            if (selectedNode.target.data().id == node.target.data().id) {
                openClassDetails(node);
                return;
            }
            hideNodeDeps(selectedNode);
        }
        selectedNode = node;
        document.getElementById('course-info').innerHTML = data.id + ": " + data.title
            + " " + data.points
            + "<br/>" + data.prereq;
        document.getElementById('course-descr').innerHTML = data.descr;

        // grey out unrelated classes
        cy.nodes().not(node.target.predecessors().nodes()).not(node.target).animate({
            style: {
                opacity: 0.2,
            }
        }, aniOpt);

        // bold nodes for related classes
        node.target.animate({
            style: {
                borderColor: "#2D3142",
                borderWidth: 3
            }
        }, aniOpt);

        // bold edges for related classes
        node.target.predecessors().edges().animate({
            style: {
                width: 4,
            }
        }, aniOpt);

        // borders for related classes
        node.target.predecessors().nodes().animate({
            style: {
                borderColor: "#2D3142",
                borderWidth: 3
            }
        }, aniOpt);
    };
    cy.on('mouseover', 'node', showNodeDeps);
    cy.on('tap', 'node', showNodeDeps);

    /* Mouse out */
    var hideNodeDeps = function(node) {
        selectedNode = null;
        // cancel grey out unrelated classes
        cy.nodes().not(node.target.predecessors().nodes()).animate({
            style: {
                opacity: 1,
            }
        }, aniOpt);

        // bold nodes for related classes
        node.target.animate({
            style: {
                borderWidth: 0
            }
        }, aniOpt);

        // cancel bold lines for related classes
        node.target.predecessors().edges().animate({
            style: {
                width: 1,
            }
        }, aniOpt);

        // cancel borders for related classes
        node.target.predecessors().nodes().animate({
            style: {
                borderColor: "#2D3142",
                borderWidth: 0
            }
        }, aniOpt);
    };
    cy.on('mouseout', 'node', hideNodeDeps);

    /* show classes by code */
    var showClassesByCode = function(code) {
        cy.elements().remove();
        var shown = new Set();
        elements.nodes.forEach(n => {
            if (n.data.code == code) {
                cy.add(n)
                shown.add(n.data.num);
            }
        });
        elements.edges.forEach(e => {
            if (e.data.code == code) {
               if (id2node[e.data.source]) {
                 if (!shown.has(e.data.source)) {
                   cy.add(id2node[e.data.source])
                   shown.add(e.data.source);
                 }
               } else {
                 return;
               }

               if (id2node[e.data.target]) {
                 if (!shown.has(e.data.target)) {
                    cy.add(id2node[e.data.target])
                    shown.add(e.data.target);
                  }
               } else {
                 return;
               }
               cy.add(e);
            }
        });

        var layout = cy.layout({
            name: 'breadthfirst',
            grid: true,
            animate: true,
            maximal: true,
            directed: true,
        });
        layout.run();
    }

    /* node click */
    var openClassDetails = function(node) {
        var classId = node.target.data().id;
        var url = "http://bulletin.columbia.edu/search/?P=" + classId.replace(String.fromCharCode(160), "+");
        try { // your browser may block popups
            window.open(url);
        } catch(e){ // fall back on url change
            window.location.href = url;
        }
    };


    // show the graph
    document.getElementById("generationDate").innerText = generationDate;

    var sel = document.getElementById("codesList");
    sel.onchange = function (e) {
        var code = e.target.value;
        window.history.pushState("object or string", "Title", "index.html?code=" + code);
        showClassesByCode(code);
    };

    Object.keys(classCodes).forEach(function (k) {
        var opt = document.createElement('option');
        opt.appendChild(document.createTextNode(classCodes[k] + ((classCodes[k] == k) ? "" : (" (" + k + ")"))));
        opt.value = k;
        sel.appendChild(opt);
    });

    // pick COMS for starter
    var url = new URL(window.location.href);
    var selectedCode = url.searchParams.get("code") || "COMS";
    showClassesByCode(selectedCode);
    sel.value = selectedCode;
});
