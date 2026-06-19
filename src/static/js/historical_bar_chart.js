// ─────────────────────────────────────────────────────────────
// historical_bar_chart.js  —  Premium D3 bar-chart race engine
// ─────────────────────────────────────────────────────────────

(function () {
    "use strict";

    // ── Colour palette (one colour sticks to a club for the entire race) ──
    const PALETTE = [
        "#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6",
        "#ec4899", "#06b6d4", "#f97316", "#14b8a6", "#a855f7",
        "#e11d48", "#0ea5e9", "#84cc16", "#f472b6", "#22d3ee",
    ];
    const clubColorMap = new Map();
    let colorIndex = 0;
    function clubColor(name) {
        if (!clubColorMap.has(name)) {
            clubColorMap.set(name, PALETTE[colorIndex % PALETTE.length]);
            colorIndex++;
        }
        return clubColorMap.get(name);
    }

    // ── Layout ──
    const barHeight = 48;
    const barGap = 6;
    const N = 10;
    const margin = { top: 24, right: 120, bottom: 12, left: 14 };
    const chartHeight = N * (barHeight + barGap) + margin.top + margin.bottom;
    const svgWidth = 960;
    const container = document.getElementById("chart-area");

    const svg = d3.select(container)
        .append("svg")
        .attr("viewBox", `0 0 ${svgWidth} ${chartHeight}`)
        .attr("preserveAspectRatio", "xMidYMid meet")
        .style("width", "100%")
        .style("height", `${chartHeight}px`);

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const innerW = svgWidth - margin.left - margin.right;
    const innerH = chartHeight - margin.top - margin.bottom;

    const xScale = d3.scaleLinear().range([0, innerW]);
    const yScale = d3.scaleBand()
        .range([0, innerH])
        .paddingInner(0.12)
        .paddingOuter(0.08);

    // ── State ──
    let timelines = { pagerank: null, hits: null };
    let timeline = [];
    let yearIdx = 0;
    let playing = false;
    let duration = 2200;
    let animTimer = null;
    let currentSeason = null;

    // ── DOM handles ──
    const btnPlay       = document.getElementById("start-btn");
    const btnPlayLabel  = btnPlay.querySelector("span");
    const btnPlayIcon   = btnPlay.querySelector("svg");
    const speedSel      = document.getElementById("speed-select");
    const algoSel       = document.getElementById("algo-select");
    const yearSel       = document.getElementById("year-select");
    const seasonBadge   = document.getElementById("season-badge");
    const yearWatermark = document.getElementById("year-watermark");
    const algoWatermark = document.getElementById("algo-watermark");
    const progressFill  = document.getElementById("progress-fill");
    const loadingOverlay = document.getElementById("loading-overlay");

    // Transfer popup
    const popup       = document.getElementById("transfer-popup");
    const popupName   = document.getElementById("popup-club-name");
    const popupLoad   = document.getElementById("popup-loading");
    const popupEmpty  = document.getElementById("popup-empty");
    const popupList   = document.getElementById("popup-list");
    const popupClose  = document.getElementById("close-popup");

    // ── Icons ──
    const ICON_PLAY  = '<polygon points="5,3 19,12 5,21"/>';
    const ICON_PAUSE = '<rect x="5" y="3" width="4" height="18"/><rect x="15" y="3" width="4" height="18"/>';

    // ── Progress bar helpers ──
    const loadingPercent = document.getElementById("loading-percent");
    const loadingBarFill = document.getElementById("loading-bar-fill");
    const loadingLabel   = document.getElementById("loading-text");

    let currentProgress = 0;
    let loadAnimFrame = null;
    let loadStartTime = 0;
    let dataReceived = false;
    // Expected load time in ms — starts at 12s, then learns from real measurements
    let expectedDuration = 12000;

    function setProgress(pct, label) {
        currentProgress = Math.min(100, pct);
        const rounded = Math.round(currentProgress);
        loadingPercent.innerHTML = `${rounded}<span class="pct-sign">%</span>`;
        loadingBarFill.style.width = `${currentProgress}%`;
        if (label) loadingLabel.textContent = label;
    }

    function formatTimeEstimate(ms) {
        const secs = Math.max(1, Math.ceil(ms / 1000));
        if (secs >= 60) {
            const m = Math.floor(secs / 60);
            const s = secs % 60;
            return s > 0 ? `~${m}m ${s}s remaining` : `~${m}m remaining`;
        }
        return `~${secs}s remaining`;
    }

    let forcePhaseText = null;

    function getPhaseLabel(pct) {
        if (forcePhaseText) return forcePhaseText;
        if (pct < 15) return "Initializing Spark engine";
        if (pct < 35) return "Loading transfer dataset";
        if (pct < 60) return "Building season graphs";
        if (pct < 80) return "Computing yearly rankings";
        if (pct < 95) return "Finalizing results";
        return "Almost done";
    }

    function startSmoothProgress() {
        dataReceived = false;
        currentProgress = 0;
        loadStartTime = performance.now();
        setProgress(0, "Initializing Spark engine — estimating time…");

        function tick() {
            const elapsed = performance.now() - loadStartTime;

            if (dataReceived) {
                // Data arrived — race smoothly to 100%
                currentProgress += (100 - currentProgress) * 0.18;
                if (currentProgress >= 99.5) {
                    setProgress(100, "Done!");
                    return; // stop the loop, finishProgress callback handles the rest
                }
                setProgress(currentProgress, "Done!");
                loadAnimFrame = requestAnimationFrame(tick);
                return;
            }

            // Smooth asymptotic curve: approaches 95% over expectedDuration
            // Formula: progress = 95 * (1 - e^(-2.5 * t / expected))
            const ratio = elapsed / expectedDuration;
            const target = 95 * (1 - Math.exp(-2.5 * ratio));
            // Ease toward target smoothly
            currentProgress += (target - currentProgress) * 0.08;

            const phase = getPhaseLabel(currentProgress);
            const estimatedRemaining = Math.max(0, expectedDuration - elapsed);
            const timeStr = formatTimeEstimate(estimatedRemaining);
            setProgress(currentProgress, `${phase} — ${timeStr}`);

            loadAnimFrame = requestAnimationFrame(tick);
        }

        loadAnimFrame = requestAnimationFrame(tick);
    }

    function stopProgressLoop() {
        if (loadAnimFrame) {
            cancelAnimationFrame(loadAnimFrame);
            loadAnimFrame = null;
        }
    }

    function finishProgress(cb) {
        const elapsed = performance.now() - loadStartTime;
        // Learn from this load: blend toward actual duration for next time
        expectedDuration = Math.round(expectedDuration * 0.4 + elapsed * 0.6);
        dataReceived = true;
        // Let the tick() loop race to 100%, then fire callback
        setTimeout(() => {
            stopProgressLoop();
            setProgress(100, "Done!");
            setTimeout(cb, 350);
        }, 500);
    }

    // ── Fetch timeline data ──
    async function preloadAllData() {
        stopProgressLoop();
        expectedDuration = 24000; // Double expected time for 2 algorithms
        startSmoothProgress();
        loadingOverlay.classList.remove("is-hidden");
        
        try {
            // Fetch PageRank
            forcePhaseText = "Computing PageRank models (1/2)";
            const resPR = await fetch("/api/rankings/historical?algorithm=pagerank&top_n=" + N, { cache: "no-store" });
            const jsonPR = await resPR.json();
            
            // Fetch HITS
            forcePhaseText = "Computing HITS Authority models (2/2)";
            const resHITS = await fetch("/api/rankings/historical?algorithm=hits&top_n=" + N, { cache: "no-store" });
            const jsonHITS = await resHITS.json();
            
            forcePhaseText = "Finalizing results";
            
            if (jsonPR.status === "success" && jsonHITS.status === "success" && 
                jsonPR.data.timeline.length && jsonHITS.data.timeline.length) {
                
                timelines.pagerank = jsonPR.data.timeline;
                timelines.hits = jsonHITS.data.timeline;
                
                // Pre-assign colors for ALL clubs across ALL years so they're stable
                [timelines.pagerank, timelines.hits].forEach(tl => {
                    tl.forEach(frame => {
                        frame.clubs.forEach(c => clubColor(c.club_name));
                    });
                });

                const algo = algoSel ? algoSel.value : "pagerank";
                timeline = timelines[algo];

                if (yearSel) {
                    yearSel.innerHTML = "";
                    timeline.forEach((frame, i) => {
                        const opt = document.createElement("option");
                        opt.value = i;
                        opt.textContent = frame.season;
                        yearSel.appendChild(opt);
                    });
                    yearSel.value = 0;
                }

                finishProgress(() => {
                    loadingOverlay.classList.add("is-hidden");
                    renderFrame(timeline[0], false);
                    updateProgress();
                    // Automatically start playing when data is loaded
                    if (!playing) play();
                });
            } else {
                stopProgressLoop();
                setProgress(100, "No data available.");
            }
        } catch (e) {
            console.error("Fetch failed:", e);
            stopProgressLoop();
            setProgress(0, "Error — please refresh.");
        }
    }

    // ── Render a single frame using the modern .join() pattern ──
    function renderFrame(frame, animate = true) {
        const clubs = frame.clubs.slice(0, N);
        currentSeason = frame.season;

        // Update displays
        seasonBadge.textContent = currentSeason;
        yearWatermark.textContent = currentSeason;
        if (yearSel && yearSel.value !== String(yearIdx)) {
            yearSel.value = yearIdx;
        }
        
        if (algoWatermark && algoSel) {
            algoWatermark.textContent = algoSel.options[algoSel.selectedIndex].text;
        }

        // Scales
        const maxScore = d3.max(clubs, d => d.score) || 0.01;
        xScale.domain([0, maxScore * 1.08]);
        yScale.domain(clubs.map(d => d.club_name));

        const dur = animate ? duration : 0;
        const ease = d3.easeCubicInOut;

        // ── BARS ──
        g.selectAll(".race-bar")
            .data(clubs, d => d.club_name)
            .join(
                enter => enter.append("rect")
                    .attr("class", "race-bar")
                    .attr("x", 0)
                    .attr("y", d => yScale(d.club_name))
                    .attr("height", yScale.bandwidth())
                    .attr("width", 0)
                    .attr("rx", 6).attr("ry", 6)
                    .attr("fill", d => clubColor(d.club_name))
                    .attr("opacity", 0)
                    .style("cursor", "pointer")
                    .on("click", (ev, d) => showTransfers(d.club_name, currentSeason))
                    .call(el => el.transition().duration(dur).ease(ease)
                        .attr("y", d => yScale(d.club_name))
                        .attr("width", d => Math.max(0, xScale(d.score)))
                        .attr("opacity", 1)),
                update => update
                    .call(el => el.transition().duration(dur).ease(ease)
                        .attr("y", d => yScale(d.club_name))
                        .attr("height", yScale.bandwidth())
                        .attr("width", d => Math.max(0, xScale(d.score)))
                        .attr("fill", d => clubColor(d.club_name))),
                exit => exit
                    .call(el => el.transition().duration(dur * 0.4).ease(ease)
                        .attr("width", 0)
                        .attr("opacity", 0)
                        .remove())
            );

        // ── RANK LABELS (#1, #2 …) ──
        g.selectAll(".rank-label")
            .data(clubs, d => d.club_name)
            .join(
                enter => enter.append("text")
                    .attr("class", "rank-label")
                    .attr("x", 12)
                    .attr("y", d => yScale(d.club_name) + yScale.bandwidth() / 2)
                    .attr("dy", "0.35em")
                    .attr("fill", "rgba(255,255,255,0.65)")
                    .attr("font-size", "11px")
                    .attr("font-weight", "700")
                    .attr("font-family", "'JetBrains Mono', monospace")
                    .attr("pointer-events", "none")
                    .attr("opacity", 0)
                    .text((d, i) => `#${i + 1}`)
                    .call(el => el.transition().duration(dur).ease(ease)
                        .attr("y", d => yScale(d.club_name) + yScale.bandwidth() / 2)
                        .attr("opacity", 1)),
                update => update
                    .text((d, i) => `#${i + 1}`)
                    .call(el => el.transition().duration(dur).ease(ease)
                        .attr("y", d => yScale(d.club_name) + yScale.bandwidth() / 2)
                        .attr("opacity", 1)),
                exit => exit
                    .call(el => el.transition().duration(dur * 0.3)
                        .attr("opacity", 0).remove())
            );

        // ── CLUB NAME LABELS ──
        g.selectAll(".name-label")
            .data(clubs, d => d.club_name)
            .join(
                enter => enter.append("text")
                    .attr("class", "name-label")
                    .attr("x", 44)
                    .attr("y", d => yScale(d.club_name) + yScale.bandwidth() / 2)
                    .attr("dy", "0.35em")
                    .attr("fill", "#fff")
                    .attr("font-size", "14px")
                    .attr("font-weight", "600")
                    .attr("font-family", "'Inter', sans-serif")
                    .attr("pointer-events", "auto")
                    .attr("opacity", 0)
                    .style("cursor", "pointer")
                    .on("click", (ev, d) => showTransfers(d.club_name, currentSeason))
                    .text(d => d.club_name)
                    .call(el => el.transition().duration(dur).ease(ease)
                        .attr("y", d => yScale(d.club_name) + yScale.bandwidth() / 2)
                        .attr("opacity", 1)),
                update => update
                    .text(d => d.club_name)
                    .call(el => el.transition().duration(dur).ease(ease)
                        .attr("y", d => yScale(d.club_name) + yScale.bandwidth() / 2)
                        .attr("opacity", 1)),
                exit => exit
                    .call(el => el.transition().duration(dur * 0.3)
                        .attr("opacity", 0).remove())
            );

        // ── SCORE VALUES (right of bar) ──
        g.selectAll(".score-label")
            .data(clubs, d => d.club_name)
            .join(
                enter => enter.append("text")
                    .attr("class", "score-label")
                    .attr("y", d => yScale(d.club_name) + yScale.bandwidth() / 2)
                    .attr("dy", "0.35em")
                    .attr("x", d => Math.max(220, xScale(d.score) + 8))
                    .attr("fill", "#94a3b8")
                    .attr("font-size", "12px")
                    .attr("font-weight", "600")
                    .attr("font-family", "'JetBrains Mono', monospace")
                    .attr("pointer-events", "none")
                    .attr("opacity", 0)
                    .text(d => d.score.toFixed(4))
                    .call(el => el.transition().duration(dur).ease(ease)
                        .attr("y", d => yScale(d.club_name) + yScale.bandwidth() / 2)
                        .attr("x", d => Math.max(220, xScale(d.score) + 8))
                        .attr("opacity", 1)),
                update => update
                    .call(el => el.transition().duration(dur).ease(ease)
                        .attr("y", d => yScale(d.club_name) + yScale.bandwidth() / 2)
                        .attr("x", d => Math.max(220, xScale(d.score) + 8))
                        .tween("text", function (d) {
                            const prev = parseFloat(this.textContent) || 0;
                            const interp = d3.interpolate(prev, d.score);
                            return (p) => { this.textContent = interp(p).toFixed(4); };
                        })),
                exit => exit
                    .call(el => el.transition().duration(dur * 0.3)
                        .attr("opacity", 0).remove())
            );
    }

    // ── Update progress bar ──
    function updateProgress() {
        if (!timeline.length) return;
        const pct = Math.min(100, ((yearIdx) / (timeline.length - 1)) * 100);
        progressFill.style.width = `${pct}%`;
    }

    // ── Play / Pause ──
    function play() {
        if (playing) return;
        playing = true;
        btnPlayLabel.textContent = "Pause";
        btnPlayIcon.innerHTML = ICON_PAUSE;
        step();
    }

    function step() {
        if (!playing || yearIdx >= timeline.length) {
            if (yearIdx >= timeline.length) {
                playing = false;
                yearIdx = 0;
                btnPlayLabel.textContent = "Restart";
                btnPlayIcon.innerHTML = ICON_PLAY;
            }
            return;
        }

        renderFrame(timeline[yearIdx], true);
        updateProgress();
        yearIdx++;

        animTimer = setTimeout(step, duration);
    }

    function pause() {
        playing = false;
        clearTimeout(animTimer);
        btnPlayLabel.textContent = "Resume";
        btnPlayIcon.innerHTML = ICON_PLAY;
    }

    // ── Event listeners ──
    btnPlay.addEventListener("click", () => {
        if (playing) { pause(); }
        else { play(); }
    });

    speedSel.addEventListener("change", () => {
        duration = parseInt(speedSel.value);
    });

    if (algoSel) {
        algoSel.addEventListener("change", () => {
            const algo = algoSel.value;
            if (timelines[algo]) {
                timeline = timelines[algo];
                // Render the current year with the new data, keeping animation smooth
                renderFrame(timeline[yearIdx], true);
            }
        });
    }

    if (yearSel) {
        yearSel.addEventListener("change", () => {
            if (playing) pause();
            yearIdx = parseInt(yearSel.value);
            renderFrame(timeline[yearIdx], true);
            updateProgress();
        });
    }

    popupClose.addEventListener("click", () => {
        popup.classList.add("hidden");
    });

    // ── Transfer details popup ──
    async function showTransfers(club, season) {
        if (playing) pause();

        popupName.textContent = club;
        popupLoad.classList.remove("hidden");
        popupEmpty.classList.add("hidden");
        popupList.innerHTML = "";
        popup.classList.remove("hidden");

        try {
            const r = await fetch(`/api/transfers/${encodeURIComponent(club)}?start_season=${season}&end_season=${season}&top_n=10`);
            const d = await r.json();
            popupLoad.classList.add("hidden");

            if (!d.transfers || !d.transfers.length) {
                popupEmpty.classList.remove("hidden");
            } else {
                d.transfers.forEach(t => {
                    const li = document.createElement("li");
                    li.className = "transfer-item";
                    const fee = t.fee >= 1e6
                        ? `€${(t.fee / 1e6).toFixed(1)}M`
                        : `€${(t.fee / 1e3).toFixed(0)}K`;
                    li.innerHTML = `
                        <div class="player-name">${t.player_name}</div>
                        <div class="transfer-meta">
                            <span class="transfer-fee">${fee}</span>
                            <span class="transfer-dir ${t.direction === 'in' ? 'dir-in' : 'dir-out'}">${t.direction === 'in' ? 'Bought' : 'Sold'}</span>
                        </div>
                        <div class="transfer-counterparty">
                            ${t.direction === 'in' ? 'from' : 'to'} <strong>${t.counterparty_club}</strong>
                        </div>`;
                    popupList.appendChild(li);
                });
            }
        } catch (err) {
            console.error(err);
            popupLoad.classList.add("hidden");
            popupEmpty.textContent = "Error loading details.";
            popupEmpty.classList.remove("hidden");
        }
    }

    // ── Boot ──
    preloadAllData();
})();
