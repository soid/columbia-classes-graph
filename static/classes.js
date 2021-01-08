'use strict';

class CUGraph {
    constructor() {
        this.id2node = {};
        this.aniOpt = {
            duration: 200
        };
    }

    /* executed on loading a semester */
    loadColumbiaGraph() {
        let me = this;
        // index by id
        for (let i = 0; i < elements.nodes.length; i++) {
            this.id2node[elements.nodes[i].data.id] = elements.nodes[i];
        }

        this.cy = window.cy = cytoscape({
            container: document.getElementById('cy'),
            style: [
                {
                    selector: 'node',
                    style: {
                        'content': 'data(course_code)',
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

        /* Mouse over */
        let selectedNode = null;
        let showNodeDeps = function (node) {
            let data = node.target.data();
            if (selectedNode != null) {
                // open class details if clicked selected node (for mobile)
                if (selectedNode.target.data().id === node.target.data().id) {
                    openClassDetails(node);
                    return;
                }
                hideNodeDeps(selectedNode);
            }
            selectedNode = node;

            // show course info
            document.getElementById('course-info').innerHTML = data.id + ": " + data.course_title
                + " (" + plural(data.points, "point") + ")"
                + (data.instructor_culpa_link
                    ? (" (<a target='_blank' href='" + data.instructor_culpa_link + "'>" +
                        "CULPA:" + data.instructor_culpa_reviews_count + "</a>)")
                    : "")
                ;

            // show instructors info
            document.getElementById('course-descr').innerHTML = data.course_descr;
            if (data.instructors.length > 0) {
            // if (data.instructors) {
                document.getElementById('instructors').innerHTML = "Taught by " +
                    // data.instructor; // TODO fix it
                    data.instructors.map(instr => {
                        let instructorInfo = instr;
                        let instructorLinks = [];
                        if (instructors[instr] !== undefined && instructors[instr]['culpa_id'] !== undefined) {
                            instructorLinks.push(
                                "<a target='_blank' href='http://culpa.info/professors/" + instructors[instr]['culpa_id']
                                + "'>CULPA:" + instructors[instr]['count']
                                + (instructors[instr].nugget
                                ? ("<img alt='Wikipedia' src='static/images/" + instructors[instr].nugget + "_nugget.gif' height='12' width='11'/>") : "")
                                + "</a>");
                        }
                        if (instructors[instr] !== undefined && instructors[instr]['wiki'] !== undefined) {
                            instructorLinks.push(
                                "<a target='_blank' href='https://en.wikipedia.org/wiki/"
                                + instructors[instr]['wiki']
                                + "'><img alt='Wikipedia' class='imglink' src='static/images/wikipedia.ico' height='18' width='18'/></a>");
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
            this.cy().nodes().not(node.target.predecessors().nodes()).not(node.target).animate({
                style: {
                    opacity: 0.2,
                }
            }, this.aniOpt);

            // bold nodes for related classes
            node.target.animate({
                style: {
                    borderColor: "#2D3142",
                    borderWidth: 3
                }
            }, this.aniOpt);

            // bold edges for related classes
            node.target.predecessors().edges().animate({
                style: {
                    width: 4,
                }
            }, this.aniOpt);

            // borders for related classes
            node.target.predecessors().nodes().animate({
                style: {
                    borderColor: "#2D3142",
                    borderWidth: 3
                }
            }, this.aniOpt);
        };
        this.cy.on('mouseover', 'node', showNodeDeps);
        this.cy.on('tap', 'node', showNodeDeps);

        /* Mouse out */
        let hideNodeDeps = function (node) {
            selectedNode = null;
            // cancel grey out unrelated classes
            this.cy().nodes().not(node.target.predecessors().nodes()).animate({
                style: {
                    opacity: 1,
                }
            }, this.aniOpt);

            // bold nodes for related classes
            node.target.animate({
                style: {
                    borderWidth: 0
                }
            }, this.aniOpt);

            // cancel bold lines for related classes
            node.target.predecessors().edges().animate({
                style: {
                    width: 1,
                }
            }, this.aniOpt);

            // cancel borders for related classes
            node.target.predecessors().nodes().animate({
                style: {
                    borderColor: "#2D3142",
                    borderWidth: 0
                }
            }, this.aniOpt);
        };
        this.cy.on('mouseout', 'node', hideNodeDeps);

        /* node click - open class page */
        let openClassDetails = function (node) {
            let classId = node.target.data().id;
            let url = "http://bulletin.columbia.edu/search/?P=" + classId.replace(String.fromCharCode(160), "+");
            try { // your browser may block popups
                window.open(url);
            } catch (e) { // fall back on url change
                window.location.href = url;
            }
        };

        // handle events
        document.getElementById("generationDate").innerText = generationDate;

        let sel = document.getElementById("codesList");
        sel.onchange = function (e) {
            let code = e.target.value;
            me.changeFilters({"code": code});
            me.applyFilters();
        };

        // typing in search box
        let search = document.getElementById("search");
        // search.onkeypress = this.onSearchKeyPress;
        let f = ev => this.onSearchKeyPress(ev);
        search.addEventListener("keypress", f);
        search.addEventListener("change", f);
        search.addEventListener("paste", f);
        search.addEventListener("input", f);

        // advanced filters
        let advFilters = document
            .getElementById("advanced-filters")
            .getElementsByTagName('input');
        for (let filter of advFilters) {
            filter.addEventListener("change", ev => this.applyFilters());
        }

        // more filters button
        document.getElementById("more-filters-btn")
            .addEventListener("click", ev=> {
                let xs = document.getElementsByClassName("adv-filter");
                for (let x of xs) {
                    if (x.style.display === "none") {
                        x.style.display = "inline";
                    } else {
                        x.style.display = "none";
                    }
                }
            });

        // add classes groups in the dropdown list
        Object.keys(classGroups).forEach(function (k) {
            let opt = document.createElement('option');
            opt.appendChild(document.createTextNode(k));
            opt.value = "group:" + k.replace(" ", "_");
            sel.appendChild(opt);
        });

        // add divisor
        {
            let opt = document.createElement('option');
            opt.appendChild(document.createTextNode("---"));
            opt.value = "";
            opt.disabled = true;
            sel.appendChild(opt);
        }

        // show departments dropdown list
        Object.keys(classCodes).forEach(function (k) {
            let opt = document.createElement('option');
            opt.appendChild(document.createTextNode(((classCodes[k] === k) ? "" : (k + ": ")) + classCodes[k]));
            opt.value = k;
            sel.appendChild(opt);
        });

        // pick COMS for starter
        {
            let url = new URL(window.location.href);
            let selectedCode = url.searchParams.get("code") || "COMS";  // TODO: read the parameter from a single place
            sel.value = selectedCode;
        }

        this.applyFilters();
    }

    onSearchKeyPress(e) {
        let term = e.target.value.trim().toUpperCase();
        if (term === "") {
            this.cy.nodes().animate({
                    style: {
                        backgroundColor: '#ABC4AB',
                        borderWidth: 1
                    }
                },
                this.aniOpt);
            return;
        }
        let searchFunc = function (data) {
            return data.course_code.includes(term)
                || data.course_title.toUpperCase().includes(term)
                || data.instructors.find(instr => instr.toUpperCase().includes(term) );
        };
        let found = this.cy.nodes().filter(node => searchFunc(node.data()));
        if (found.length === 0 && e.key === "Enter") {
            // nothing found, try other departments
            elements.nodes.every(function (node, index) {
                if (searchFunc(node.data)) {
                    console.log("found!" + node.data.department_code);
                    let sel = document.getElementById("codesList");
                    sel.value = node.data.department_code;
                    sel.dispatchEvent(new Event('change'));
                    return false;
                }
                return true;
            });
            search.dispatchEvent(new Event('change'));
            return;
        }
        let notFound = this.cy.nodes().not(found);
        found.animate({
                style: {
                    backgroundColor: '#ABD897',
                    borderWidth: 1
                }
            },
            this.aniOpt);
        notFound.animate({
                style: {
                    backgroundColor: '#ABB0AB',
                }
            },
            this.aniOpt);

    }

    loadSemesters() {
        // sort semesters
        let sems = new Set();
        let slist = Object.keys(semesters);
        slist.sort((a, b) => {
            let alist = a.split(" ");
            let blist = b.split(" ");
            if (alist[1] != blist[1]) // not same year
                return alist[1] - blist[1];
            let conv = function(term) {
                if (term == 'Spring') return 1;
                if (term == 'Summer') return 2;
                if (term == 'Fall') return 3;
            }
            alist[0] = conv(alist[0]);
            blist[0] = conv(blist[0]);

            return alist[0] - blist[0];
        });
        slist.forEach(function (name) {
            sems.add({name: name, value: semesters[name]});
        });
        // sems.add({name: "all semesters", value: "all"});

        // add semesters to dropdown list
        let semesterSel = document.getElementById("semesterList");
        sems = Array.from(sems);
        sems.forEach(function (sem) {
            let opt = document.createElement('option');
            opt.appendChild(document.createTextNode(sem.name));
            opt.value = sem.value;
            semesterSel.appendChild(opt);
        });
        let me = this;
        semesterSel.onchange = function (e) {
            let semester = e.target.value;
            me.changeFilters({"semester": semester});

            // find semester id
            let semesterStr = me.getSemesterId(semester);
            elements = null;
            loadData("classes-" + semesterStr + ".js", ev => me.applyFilters());
        };
        let url = new URL(window.location.href);
        let selectedSemester = this.getSemesterId(url.searchParams.get("semester"));
        semesterSel.value = selectedSemester;
    }

    /* Filter changes. If any parameter is undefined then pick the current one. Updates URL */
    changeFilters(newParams) {
        let url = new URL(window.location.href);
        let allParams = ["code", "semester"];
        let urlParams = [];

        // creates new parameter in url and adds it to urlParams list
        let makeParam = function (name, newValue) {
            let selected = url.searchParams.get(name);
            let str = newValue === undefined
                ? (selected ? (name + "=" + selected) : "")
                : (name + "=" + newValue);
            urlParams.push(str);
        };

        // process all new params
        allParams.forEach(function (paramName) {
            makeParam(paramName, newParams[paramName]);
        });

        window.history.pushState("object or string", "Title",
            "?" + urlParams.join("&"));
    }

    /* show classes, filter, etc */
    applyFilters() {
        let url = new URL(window.location.href);
        let code = url.searchParams.get("code") || "COMS";
        let semester = this.getSemesterId(url.searchParams.get("semester"));

        let filterFunc;
        let groupKeyword = "group:";
        let semesterFilter = true; // TODO get rid of this
        if (code.startsWith(groupKeyword)) {
            let group = code.substring(groupKeyword.length).replace("_", " ");
            let groupClasses = classGroups[group];
            filterFunc = function (code, node) {
                let groupFilter = groupClasses.indexOf(node.data.id) !== -1;
                // let semesterFilter = node.data.schedule[semester] !== undefined || semester === "all";
                return groupFilter && semesterFilter;
            }
        } else {
            // find if level filter used
            let lvlSelected = Array(6)
                .fill()
                .map((_, i) =>
                    document.getElementById("l" + (i+1) + "000").checked);
            let lvlUsed = lvlSelected.find(v => v);

            // find day of week filters
            let daySelected = Array(7)
                .fill()
                .map((_, i) =>
                    document.getElementById("df" + i).checked);
            let dayUsed = daySelected.find(v => v);

            // filter function
            filterFunc = function (code, node) {
                let codeFilter = node.data.department_code === code;

                // level filter
                var levelFilter = true;
                if (lvlUsed) {
                    let lvl = parseInt(node.data.course_code.slice(-4)[0]);
                    levelFilter = lvlSelected[lvl-1];
                }

                // day filter
                var dayFilter = true;
                if (dayUsed && node.data.scheduled_days) {
                    dayFilter = false;
                    let alldays = "MTWRFSU";
                    for (let i=0; i<7; i++) {
                        if (daySelected[i]) {
                            if (node.data.scheduled_days.includes(alldays[i])) {
                                dayFilter = true;
                                break;
                            }
                        }
                    }
                }

                // let semesterFilter = node.data.schedule[semester] !== undefined || semester === "all";
                return codeFilter && semesterFilter && levelFilter && dayFilter;
            }
        }

        this.cy.elements().remove();
        let shown = new Set();
        elements.nodes.forEach(n => {
            if (filterFunc(code, n)) {
                this.cy.add(n);
                shown.add(n.data.course_code);
            }
        });
        let filtered = new Set(shown);
        let filterEdge = function (e) {
            return filtered.has(e.data.source) || filtered.has(e.data.target);
        };
        elements.edges.forEach(e => {
            if (filterEdge(e)) {
                // show edge source if it's not shown
                if (this.id2node[e.data.source]) {
                    if (!shown.has(e.data.source)) {
                        this.cy.add(this.id2node[e.data.source]);
                        shown.add(e.data.source);
                    }
                } else {
                    return;
                }

                // show edge target if it's not shown
                if (this.id2node[e.data.target]) {
                    if (!shown.has(e.data.target)) {
                        this.cy.add(this.id2node[e.data.target]);
                        shown.add(e.data.target);
                    }
                } else {
                    return;
                }
                this.cy.add(e);
            }
        }, this);

        let layout = this.cy.layout({
            name: 'breadthfirst',
            spacingFactor: 2.3,
            grid: true,
            animate: true,
            maximal: true,
            directed: true,
        });
        layout.run();
    }

    getSemesterId(semester) {
        let semesterStr;
        if (semester == undefined) {
            // compute current semester
            let td = new Date();
            let term = "Spring";
            if (td.getMonth() >= 4) term = "Summer";
            if (td.getMonth() >= 8) term = "Fall";

            semesterStr = term + "-" + (td.getFullYear());
        } else {
            semesterStr = semester;
        }
        return semesterStr.replace(" ", "-");
    }
}

function loadData(name, onLoad) {
    var script = document.createElement("script");
    script.src = "data/" + name;
    script.type = "application/javascript";
    script.onload = onLoad;
    document.head.appendChild(script);
}

function plural(count, noun) {
    if (count == 1) {
        return count + " " + noun
    } else {
        return count + " " + noun + "s"
    }
}

var cug;
// executed when this script is loaded
(function() {
    cug = new CUGraph()
    let url = new URL(window.location.href);
    let semesterStr = cug.getSemesterId(url.searchParams.get("semester"));

    loadData("classes-" + semesterStr + ".js", ev => cug.loadColumbiaGraph());
    loadData("semesters.js", ev => cug.loadSemesters());
})();
