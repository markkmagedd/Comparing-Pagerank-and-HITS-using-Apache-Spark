document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyzer-form');
    const runBtn = document.getElementById('run-btn');
    const resetBtn = document.getElementById('reset-controls');
    const loader = document.getElementById('loader');
    const vizLoading = document.getElementById('viz-loading');
    const emptyState = document.getElementById('empty-state');
    const leagueSelect = document.getElementById('league');
    const weightModeSelect = document.getElementById('weight-mode');
    const algorithmSelect = document.getElementById('algorithm');
    const directionSelect = document.getElementById('direction');
    const iterationsInput = document.getElementById('iterations');
    const dampingInput = document.getElementById('damping');
    
    const statusText = document.querySelector('.status-text');
    const statusIndicator = document.getElementById('status-indicator');
    const nodeName = document.getElementById('node-name');
    const nodeRank = document.getElementById('node-rank');
    const overlay = document.getElementById('graph-overlay');
    const cyContainer = document.getElementById('cy-container');
    const chartContainer = document.getElementById('chart-container');
    const vizBtns = document.querySelectorAll('.viz-toggle-btn');
    const seasonRangeMeta = document.getElementById('season-range-meta');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const chordContainer = document.getElementById('chord-container');
    const chordSeasonMeta = document.getElementById('chord-season-meta');

    // Transfer Popup Elements
    const transferPopup = document.getElementById('transfer-popup');
    const popupClubName = document.getElementById('popup-club-name');
    const popupLoading = document.getElementById('popup-loading');
    const popupEmpty = document.getElementById('popup-empty');
    const popupList = document.getElementById('popup-list');
    const closePopupBtn = document.getElementById('close-popup');

    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        sidebarToggle.classList.toggle('active');
        mainContent.classList.toggle('expanded');
        
        // Trigger cytoscape resize if it exists
        if (cy) {
            setTimeout(() => cy.resize(), 400);
        }
    });

    closePopupBtn.addEventListener('click', () => {
        transferPopup.classList.add('hidden');
    });
    
    let cy = null;
    let charts = {
        main: null,
        right: null
    };
    let lastResult = null;
    let lastResultRight = null; // For compare mode
    let lastChordResult = null;
    let currentViz = 'chart'; // default
    let isCompareModeActive = false;
    let isChordModeActive = false;
    let debounceTimer = null;

    const SEASONS = [
        "2000-2001", "2001-2002", "2002-2003", "2003-2004", "2004-2005",
        "2005-2006", "2006-2007", "2007-2008", "2008-2009", "2009-2010",
        "2010-2011", "2011-2012", "2012-2013", "2013-2014", "2014-2015",
        "2015-2016", "2016-2017", "2017-2018", "2018-2019"
    ];

    const startSeasonSelect = document.getElementById('start-season');
    const endSeasonSelect = document.getElementById('end-season');

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

    const fetchTransferDetails = async (clubName) => {
        popupClubName.textContent = clubName;
        popupLoading.classList.remove('hidden');
        popupEmpty.classList.add('hidden');
        popupList.innerHTML = '';
        transferPopup.classList.remove('hidden');

        const params = new URLSearchParams({
            league: leagueSelect.value,
            weight_mode: weightModeSelect.value,
            start_season: startSeasonSelect.value,
            end_season: endSeasonSelect.value,
            top_n: 10
        });

        try {
            const response = await fetch(`/api/transfers/${encodeURIComponent(clubName)}?${params.toString()}`);
            if (!response.ok) throw new Error('Failed to fetch transfers');
            const data = await response.json();
            
            popupLoading.classList.add('hidden');
            
            if (!data.transfers || data.transfers.length === 0) {
                popupEmpty.classList.remove('hidden');
            } else {
                renderTransferItems(data.transfers);
            }
        } catch (error) {
            console.error(error);
            popupLoading.classList.add('hidden');
            popupEmpty.textContent = "Error loading details.";
            popupEmpty.classList.remove('hidden');
        }
    };

    const renderTransferItems = (transfers) => {
        popupList.innerHTML = '';
        transfers.forEach(t => {
            const li = document.createElement('li');
            li.className = 'transfer-item';
            
            const feeFormatted = t.fee >= 1000000 
                ? `€${(t.fee / 1000000).toFixed(1)}M` 
                : `€${(t.fee / 1000).toFixed(0)}K`;

            li.innerHTML = `
                <div class="player-name">${t.player_name}</div>
                <div class="transfer-meta">
                    <span class="transfer-fee">${feeFormatted}</span>
                    <span class="transfer-dir ${t.direction === 'in' ? 'dir-in' : 'dir-out'}">${t.direction === 'in' ? 'Bought' : 'Sold'}</span>
                </div>
                <div class="transfer-counterparty">
                    ${t.direction === 'in' ? 'from' : 'to'} <strong>${t.counterparty_club}</strong>
                </div>
            `;
            popupList.appendChild(li);
        });
    };

    const updateAlgorithmUI = () => {
        const algo = algorithmSelect.value;
        const isHits = algo === 'hits';
        
        // Damping factor is for PageRank, not HITS
        dampingInput.disabled = isHits;
        const dampingGroup = dampingInput.closest('.form-group');
        if (isHits) {
            dampingGroup.classList.add('disabled');
            dampingInput.title = "Not applicable to HITS algorithm";
        } else {
            dampingGroup.classList.remove('disabled');
            dampingInput.title = "";
        }
        
        // Update direction labels based on algorithm terminology
        const buyersOpt = directionSelect.querySelector('option[value="buyers"]');
        const sellersOpt = directionSelect.querySelector('option[value="sellers"]');
        
        if (isHits) {
            buyersOpt.textContent = "Authority (Buyers)";
            sellersOpt.textContent = "Hub (Sellers)";
        } else {
            buyersOpt.textContent = "Attractors (Buyers)";
            sellersOpt.textContent = "Suppliers (Sellers)";
        }
    };

    const calculateOverlap = (resPR, resHITS) => {
        const prIds = new Set(resPR.nodes.map(n => n.data.id));
        const hitsIds = new Set(resHITS.nodes.map(n => n.data.id));
        
        const intersection = new Set([...prIds].filter(id => hitsIds.has(id)));
        const totalN = document.getElementById('top_n').value;
        const actualMax = Math.max(prIds.size, hitsIds.size);
        
        return {
            overlapSet: intersection,
            overlapCount: intersection.size,
            totalN: Math.min(totalN, actualMax)
        };
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
                        'background-color': '#111827',
                        'background-image': (ele) => {
                            const name = ele.data('id');
                            // Now pointing to our own smart proxy
                            return `/logo/${encodeURIComponent(name)}`;
                        },
                        'background-fit': 'cover',
                        'background-image-opacity': 1,
                        'label': (ele) => {
                            const score = ele.data('rank').toFixed(4);
                            const scoreType = lastResult.meta ? lastResult.meta.score_type : 'pagerank';
                            let prefix = "Rank:";
                            if (scoreType === 'authority') prefix = "Auth:";
                            if (scoreType === 'hub') prefix = "Hub:";
                            return `${ele.data('id')}\n${prefix} ${score}`;
                        },
                        'color': '#f1f5f9',
                        'font-family': 'Inter',
                        'font-size': '14px',
                        'font-weight': 'bold',
                        'text-valign': 'bottom',
                        'text-halign': 'center',
                        'text-margin-y': 8,
                        'text-wrap': 'wrap',
                        'text-outline-width': 2,
                        'text-outline-color': '#111827',
                        'width': 'mapData(rank, 0, 0.1, 60, 150)',
                        'height': 'mapData(rank, 0, 0.1, 60, 150)',
                        'border-width': 2,
                        'border-color': '#3b82f6',
                        'cursor': 'pointer'
                    }
                },
                {
                    selector: 'node:hover',
                    style: {
                        'border-width': 4,
                        'border-color': '#60a5fa',
                        'shadow-blur': 15,
                        'shadow-color': '#3b82f6',
                        'shadow-opacity': 0.8
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 'mapData(weight, 0, 500000000, 1, 10)',
                        'line-color': '#ffffff',
                        'target-arrow-color': '#ffffff',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'opacity': 0.4,
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
                nodeRepulsion: 800000,
                gravity: 40
            }
        });

        cy.on('tap click', 'node', (evt) => {
            const data = evt.target.data();
            showOverlay(data);
            fetchTransferDetails(data.id);
        });
        
        cy.on('tap', 'edge', (evt) => {
            showOverlay({
                id: `${evt.target.data('source')} → ${evt.target.data('target')}`,
                rank: 0,
                weight_label: evt.target.data('weight_label')
            });
        });

        cy.on('tap', (evt) => {
            if (evt.target === cy) {
                overlay.classList.add('hidden');
                transferPopup.classList.add('hidden');
            }
        });
    };

    const renderBarChart = (result, canvasId = 'rankChart', overlapSet = null) => {
        const data = result;
        const meta = result.meta || {};
        const chartKey = canvasId === 'rankChart' ? 'main' : 'right';
        
        // Cleanup existing for this specific canvas
        if (charts[chartKey]) charts[chartKey].destroy();
        
        cyContainer.classList.add('hidden');
        chartContainer.classList.remove('hidden');

        const nodes = [...data.nodes].sort((a, b) => b.data.rank - a.data.rank);
        const labels = nodes.map(n => n.data.id);
        const ranks = nodes.map(n => n.data.rank);

        const weightDesc = meta.weight_mode === 'count' ? 'Transfer Count' : 'Transfer Fee';
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        const scoreTypeMap = {
            'pagerank': 'PageRank Score',
            'authority': 'Authority Score',
            'hub': 'Hub Score'
        };
        const scoreLabel = scoreTypeMap[meta.score_type] || 'Score';

        charts[chartKey] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: `${scoreLabel} (${weightDesc})`,
                    data: ranks,
                    backgroundColor: nodes.map(n => 
                        overlapSet && overlapSet.has(n.data.id) ? 'rgba(255, 215, 0, 0.6)' : 'rgba(59, 130, 246, 0.8)'
                    ),
                    borderColor: nodes.map(n => 
                        overlapSet && overlapSet.has(n.data.id) ? '#ffd700' : '#3b82f6'
                    ),
                    borderWidth: 2,
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
                        const data = nodes[index].data;
                        showOverlay(data);
                        fetchTransferDetails(data.id);
                    } else {
                        overlay.classList.add('hidden');
                        transferPopup.classList.add('hidden');
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
        isCompareModeActive = (type === 'compare');
        isSankeyModeActive = (type === 'sankey');
        isChordModeActive = (type === 'chord');
        
        vizBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.viz === type);
        });

        const panelRight = document.getElementById('chart-panel-right');
        const labelLeft = document.getElementById('chart-label-left');
        
        // Hide all major containers
        cyContainer.classList.add('hidden');
        chartContainer.classList.add('hidden');
        chordContainer.classList.add('hidden');
        overlay.classList.add('hidden');

        if (isCompareModeActive) {
            chartContainer.classList.add('compare-mode-active');
            panelRight.classList.remove('hidden');
            labelLeft.classList.remove('hidden');
            chartContainer.classList.remove('hidden');
            
            algorithmSelect.disabled = true;
            algorithmSelect.closest('.form-group').classList.add('disabled');
            dampingInput.disabled = false;
            dampingInput.closest('.form-group').classList.remove('disabled');
        } else if (isChordModeActive) {
            chordContainer.classList.remove('hidden');
            algorithmSelect.disabled = true;
            algorithmSelect.closest('.form-group').classList.add('disabled');
            directionSelect.disabled = true;
            directionSelect.closest('.form-group').classList.add('disabled');
        } else {
            chartContainer.classList.remove('compare-mode-active');
            panelRight.classList.add('hidden');
            labelLeft.classList.add('hidden');
            
            algorithmSelect.disabled = false;
            algorithmSelect.closest('.form-group').classList.remove('disabled');
            directionSelect.disabled = false;
            directionSelect.closest('.form-group').classList.remove('disabled');
            updateAlgorithmUI();
        }

        if (isChordModeActive && lastChordResult) {
            renderChord(lastChordResult);
        } else if (lastResult) {
            if (isCompareModeActive) {
                renderBarChart(lastResult, 'rankChart');
                renderBarChart(lastResultRight, 'rankChartRight');
            } else if (type === 'chart') {
                chartContainer.classList.remove('hidden');
                renderBarChart(lastResult);
            } else if (type === 'network') {
                cyContainer.classList.remove('hidden');
                renderNetwork(lastResult);
            }
        } else {
            triggerAnalysis(false);
        }
    };

    const triggerAnalysis = async (isManual = false) => {
        const isChordModeActive = currentViz === 'chord';
        const payload = {
            direction: directionSelect.value,
            iterations: parseInt(iterationsInput.value),
            damping_factor: parseFloat(dampingInput.value),
            top_n: 10,
            league: leagueSelect.value,
            weight_mode: weightModeSelect.value,
            algorithm: algorithmSelect.value,
            start_season: startSeasonSelect.value,
            end_season: endSeasonSelect.value
        };

        // UI Feedback
        if (isManual) {
            loader.classList.remove('hidden');
        } else {
            vizLoading.classList.remove('hidden');
        }
        
        runBtn.disabled = true;
        
        statusText.textContent = "Processing...";
        statusIndicator.classList.add('status-loading');
        overlay.classList.add('hidden');
        emptyState.classList.add('hidden');

        try {
            if (isChordModeActive) {
                const response = await fetch('/api/league-flow', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                lastChordResult = await response.json();
                renderChord(lastChordResult);
            } else if (isCompareModeActive) {
                const payloadPR = { ...payload, algorithm: 'pagerank' };
                const payloadHITS = { ...payload, algorithm: 'hits' };
                
                const [resPR, resHITS] = await Promise.all([
                    fetch('/api/pagerank', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payloadPR)
                    }).then(r => r.json()),
                    fetch('/api/pagerank', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payloadHITS)
                    }).then(r => r.json())
                ]);

                lastResult = resPR;
                lastResultRight = resHITS;

                const summaryDiv = document.getElementById('overlap-summary');

                if (resPR.meta?.empty && resHITS.meta?.empty) {
                    chartContainer.classList.add('hidden');
                    emptyState.classList.remove('hidden');
                    summaryDiv.classList.add('hidden');
                } else {
                    const { overlapSet, overlapCount, totalN } = calculateOverlap(resPR, resHITS);
                    
                    summaryDiv.textContent = `${overlapCount} of ${totalN} clubs appear in both rankings`;
                    summaryDiv.classList.remove('hidden');

                    if (resPR.meta?.season_range) {
                        seasonRangeMeta.textContent = resPR.meta.season_range;
                        seasonRangeMeta.classList.remove('hidden');
                    }

                    renderBarChart(resPR, 'rankChart', overlapSet);
                    renderBarChart(resHITS, 'rankChartRight', overlapSet);
                }
            } else {
                const response = await fetch('/api/pagerank', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) throw new Error('Algorithm computation failed');

                lastResult = await response.json();
                
                document.getElementById('overlap-summary').classList.add('hidden');

                if (lastResult.meta && lastResult.meta.season_range) {
                    seasonRangeMeta.textContent = lastResult.meta.season_range;
                    seasonRangeMeta.classList.remove('hidden');
                } else {
                    seasonRangeMeta.classList.add('hidden');
                }

                if (lastResult.meta && lastResult.meta.empty) {
                    cyContainer.classList.add('hidden');
                    chartContainer.classList.add('hidden');
                    emptyState.classList.remove('hidden');
                } else {
                    switchVisualization(currentViz);
                }
            }
            
            statusText.textContent = "Ready";
        } catch (error) {
            console.error(error);
            alert("Error running algorithm. Check console for details.");
            statusText.textContent = "Error";
        } finally {
            loader.classList.add('hidden');
            vizLoading.classList.add('hidden');
            runBtn.disabled = false;
            leagueSelect.disabled = false;
            weightModeSelect.disabled = false;
            algorithmSelect.disabled = false;
            statusIndicator.classList.remove('status-loading');
        }
    };

    const debounceAnalysis = (ms = 300) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => triggerAnalysis(false), ms);
    };

    vizBtns.forEach(btn => {
        btn.addEventListener('click', () => switchVisualization(btn.dataset.viz));
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        triggerAnalysis(true);
    });
    
    leagueSelect.addEventListener('change', () => debounceAnalysis(300));
    weightModeSelect.addEventListener('change', () => debounceAnalysis(300));
    directionSelect.addEventListener('change', () => debounceAnalysis(300));
    
    iterationsInput.addEventListener('input', () => debounceAnalysis(500));
    dampingInput.addEventListener('input', () => debounceAnalysis(500));
    algorithmSelect.addEventListener('change', () => {
        updateAlgorithmUI();
        debounceAnalysis(300);
    });

    const validateSeasonRange = () => {
        const startVal = startSeasonSelect.value;
        const endVal = endSeasonSelect.value;

        if (startVal === 'all' || endVal === 'all') {
            // Re-enable everything if either is 'all'
            Array.from(startSeasonSelect.options).forEach(opt => opt.disabled = false);
            Array.from(endSeasonSelect.options).forEach(opt => opt.disabled = false);
            return;
        }

        const startIndex = SEASONS.indexOf(startVal);
        const endIndex = SEASONS.indexOf(endVal);

        // Disable options in End dropdown that are BEFORE the Start season
        Array.from(endSeasonSelect.options).forEach(opt => {
            if (opt.value === 'all') return;
            const idx = SEASONS.indexOf(opt.value);
            opt.disabled = idx < startIndex;
        });

        // Disable options in Start dropdown that are AFTER the End season
        Array.from(startSeasonSelect.options).forEach(opt => {
            if (opt.value === 'all') return;
            const idx = SEASONS.indexOf(opt.value);
            opt.disabled = idx > endIndex;
        });
    };

    startSeasonSelect.addEventListener('change', () => {
        validateSeasonRange();
        debounceAnalysis(300);
    });

    endSeasonSelect.addEventListener('change', () => {
        validateSeasonRange();
        debounceAnalysis(300);
    });
    
    resetBtn.addEventListener('click', () => {
        algorithmSelect.value = 'pagerank';
        directionSelect.value = 'buyers';
        leagueSelect.value = 'all';
        weightModeSelect.value = 'fee';
        startSeasonSelect.value = 'all';
        endSeasonSelect.value = 'all';
        iterationsInput.value = 10;
        dampingInput.value = 0.85;
        validateSeasonRange();
        updateAlgorithmUI();
        triggerAnalysis(true);
    });

    // Close overlays on background click
    window.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.add('hidden');
        }
    });

    // Initial load
    loadLeagues();
    updateAlgorithmUI();
    triggerAnalysis(true);

    const renderChord = (res) => {
        if (!res || !res.flows) return;
        
        chordContainer.classList.remove('hidden');
        chordSeasonMeta.textContent = res.meta?.season_range || "All Seasons";

        const wrapper = document.getElementById('chord-wrapper');
        wrapper.innerHTML = ''; // Clear previous

        const width = 800;
        const height = 800;
        const outerRadius = Math.min(width, height) * 0.45 - 60;
        const innerRadius = outerRadius - 20;

        // 1. Prepare Matrix
        const leagues = Array.from(new Set(res.flows.flatMap(f => [f.from, f.to]))).sort();
        const indexByName = new Map(leagues.map((name, i) => [name, i]));
        const matrix = Array.from({length: leagues.length}, () => Array(leagues.length).fill(0));

        for (const {from, to, flow} of res.flows) {
            matrix[indexByName.get(from)][indexByName.get(to)] += flow;
        }

        const chord = d3.chord()
            .padAngle(0.05)
            .sortSubgroups(d3.descending);

        const arc = d3.arc()
            .innerRadius(innerRadius)
            .outerRadius(outerRadius);

        const ribbon = d3.ribbon()
            .radius(innerRadius);

        const svg = d3.select("#chord-wrapper").append("svg")
            .attr("viewBox", [-width / 2, -height / 2, width, height])
            .attr("width", width)
            .attr("height", height)
            .attr("style", "max-width: 100%; height: auto;");

        const chords = chord(matrix);

        const colors = {
            "Premier League": "#38bdf8",
            "LaLiga": "#f43f5e",
            "Serie A": "#10b981",
            "Bundesliga": "#f59e0b",
            "Ligue 1": "#8b5cf6",
            "Eredivisie": "#ec4899",
            "Liga NOS": "#06b6d4",
            "Other": "#475569"
        };
        const colorScale = (name) => colors[name] || "#94a3b8";

        const group = svg.append("g")
            .selectAll("g")
            .data(chords.groups)
            .join("g");

        group.append("path")
            .attr("fill", d => colorScale(leagues[d.index]))
            .attr("stroke", d => d3.rgb(colorScale(leagues[d.index])).darker())
            .attr("d", arc)
            .append("title")
            .text(d => `${leagues[d.index]}\nTotal: ${res.meta.weight_mode === 'fee' ? '€'+(d.value/1e6).toFixed(1)+'M' : Math.round(d.value)+' deals'}`);

        group.append("text")
            .each(d => { d.angle = (d.startAngle + d.endAngle) / 2; })
            .attr("dy", ".35em")
            .attr("transform", d => `
                rotate(${(d.angle * 180 / Math.PI - 90)})
                translate(${outerRadius + 10})
                ${d.angle > Math.PI ? "rotate(180)" : ""}
            `)
            .attr("text-anchor", d => d.angle > Math.PI ? "end" : "start")
            .text(d => leagues[d.index])
            .style("font-weight", "600");

        svg.append("g")
            .attr("fill-opacity", 0.6)
            .selectAll("path")
            .data(chords)
            .join("path")
            .attr("class", "chord-ribbon")
            .attr("d", ribbon)
            .attr("fill", d => colorScale(leagues[d.source.index]))
            .append("title")
            .text(d => `${leagues[d.source.index]} ➔ ${leagues[d.target.index]}: ${res.meta.weight_mode === 'fee' ? '€'+(d.source.value/1e6).toFixed(1)+'M' : Math.round(d.source.value)+' deals'}`);
            
        // Hover effects
        group.on("mouseover", function(event, d) {
            svg.selectAll(".chord-ribbon")
                .filter(ribbon => ribbon.source.index !== d.index && ribbon.target.index !== d.index)
                .transition()
                .duration(200)
                .style("opacity", 0.1);
        }).on("mouseout", function() {
            svg.selectAll(".chord-ribbon")
                .transition()
                .duration(200)
                .style("opacity", 0.6);
        });
    };
});
