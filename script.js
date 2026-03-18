let selectedLibrarySong = null;
const API_BASE = window.location.protocol === 'file:' ? 'http://localhost:5000' : '';

// Load library songs on startup
async function loadLibrary() {
    try {
        const response = await fetch(`${API_BASE}/api/library`);
        const songs = await response.json();
        const container = document.getElementById('song-library');
        container.innerHTML = '';

        if (songs.length === 0) {
            container.innerHTML = '<div class="loading">No library songs found.</div>';
            return;
        }

        songs.forEach(song => {
            const div = document.createElement('div');
            div.className = 'song-item';
            div.innerHTML = `
                <div class="song-icon">🎵</div>
                <div class="song-name">${song.name}</div>
            `;
            div.onclick = () => {
                document.querySelectorAll('.song-item').forEach(el => el.classList.remove('selected'));
                div.classList.add('selected');
                selectedLibrarySong = song.id;
                // Clear file input if something was there
                document.getElementById('audio-input').value = '';
                document.getElementById('audio-filename').textContent = '';
            };
            container.appendChild(div);
        });
    } catch (err) {
        console.error("Failed to load library:", err);
        document.getElementById('song-library').innerHTML = '<div class="loading">Error loading library.</div>';
    }
}

loadLibrary();

document.getElementById('audio-input').onchange = function () {
    const file = this.files[0];
    if (file) {
        document.getElementById('audio-filename').textContent = file.name;
        // Deselect library song if a file is chosen
        document.querySelectorAll('.song-item').forEach(el => el.classList.remove('selected'));
        selectedLibrarySong = null;
    }
};

document.getElementById('formula-file-input').onchange = function () {
    const file = this.files[0];
    if (file) {
        document.getElementById('formula-filename').textContent = file.name;
    }
};

document.getElementById('process-btn').onclick = async function () {
    const audioFile = document.getElementById('audio-input').files[0];
    const formulaFile = document.getElementById('formula-file-input').files[0];

    if ((!audioFile && !selectedLibrarySong) || !formulaFile) {
        alert("Please select a song from the library or upload an audio file, and upload a formulas file.");
        return;
    }

    const formData = new FormData();
    if (audioFile) {
        formData.append('audio', audioFile);
    } else if (selectedLibrarySong) {
        formData.append('librarySong', selectedLibrarySong);
    }

    if (formulaFile) formData.append('formulasFile', formulaFile);

    this.textContent = "Processing...";
    this.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/process`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();

            if (data.warning) {
                alert("Processing Note: " + data.warning);
            }

            const resultsSection = document.getElementById('results-section');
            resultsSection.classList.remove('hidden');

            const audioPlayer = document.getElementById('transformed-audio');
            audioPlayer.src = `${API_BASE}${data.outputFile}`;

            const downloadLink = document.getElementById('download-link');
            downloadLink.href = `${API_BASE}${data.outputFile}`;
            downloadLink.download = "transformed_" + audioFile.name;

            // Simple visualization placeholder
            drawVisualizer();

            resultsSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            const errorData = await response.json();
            let msg = errorData.message || "Something went wrong";
            if (errorData.details) {
                msg += "\n\nDetails: " + errorData.details;
                if (errorData.details.toLowerCase().includes("ffmpeg")) {
                    msg += "\n\nNote: For full MP3 transformation, 'ffmpeg' needs to be installed on the server.";
                }
            }
            alert(msg);
        }
    } catch (error) {
        console.error("Fetch error details:", error);
        alert("Server error: " + error.message + "\n\nMake sure the backend is running.");
    } finally {
        this.textContent = "Generate Transformation";
        this.disabled = false;
    }
};

function drawVisualizer() {
    const canvas = document.getElementById('visualizer');
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.offsetWidth;
    const height = canvas.height = canvas.offsetHeight;

    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = '#6366f1';
    ctx.lineWidth = 2;
    ctx.beginPath();

    for (let x = 0; x < width; x++) {
        const y = height / 2 + Math.sin(x * 0.05) * 30 * Math.random();
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.stroke();
}

function drawMappingChart(formula) {
    const ctx = document.getElementById('mapping-chart').getContext('2d');

    // Evaluate formula for 15 points
    const labels = [];
    const data = [];

    try {
        // Simple evaluation logic for common math functions
        const safeFormula = formula.replace(/sin/g, 'Math.sin').replace(/cos/g, 'Math.cos').replace(/tan/g, 'Math.tan').replace(/log/g, 'Math.log').replace(/exp/g, 'Math.exp').replace(/sqrt/g, 'Math.sqrt');

        for (let i = 0; i < 15; i++) {
            labels.push(`Step ${i}`);
            let val = eval(safeFormula.replace(/x/g, `(${i})`));
            data.push(val);
        }
    } catch (e) {
        console.error("Chart eval error:", e);
    }

    if (window.myChart) window.myChart.destroy();

    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Formula Value',
                data: data,
                borderColor: '#a855f7',
                backgroundColor: 'rgba(168, 85, 247, 0.2)',
                borderWidth: 2,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#fff' } },
                x: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#fff' } }
            },
            plugins: {
                legend: { labels: { color: '#fff' } }
            }
        }
    });
}
