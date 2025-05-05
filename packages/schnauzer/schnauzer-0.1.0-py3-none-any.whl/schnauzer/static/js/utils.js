// utils.js - Utility functions for the graph visualization
function escapeHTML(str = '') {
    if (str === null || str === undefined) {
        return null;
    }
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
}


/**
 * Format node data for display in details panel
 * @param {Object} node - The node data object
 * @returns {string} HTML formatted node details
 */
function formatNodeDetails(node) {
    // Debug output to see what data is actually being received
    if (!node) return '<p>No node data available</p>';

    let html = '';

    // Show node name at the top
    html += `<p><strong>Name:</strong> ${escapeHTML(node.name) || 'Unknown'}</p>`;
    html += `<p><strong>Type:</strong> ${escapeHTML(node.type) || 'Unknown'}</p>`;

    // Show all labels from the dictionary
    if (node.labels && Object.keys(node.labels).length > 0) {
        for (const [key, value] of Object.entries(node.labels)) {
            html += `<p><strong>${escapeHTML(key)}:</strong> ${escapeHTML(value)}</p>`;
        }
    }

    // Show parents
    if (node.parents && Array.isArray(node.parents) && node.parents.length > 0) {
        html += `<p><strong>Parents:</strong><br> `;
        const parentNames = node.parents.map(p => p.name).join('\n');
        html += escapeHTML(parentNames);
        html += `</p>`;
    }


    // Show children
    if (node.children && Array.isArray(node.children) && node.children.length > 0) {
        html += `<p><strong>Children:</strong><br> `;
        const childrenNames = node.children.map(c => c.name).join(',\n');
        html += escapeHTML(childrenNames);
        html += `</p>`;
    }


    // Add description if available
    if (node.description) {
        html += `
            <hr>
            <h6>Description</h6>
            <div class="node-description">${escapeHTML(node.description)}</div>
        `;
    }

    return html;
}

function formatEdgeDetails(edge) {
    if (!edge) return '';

    let html = '';

    // Show edge name at the top if available
    if (edge.name) {
        html += `<p><strong>Name:</strong> ${escapeHTML(edge.name)}</p>`;
    }

    if (edge.type) {
        html += `<p><strong>Type:</strong> ${escapeHTML(edge.type)}</p>`;
    }

    // Show source and target
    const sourceNode = typeof edge.source === 'object' ? edge.source :
        (window.SchGraphApp.state.currentGraph?.nodes.find(n => n.name === edge.source) || {name: edge.source});
    const targetNode = typeof edge.target === 'object' ? edge.target :
        (window.SchGraphApp.state.currentGraph?.nodes.find(n => n.name === edge.target) || {name: edge.target});

    html += `<p><strong>Src:</strong> ${escapeHTML(sourceNode.name)}</p>`;
    html += `<p><strong>Dst:</strong> ${escapeHTML(targetNode.name)}</p>`;

    // Show all labels from the dictionary
    if (edge.labels && Object.keys(edge.labels).length > 0) {
        for (const [key, value] of Object.entries(edge.labels)) {
            html += `<p><strong>${escapeHTML(key)}:</strong> ${escapeHTML(value)}</p>`;
        }
    }

    // Add description if available
    if (edge.description) {
        html += `
            <hr>
            <h6>Description</h6>
            <div class="node-description">${escapeHTML(edge.description)}</div>
        `;
    }

    return html;
}

// Determine if text should be black or white based on background color
function getTextColor(bgColor) {
    // If no color provided, default to white
    if (!bgColor) return "#ffffff";

    // Remove the '#' if it exists
    const color = bgColor.startsWith('#') ? bgColor.substring(1) : bgColor;

    // Handle 3-digit hex codes by expanding to 6 digits
    const normalizedColor = color.length === 3
        ? color[0] + color[0] + color[1] + color[1] + color[2] + color[2]
        : color;

    // Convert to RGB - fixed substring parameters
    const r = parseInt(normalizedColor.substring(0, 2), 16);
    const g = parseInt(normalizedColor.substring(2, 4), 16);
    const b = parseInt(normalizedColor.substring(4, 6), 16);

    // Calculate relative luminance (perceived brightness)
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

    // Use white text for dark backgrounds, black text for light backgrounds
    return luminance > 0.5 ? "#000000" : "#ffffff";
}

function getNodeTextColor(node) {
    const nodeColor = node.color || "#999";
    return getTextColor(nodeColor);
}

function getEdgeTextColor(edge) {
    const edgeColor = edge.color || "#999";
    return getTextColor(edgeColor);
}


function exportGraphAsPNG() {
    const svgElement = document.querySelector('#graph-container svg');
    if (!svgElement) {
        console.error('SVG element not found');
        return;
    }

    // Create a copy of the SVG to avoid modifying the original
    const svgClone = svgElement.cloneNode(true);

    // Make sure all SVG elements have explicit styling
    // This ensures that CSS styles are included in the exported image
    const lines = svgClone.querySelectorAll('.link');
    lines.forEach(line => {
        // Explicitly set stroke attributes that might be in CSS
        if (!line.getAttribute('stroke')) {
            line.setAttribute('stroke', '#999');
        }
        if (!line.getAttribute('stroke-width')) {
            line.setAttribute('stroke-width', '2');
        }
        if (!line.getAttribute('stroke-opacity')) {
            line.setAttribute('stroke-opacity', '0.6');
        }
    });

    // Set explicit dimensions on the SVG
    const width = svgElement.clientWidth || svgElement.parentElement.clientWidth;
    const height = svgElement.clientHeight || svgElement.parentElement.clientHeight;
    svgClone.setAttribute('width', width);
    svgClone.setAttribute('height', height);

    // You might need to include namespaces for proper rendering
    svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    svgClone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');

    // Get SVG data with proper encoding
    const svgData = new XMLSerializer().serializeToString(svgClone);
    const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
    const url = URL.createObjectURL(svgBlob);

    // Create canvas with appropriate dimensions
    const canvas = document.createElement('canvas');
    // Use a slightly higher resolution for better quality
    const scale = 2; // 2x scaling for better resolution
    canvas.width = width * scale;
    canvas.height = height * scale;

    const context = canvas.getContext('2d');
    context.fillStyle = '#f9f9f9'; // Match background color
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.scale(scale, scale); // Scale up for better resolution

    // Create image and draw to canvas
    const img = new Image();
    img.onload = () => {
        // Draw the image
        context.drawImage(img, 0, 0);
        URL.revokeObjectURL(url);

        // Download the image
        const a = document.createElement('a');
        a.download = 'graph-visualization.png';

        // Use custom filename if graph has a title
        if (window.SchGraphApp && window.SchGraphApp.state &&
            window.SchGraphApp.state.currentGraph &&
            window.SchGraphApp.state.currentGraph.title) {
            a.download = `${window.SchGraphApp.state.currentGraph.title.toLowerCase().replace(/\s+/g, '-')}.png`;
        }

        a.href = canvas.toDataURL('image/png');
        document.body.appendChild(a);
        a.click();

        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
        }, 100);
    };

    // Set cross-origin = anonymous to avoid tainted canvas issues
    img.crossOrigin = 'Anonymous';
    img.src = url;

    // Add error handling
    img.onerror = (error) => {
        console.error('Error creating export:', error);
        URL.revokeObjectURL(url);
    };
}

// Make sure the function is attached to the app namespace
document.addEventListener('DOMContentLoaded', function() {
    window.SchGraphApp = window.SchGraphApp || {};
    window.SchGraphApp.utils = window.SchGraphApp.utils || {};
    window.SchGraphApp.utils.formatNodeDetails = formatNodeDetails;
    window.SchGraphApp.utils.formatEdgeDetails = formatEdgeDetails;
    window.SchGraphApp.utils.exportGraphAsPNG = exportGraphAsPNG;
    window.SchGraphApp.utils.escapeHTML = escapeHTML;
    window.SchGraphApp.utils.getTextColor = getTextColor;
    window.SchGraphApp.utils.getNodeTextColor = getNodeTextColor;
    window.SchGraphApp.utils.getEdgeTextColor = getEdgeTextColor;
});