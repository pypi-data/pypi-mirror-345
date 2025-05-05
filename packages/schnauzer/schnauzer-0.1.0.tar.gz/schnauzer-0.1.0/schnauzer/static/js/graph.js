// graph.js - Core graph visualization functionality
// Handles the D3.js SVG setup and rendering

function initializeVisualization() {
    const app = window.SchGraphApp;
    const width = app.elements.graphContainer.clientWidth;
    const height = app.elements.graphContainer.clientHeight;

    let svg, zoom, simulation, node, link;

    function getNodeDimensions(node) {
        const label = node.name || node.id || "Unknown";
        // Increase default width and make dynamic calculation more generous
        return {
            width: Math.max(100, label.length * 6), // Increased from 100 to 120 and multiplier from 8 to 10
            height: 60
        };
    }

    // Create SVG container
    svg = d3.select("#graph-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // Create a group for the graph that can be transformed
    const g = svg.append("g");

    // Set up zoom behavior
    zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoom);

    // Create marker for arrow
    svg.append("defs").append("marker")
        .attr("id", "arrowhead")
        .attr("viewBox", "-0 -5 10 10")
        .attr("refX", 0)  // Changed from original value
        .attr("refY", 0)
        .attr("orient", "auto")
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("overflow", "visible")
        .append("svg:path")
        .attr("d", "M 0,-5 L 10,0 L 0,5")
        .attr("fill", "#999")
        .style("stroke", "none");

    // Get tooltip element
    const tooltip = d3.select(".graph-tooltip");

    // Track tooltip state
    let tooltipVisible = false;
    let currentTooltipNode = null;

    // Add mouse event listeners to track mouse state
    svg.on("mousedown", function() {
        app.state.isMouseDown = true;

        // Hide tooltip immediately on mousedown
        hideTooltip();
    });

    svg.on("mouseup", function() {
        app.state.isMouseDown = false;
    });

    // Ensure mouse up is detected even if released outside the SVG
    document.addEventListener("mouseup", function() {
        app.state.isMouseDown = false;
    });

    function showNodeTooltip(event, d) {
        // Don't show tooltip if mouse is pressed (during dragging)
        if (app.state.isMouseDown) return;

        // Set current node
        currentTooltipNode = d;

        let html = ``

        html += `<h4>${escapeHTML(d.name || "Node")}</h4>`;

        // Format the description for hover tooltip
        if (d.description) {
            let description = d.description;
            description += d.description.length > 150 ?
                escapeHTML(description.substring(0, 147) + "...") :
                escapeHTML(description);
            html += `
                <hr>
                <h6>Description</h6>
                <div class="node-description">${description}</div>
            `;
        }

        // Format parent and child names for tooltip using pre-calculated data
        if (d.parents && d.parents.length > 0) {
            html += `<p><strong>Parents:</strong><br>`;
            html += escapeHTML(d.parents.map(p => p.name).join('\n'));
            html += `</p>`;
        }

        if (d.children && d.children.length > 0) {
            html += `<p><strong>Children:</strong><br>`;
            html += escapeHTML(d.children.map(p => p.name).join('\n'));
            html += `</p>`;
        }

        // Update tooltip content with enhanced information
        tooltip.html(html);

        // Position the tooltip
        tooltip
            .style("left", (event.pageX + 15) + "px")
            .style("top", (event.pageY - 30) + "px");

        // Make tooltip visible
        tooltip
            .transition()
            .duration(50)
            .style("opacity", 0.95);

        tooltipVisible = true;
    }

    // Show tooltip for edges
    function showEdgeTooltip(event, d) {
        // Don't show tooltip if mouse is pressed (during dragging)
        if (app.state.isMouseDown) return;

        // Set current edge
        currentTooltipNode = d;

        // Get source and target names
        const sourceName = typeof d.source === 'object' ?
            (d.source.name) : d.source;
        const targetName = typeof d.target === 'object' ?
            (d.target.name) : d.target;

        // Update tooltip content
        tooltip.html(`
            <h4>${escapeHTML(d.name) || "Edge"}</h4>
            <p><strong>From:</strong> ${escapeHTML(sourceName)}</p>
            <p><strong>To:</strong> ${escapeHTML(targetName)}</p>
        `);

        // Position the tooltip near the cursor
        tooltip
            .style("left", (event.pageX + 15) + "px")
            .style("top", (event.pageY - 30) + "px");

        // Make tooltip visible with a very short transition
        tooltip
            .transition()
            .duration(50)
            .style("opacity", 0.95);

        tooltipVisible = true;
    }

    // Hide tooltip function
    function hideTooltip() {
        // Only transition if tooltip was visible
        if (tooltipVisible) {
            tooltip
                .transition()
                .duration(50)
                .style("opacity", 0);

            tooltipVisible = false;
            currentTooltipNode = null;
        }
    }

    // Render a graph from data
    function updateGraph(graph) {
        // Ensure graph has nodes and links arrays
        if (!graph.nodes) graph.nodes = [];
        if (!graph.edges) graph.edges = [];

        // Update counters if the app has stats elements
        if (app.elements.nodeCountEl) {
            app.elements.nodeCountEl.textContent = graph.nodes.length;
        }
        if (app.elements.edgeCountEl) {
            app.elements.edgeCountEl.textContent = graph.edges.length;
        }

        // Clear existing graph elements
        g.selectAll(".node").remove();
        g.selectAll(".link").remove();

        // Create dynamic markers for different colored edges
        const defs = svg.select("defs");
        const colors = new Set();

        // Add default color
        colors.add("#999");

        // Collect all unique edge colors
        graph.edges.forEach(edge => {
            if (edge.color) {
                colors.add(edge.color);
            }
        });

        // Clear existing markers
        defs.selectAll("marker").remove();

        // Create a marker for each color
        colors.forEach(color => {
            const markerId = "arrowhead-" + color.replace('#', '');
            defs.append("marker")
                .attr("id", markerId)
                .attr("viewBox", "-0 -5 10 10")
                .attr("refX", 0)
                .attr("refY", 0)
                .attr("orient", "auto")
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("overflow", "visible")
                .append("svg:path")
                .attr("d", "M 0,-5 L 10,0 L 0,5")
                .attr("fill", color)
                .style("stroke", "none");
        });

        // Set up force simulation
        simulation = d3.forceSimulation(graph.nodes)
            .force("link", d3.forceLink(graph.edges)
                .id(d => d.name)
                .distance(200)
                .strength(0.5))
            .force("charge", d3.forceManyBody()
                .strength(-1800)
                .distanceMin(150)
                .distanceMax(500))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius(100).strength(1.0))
            .force("x", d3.forceX(width / 2).strength(0.07))
            .force("y", d3.forceY(height / 2).strength(0.07));

        // Create links with wider click/hover areas
        link = g.selectAll(".link")
            .data(graph.edges)
            .enter()
            .append("g")  // Use a group to contain both visible line and invisible click area
            .attr("class", "link-group");

        // Add the visible line
        link.append("line")
            .attr("class", "link")
            .attr("stroke-width", 2)
            .attr("stroke", d => d.color || "#999")
            .attr("marker-end", function(d) {
                const color = d.color || "#999";
                const markerId = "arrowhead-" + color.replace('#', '');
                return "url(#" + markerId + ")";
            });

        // Add invisible wider line for easier interaction (10px wide)
        link.append("line")
            .attr("class", "link-hitarea")
            .attr("stroke-width", 10)  // Much wider than the visible line
            .attr("stroke", "transparent")  // Invisible
            .attr("stroke-opacity", 0)  // Completely transparent
            .style("cursor", "pointer");  // Show pointer cursor on hover

        // Add events to the group
        link.on("click", edgeClicked)
            .on("mouseover", function(event, d) {
                if (!app.state.isMouseDown) {
                    // Highlight the visible line
                    d3.select(this).select(".link").attr("stroke-width", 4);
                    showEdgeTooltip(event, d);
                }
            })
            .on("mousemove", function(event, d) {
                // Update tooltip position if it's for the current edge
                if (tooltipVisible && currentTooltipNode === d) {
                    tooltip
                        .style("left", (event.pageX + 15) + "px")
                        .style("top", (event.pageY - 30) + "px");
                }
            })
            .on("mouseout", function() {
                // Reset line width
                d3.select(this).select(".link").attr("stroke-width", 2);
                hideTooltip();
            });

        // Create node groups
        node = g.selectAll(".node")
            .data(graph.nodes)
            .enter()
            .append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragStarted)
                .on("drag", dragged)
                .on("end", dragEnded))
            .on("click", nodeClicked);

        // Add square nodes with text wrapping
        node.append("rect")
            .attr("width", d => getNodeDimensions(d).width)
            .attr("height", d => getNodeDimensions(d).height)
            .attr("x", d => -getNodeDimensions(d).width / 2)
            .attr("y", d => -getNodeDimensions(d).height / 2)
            .attr("rx", 6)
            .attr("ry", 6)
            .attr("fill", d => d.color)
            .attr("stroke", "#fff")
            .attr("stroke-width", 2);

        // Add text with improved wrapping
        node.each(function(d) {
            const name = d.name || "Unknown";
            const nodeWidth = getNodeDimensions(d).width - 20; // Padding
            const text = d3.select(this).append("text")
                .attr("text-anchor", "middle")
                .attr("fill", d => getNodeTextColor(d))
                .attr("pointer-events", "none");

            // Improved text wrapping algorithm that handles long words without spaces
            let words = name.split(/\s+/);
            let line = "";
            let lineNumber = 0;
            const lineHeight = 20;
            const maxCharPerLine = Math.floor(nodeWidth / 7); // Approx. character width

            for (let i = 0; i < words.length; i++) {
                let word = words[i];

                // Handle very long words by splitting them
                if (word.length > maxCharPerLine) {
                    // If line is not empty, add it first
                    if (line) {
                        text.append("tspan")
                            .attr("x", 0)
                            .attr("y", 0)
                            .attr("dy", lineNumber * lineHeight)
                            .text(line);
                        lineNumber++;
                        line = "";
                    }

                    // Split long word into chunks
                    while (word.length > 0) {
                        const chunk = word.substring(0, maxCharPerLine - 1);
                        word = word.substring(maxCharPerLine - 1);

                        // Add hyphen if not at the end
                        const displayChunk = word.length > 0 ? chunk + "-" : chunk;

                        text.append("tspan")
                            .attr("x", 0)
                            .attr("y", 0)
                            .attr("dy", lineNumber * lineHeight)
                            .text(displayChunk);
                        lineNumber++;
                    }
                } else {
                    // Normal word processing
                    let testLine = line + (line ? " " : "") + word;
                    if (testLine.length * 7 > nodeWidth) {
                        // Add the current line
                        text.append("tspan")
                            .attr("x", 0)
                            .attr("y", 0)
                            .attr("dy", lineNumber * lineHeight)
                            .text(line);
                        line = word;
                        lineNumber++;
                    } else {
                        line = testLine;
                    }
                }
            }

            // Add the last line if not empty
            if (line) {
                text.append("tspan")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("dy", lineNumber * lineHeight)
                    .text(line);
            }
        });

        // Add tooltip events with improved responsiveness
        node.on("mouseover", function(event, d) {
            if (!app.state.isMouseDown) {
                showNodeTooltip(event, d);
            }
        })
        .on("mousemove", function(event, d) {
            // Update tooltip position if it's for the current node
            if (tooltipVisible && currentTooltipNode === d) {
                tooltip
                    .style("left", (event.pageX + 15) + "px")
                    .style("top", (event.pageY - 30) + "px");
            }
        })
        .on("mouseout", function() {
            hideTooltip();
        });

        simulation.on("tick", () => {
            link.each(function(d) {
                // Calculate direction vector between source and target
                const dx = d.target.x - d.source.x;
                const dy = d.target.y - d.source.y;

                // Get target node dimensions
                const targetDimensions = getNodeDimensions(d.target);
                const padding = 12; // Padding before the node boundary

                // Calculate the distance to the rectangle intersection
                const distance = Math.sqrt(dx * dx + dy * dy);

                // Using normalized direction for consistent approach
                const unitDx = dx / distance;
                const unitDy = dy / distance;

                // Find intersection with rectangle using parametric approach
                let t = Infinity;
                const halfWidth = targetDimensions.width / 2;
                const halfHeight = targetDimensions.height / 2;

                // Check intersection with each edge of the rectangle
                if (unitDx !== 0) {
                    // Intersection with vertical edges
                    const tx1 = (-halfWidth - padding) / unitDx; // Left edge
                    const tx2 = (halfWidth + padding) / unitDx;  // Right edge
                    t = Math.min(t, Math.max(tx1, tx2));
                }

                if (unitDy !== 0) {
                    // Intersection with horizontal edges
                    const ty1 = (-halfHeight - padding) / unitDy; // Top edge
                    const ty2 = (halfHeight + padding) / unitDy;  // Bottom edge
                    t = Math.min(t, Math.max(ty1, ty2));
                }

                // Calculate target point
                const targetX = d.target.x - t * unitDx;
                const targetY = d.target.y - t * unitDy;

                // Set the coordinates for both the visible line and hit area
                d3.select(this).selectAll("line")
                    .attr("x1", d.source.x)
                    .attr("y1", d.source.y)
                    .attr("x2", targetX)
                    .attr("y2", targetY);
            });

            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });
    }

    // Handle node click to show details
    function nodeClicked(event, d) {
        // Prevent event bubbling
        event.stopPropagation();

        // Deselect current node if it's the same one
        if (app.state.selectedNode === d.name) {
            app.state.selectedNode = null;
            app.elements.nodeDetails.classList.add('d-none');
            return;
        }

        // Clear selected edge if any
        app.state.selectedEdge = null;

        // Update selected node
        app.state.selectedNode = d.name;

        // Show the details panel
        app.elements.nodeDetails.classList.remove('d-none');
        app.elements.nodeDetailsTitle.textContent = d.name || "Node Details";

        // Apply colors to the details panel header
        const headerEl = app.elements.nodeDetails.querySelector('.card-header');
        if (headerEl) {
            headerEl.style.backgroundColor = d.color;
            headerEl.style.color = getTextColor(d.color);
        }

        // Format node details using the utility function
        app.elements.nodeDetailsContent.innerHTML = window.SchGraphApp.utils.formatNodeDetails(d);
    }

    // Handle edge click to show details
    function edgeClicked(event, d) {
        // Prevent event bubbling
        event.stopPropagation();

        // Deselect current edge if it's the same one
        if (app.state.selectedEdge === d) {
            app.state.selectedEdge = null;
            app.elements.nodeDetails.classList.add('d-none');
            return;
        }

        // Clear selected node if any
        app.state.selectedNode = null;

        // Update selected edge
        app.state.selectedEdge = d;

        // Show the details panel
        app.elements.nodeDetails.classList.remove('d-none');
        app.elements.nodeDetailsTitle.textContent = d.name || "Edge Details";

        // Format edge details using the utility function
        app.elements.nodeDetailsContent.innerHTML = window.SchGraphApp.utils.formatEdgeDetails(d);
    }

    // Drag functions for nodes
    function dragStarted(event, d) {
        // Hide tooltip immediately when starting to drag
        hideTooltip();

        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        if (!app.state.physicsEnabled) {
            d.fx = event.x;
            d.fy = event.y;
        } else {
            d.fx = null;
            d.fy = null;
        }
    }

    // Reset zoom function - FIXED VERSION
    function resetZoom() {
        console.log('Resetting zoom'); // Debug log
        if (svg && zoom) {
            svg.transition()
                .duration(750)
                .call(zoom.transform, d3.zoomIdentity);
        } else {
            console.error('svg or zoom not defined');
        }
    }

    // Toggle physics simulation
    function togglePhysics(enabled) {
        if (enabled) {
            // Release fixed positions
            if (node) {
                node.each(d => {
                    d.fx = null;
                    d.fy = null;
                });
                simulation.alpha(0.3).restart();
            }
        } else {
            // Fix nodes in current positions
            if (node) {
                node.each(d => {
                    d.fx = d.x;
                    d.fy = d.y;
                });
            }
        }
    }

    function updateForces(forces) {
    if (!simulation) return;

    // Update charge force
    if (forces.charge !== undefined) {
        simulation.force("charge")
            .strength(forces.charge);
    }

    // Update link distance
    if (forces.linkDistance !== undefined) {
        simulation.force("link")
            .distance(forces.linkDistance);
    }

    // Update collision strength
    if (forces.collisionStrength !== undefined) {
        simulation.force("collide")
            .strength(forces.collisionStrength);
    }

    // Use a smaller alpha for smoother transitions during slider changes
    simulation.alpha(0.1).restart();
}

    // Return public API
    return {
        updateGraph,
        resetZoom,
        togglePhysics,
        updateForces
    };
}