const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');

const app = express();
const port = 5000;

const libraryDir = path.join(__dirname, 'library');
if (!fs.existsSync(libraryDir)) {
    fs.mkdirSync(libraryDir);
}

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/library', express.static(libraryDir));

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({ storage });

const { spawn } = require('child_process');

// Endpoint to list library songs
app.get('/api/library', (req, res) => {
    fs.readdir(libraryDir, (err, files) => {
        if (err) {
            return res.status(500).json({ message: 'Error reading library' });
        }
        const songs = files.filter(f => f.endsWith('.mp3') || f.endsWith('.wav') || f.endsWith('.midi') || f.endsWith('.mid'))
            .map(f => ({
                id: f,
                name: f.replace(/_/g, ' ').replace(/\.[^/.]+$/, ""),
                url: `/library/${f}`
            }));
        res.json(songs);
    });
});

app.post('/process', upload.fields([
    { name: 'audio', maxCount: 1 },
    { name: 'formulasFile', maxCount: 1 }
]), (req, res) => {
    const audioFile = req.files['audio'] ? req.files['audio'][0] : null;
    const formulaFile = req.files['formulasFile'] ? req.files['formulasFile'][0] : null;
    const librarySong = req.body.librarySong;

    if ((!audioFile && !librarySong) || !formulaFile) {
        return res.status(400).json({ message: 'Missing audio (or library song) or formulas file' });
    }

    let inputPath;
    let isLibrary = false;

    if (audioFile) {
        inputPath = audioFile.path;
    } else {
        inputPath = path.join(libraryDir, librarySong);
        isLibrary = true;
    }

    const formulasFilePath = formulaFile ? formulaFile.path : '';

    const timestamp = Date.now();
    const outputPath = `uploads/transformed-${timestamp}.wav`;

    // Invoke Python script with optional formula file path
    const pythonArgs = ['processor.py', inputPath, outputPath];
    if (formulasFilePath) {
        pythonArgs.push('--file', formulasFilePath);
    }

    const pythonProcess = spawn('python', pythonArgs, {
        cwd: __dirname,
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });

    let stdoutData = '';
    let stderrData = '';

    pythonProcess.stdout.on('data', (data) => {
        const str = data.toString();
        stdoutData += str;
        console.log(`[Python Stdout]: ${str.trim()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        const str = data.toString();
        stderrData += str;
        console.error(`[Python Stderr]: ${str.trim()}`);
    });

    pythonProcess.on('close', (code) => {
        // Clean up the input files after processing (only if uploaded)
        if (!isLibrary) {
            fs.unlink(inputPath, (err) => {
                if (err) console.error(`Error deleting input file ${inputPath}:`, err);
            });
        }

        if (formulasFilePath) {
            fs.unlink(formulasFilePath, (err) => {
                if (err) console.error(`Error deleting formulas file ${formulasFilePath}:`, err);
            });
        }

        if (code === 0) {
            // Check for warnings in stdout (e.g., "Skipping original tune load")
            const hasWarning = stdoutData.includes("Skipping original tune load") || stdoutData.includes("Notice: Loading MP3 requires ffmpeg");

            res.json({
                success: true,
                message: "Music processed successfully",
                outputFile: `/uploads/transformed-${timestamp}.wav`,
                warning: hasWarning ? "Original tune could not be loaded (needs ffmpeg for MP3). Generated pure formula melody instead." : null
            });
        } else {
            console.error(`Python process exited with code ${code}`);
            console.error(`Stderr: ${stderrData}`);
            // If Python script failed, delete the potentially created output file
            fs.unlink(outputPath, (err) => {
                if (err && err.code !== 'ENOENT') console.error(`Error deleting output file ${outputPath}:`, err);
            });
            res.status(500).json({
                success: false,
                message: "Error processing music in Python script",
                details: stderrData || stdoutData || `Process exited with code ${code}`
            });
        }
    });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
