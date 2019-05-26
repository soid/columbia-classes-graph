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
            // open class details if clicked selected node (for mobile)
            if (selectedNode.target.data().id == node.target.data().id) {
                openClassDetails(node);
                return;
            }
            hideNodeDeps(selectedNode);
        }
        selectedNode = node;

        // show course info
        document.getElementById('course-info').innerHTML = data.id + ": " + data.title
            + " " + data.points
            + (data.culpa ? (" (<a href='http://culpa.info/courses/" + data.culpa.id + "'>CULPA:" + data.culpa.count + "</a>)") : "")
            + "<br/>" + data.prereq;

        // show instructors info
        document.getElementById('course-descr').innerHTML = data.descr;
        if (data.instructors.length > 0) {
            document.getElementById('instructors').innerHTML = "Taught by " +
                data.instructors.map(instr => {
                    var instructorInfo = instr;
                    var instructorLinks = [];
                    if (instructors[instr] != undefined && instructors[instr]['wiki'] != undefined) {
                        instructorLinks.push(
                            "<a target='_blank' href='http://culpa.info/professors/" + instructors[instr]['culpa_id']
                            + "'>CULPA:" + instructors[instr]['count']
                            + (instructors[instr].nugget
                                ? "<img src='images/gold_nugget.gif' height='12' width='11'/>" : "")
                            + "</a>");
                    }
                    if (instructors[instr] != undefined && instructors[instr]['wiki'] != undefined) {
                        instructorLinks.push(
                            "<a target='_blank' href='https://en.wikipedia.org/wiki/"
                            + instructors[instr]['wiki']
                            + "'><img class='imglink' src='images/wikipedia.ico' height='18' width='18'/></a>");
                    }
                    if (instructorLinks.length > 0) {
                        instructorInfo += " (" + instructorLinks.join(" ") + ")";
                    }
                    return instructorInfo;
                }).join(", ");
        } else {
            document.getElementById('instructors').innerHTML = "";
        }

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
            spacingFactor: 2.3,
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


    // handle events
    document.getElementById("generationDate").innerText = generationDate;

    var sel = document.getElementById("codesList");
    sel.onchange = function (e) {
        var code = e.target.value;
        window.history.pushState("object or string", "Title", "index.html?code=" + code);
        showClassesByCode(code);
    };

    var search = document.getElementById("search");
    search.onkeypress = function (e) {
      var term = e.target.value.trim().toUpperCase();
      if (term == "") {
          cy.nodes().animate({
                  style: {
                      backgroundColor: '#ABC4AB',
                      borderWidth: 1
                  }
              },
              aniOpt);
          return;
      }
      var found = cy.nodes().filter(n => n.data().num.includes(term));
      var notFound = cy.nodes().not(found);
      found.animate({
            style: {
              backgroundColor: '#ABD897',
              borderWidth: 1
            }
          },
          aniOpt);
      notFound.animate({
            style: {
                backgroundColor: '#ABB0AB',
            }
          },
          aniOpt);

    };
    search.onchange = search.onkeypress;
    search.onpaste = search.onkeypress;
    search.oninput = search.onkeypress;

    // show the graph
    Object.keys(classCodes).forEach(function (k) {
        var opt = document.createElement('option');
        opt.appendChild(document.createTextNode(((classCodes[k] == k) ? "" : (k + ": ")) + classCodes[k]));
        opt.value = k;
        sel.appendChild(opt);
    });

    // pick COMS for starter
    var url = new URL(window.location.href);
    var selectedCode = url.searchParams.get("code") || "COMS";
    showClassesByCode(selectedCode);
    sel.value = selectedCode;
});
