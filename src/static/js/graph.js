document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyzer-form');
    const runBtn = document.getElementById('run-btn');
    const resetBtn = document.getElementById('reset-controls');
    const loader = document.getElementById('loader');
    const vizLoading = document.getElementById('viz-loading');
    const emptyState = document.getElementById('empty-state');
    const leagueSelect = document.getElementById('league');
    const weightModeSelect = document.getElementById('weight-mode');
    
    const statusText = document.querySelector('.status-text');
    const statusIndicator = document.getElementById('status-indicator');
    const nodeName = document.getElementById('node-name');
    const nodeRank = document.getElementById('node-rank');
    const overlay = document.getElementById('graph-overlay');
    const cyContainer = document.getElementById('cy-container');
    const chartContainer = document.getElementById('chart-container');
    const vizBtns = document.querySelectorAll('.viz-toggle-btn');
    
    let cy = null;
    let chart = null;
    let lastResult = null;
    let currentViz = 'chart'; // default
    let debounceTimer = null;

    // Register Chart.js DataLabels plugin globally
    Chart.register(ChartDataLabels);

    const showOverlay = (data) => {
        nodeName.textContent = data.id;
        nodeRank.textContent = data.rank.toFixed(4);
        
        // Show edge info if available (for Cytoscape edges)
        if (data.weight_label) {
            const labelP = document.createElement('p');
            labelP.className = 'edge-weight-info';
            labelP.textContent = `Weight: ${data.weight_label}`;
            // Remove existing weight info if any
            const existing = overlay.querySelector('.edge-weight-info');
            if (existing) existing.remove();
            overlay.querySelector('.node-info').appendChild(labelP);
        } else {
            const existing = overlay.querySelector('.edge-weight-info');
            if (existing) existing.remove();
        }
        
        overlay.classList.remove('hidden');
    };

    const loadLeagues = async () => {
        try {
            const response = await fetch('/api/leagues');
            if (!response.ok) throw new Error('Failed to load leagues');
            const data = await response.json();
            
            // Clear loading placeholder
            leagueSelect.innerHTML = '<option value="all">All Leagues</option>';
            
            data.leagues.forEach(league => {
                const opt = document.createElement('option');
                opt.value = league;
                opt.textContent = league;
                leagueSelect.appendChild(opt);
            });
        } catch (error) {
            console.warn('Could not load leagues:', error);
            leagueSelect.innerHTML = '<option value="all">All Leagues</option>';
        }
    };

    const renderNetwork = (result) => {
        const elements = {
            nodes: result.nodes,
            edges: result.edges
        };
        // Cleanup existing
        if (cy) cy.destroy();
        
        cyContainer.classList.remove('hidden');
        chartContainer.classList.add('hidden');

        cy = cytoscape({
            container: cyContainer,
            elements: elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#3b82f6',
                        'label': (ele) => `${ele.data('id')}\nRank: ${ele.data('rank').toFixed(4)}`,
                        'color': '#f1f5f9',
                        'font-family': 'Inter',
                        'font-size': '16px',
                        'font-weight': 'bold',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'text-wrap': 'wrap',
                        'text-outline-width': 2,
                        'text-outline-color': '#1e293b',
                        'width': 'mapData(rank, 0, 10, 100, 250)',
                        'height': 'mapData(rank, 0, 10, 100, 250)',
                        'border-width': 2,
                        'border-color': '#1e293b'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 'mapData(weight, 0, 500000000, 1, 10)',
                        'line-color': '#1e293b',
                        'target-arrow-color': '#1e293b',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'opacity': 0.6,
                        'label': 'data(weight_label)',
                        'color': '#fff',
                        'font-size': '10px',
                        'text-outline-width': 1,
                        'text-outline-color': '#000'
                    }
                },
                {
                    selector: 'node:selected',
                    style: {
                        'border-width': 4,
                        'border-color': '#f1f5f9',
                        'background-color': '#2563eb'
                    }
                }
            ],
            layout: {
                name: 'cose',
                animate: true,
                padding: 100,
                nodeRepulsion: 400000,
                gravity: 80
            }
        });

        cy.on('tap', 'node', (evt) => {
            showOverlay(evt.target.data());
        });
        
        cy.on('tap', 'edge', (evt) => {
            showOverlay({
                id: `${evt.target.data('source')} → ${evt.target.data('target')}`,
                rank: 0,
                weight_label: evt.target.data('weight_label')
            });
        });

        cy.on('tap', (evt) => {
            if (evt.target === cy) overlay.classList.add('hidden');
        });
    };

    const renderBarChart = (result) => {
        const data = result;
        const meta = result.meta || {};
        // Cleanup existing
        if (chart) chart.destroy();
        
        cyContainer.classList.add('hidden');
        chartContainer.classList.remove('hidden');

        const nodes = [...data.nodes].sort((a, b) => b.data.rank - a.data.rank);
        const labels = nodes.map(n => n.data.id);
        const ranks = nodes.map(n => n.data.rank);

        const weightDesc = meta.weight_mode === 'count' ? 'Transfer Count' : 'Transfer Fee';
        const ctx = document.getElementById('rankChart').getContext('2d');
        
        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: `PageRank Score (${weightDesc})`,
                    data: ranks,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        showOverlay(nodes[index].data);
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#f1f5f9', font: { weight: 'bold' } }
                    }
                },
                plugins: {
                    legend: { display: true, labels: { color: '#f1f5f9' } },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#f1f5f9',
                        bodyColor: '#94a3b8',
                        padding: 12,
                        cornerRadius: 8
                    },
                    datalabels: {
                        color: 'white',
                        anchor: 'center',
                        align: 'center',
                        formatter: (value) => value.toFixed(4),
                        font: {
                            weight: 'bold',
                            family: 'Inter',
                            size: 14
                        }
                    }
                }
            }
        });
    };

    const switchVisualization = (type) => {
        currentViz = type;
        vizBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.viz === type);
        });

        if (!lastResult) return;

        if (type === 'chart') {
            renderBarChart(lastResult);
        } else {
            renderNetwork(lastResult);
        }
    };

    const triggerAnalysis = async (isManual = false) => {
        const payload = {
            direction: document.getElementById('direction').value,
            iterations: parseInt(document.getElementById('iterations').value),
            damping_factor: parseFloat(document.getElementById('damping').value),
            top_n: parseInt(document.getElementById('top_n').value),
            league: leagueSelect.value,
            weight_mode: weightModeSelect.value
        };

        // UI Feedback
        if (isManual) {
            loader.classList.remove('hidden');
        } else {
            vizLoading.classList.remove('hidden');
        }
        
        runBtn.disabled = true;
        leagueSelect.disabled = true;
        weightModeSelect.disabled = true;
        
        statusText.textContent = "Processing...";
        statusIndicator.classList.add('status-loading');
        overlay.classList.add('hidden');
        emptyState.classList.add('hidden');

        try {
            const response = await fetch('/api/pagerank', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Algorithm computation failed');

            lastResult = await response.json();
            
            if (lastResult.meta && lastResult.meta.empty) {
                cyContainer.classList.add('hidden');
                chartContainer.classList.add('hidden');
                emptyState.classList.remove('hidden');
            } else {
                switchVisualization(currentViz);
            }
            
            statusText.textContent = "Ready";
        } catch (error) {
            console.error(error);
            alert("Error running PageRank algorithm. Check console for details.");
            statusText.textContent = "Error";
        } finally {
            loader.classList.add('hidden');
            vizLoading.classList.add('hidden');
            runBtn.disabled = false;
            leagueSelect.disabled = false;
            weightModeSelect.disabled = false;
            statusIndicator.classList.remove('status-loading');
        }
    };

    const debounceAnalysis = () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => triggerAnalysis(false), 300);
    };

    vizBtns.forEach(btn => {
        btn.addEventListener('click', () => switchVisualization(btn.dataset.viz));
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        triggerAnalysis(true);
    });
    
    leagueSelect.addEventListener('change', debounceAnalysis);
    weightModeSelect.addEventListener('change', debounceAnalysis);
    
    resetBtn.addEventListener('click', () => {
        leagueSelect.value = 'all';
        weightModeSelect.value = 'fee';
        triggerAnalysis(true);
    });

    // Close overlay on background click
    window.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.classList.add('hidden');
    });

    // Initial load
    loadLeagues();
});
