document.addEventListener('DOMContentLoaded', function () {

    var id2node = {};
    for (var i=0; i<elements.nodes.length; i++) {
        id2node[elements.nodes[i].data.id] = elements.nodes[i];
    }

    var cy = window.cy = cytoscape({
        container: document.getElementById('cy'),

        layout: {
            name: 'breadthfirst',
            maximal: true,
            directed: true,
        },

        style: [
            {
                selector: 'node',
                style: {
                    'content': 'data(id)',
                    'background-color': 'data(color)',
                    'color': 'black',
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
        elements: elements
    });

    var aniOpt = {
        duration: 200
    };

    /* Mouse over */
    cy.on('mouseover', 'node', function(node) {
        var data = node.target.data();
        document.getElementById('course-descr').innerHTML = data.id + ": " + data.title
            + " " + data.points + " points."
            + "<br/>" + data.prereq_full;

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
    });

    /* Mouse out */
    cy.on('mouseout', 'node', function(node) {
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
    });

    /* node click */
    cy.on('tap', 'node', function(node) {
        var classId = node.target.data().id;
        var url = "http://bulletin.columbia.edu/search/?P=" + classId.replace(String.fromCharCode(160), "+");
        try { // your browser may block popups
            window.open(url);
        } catch(e){ // fall back on url change
            window.location.href = url;
        }
    });
});