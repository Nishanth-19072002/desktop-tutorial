const path = require('path');
const WebSocket = require('ws');
const { spawn } = require('child_process');
const fs = require('fs');

// Create a WebSocket server
const server = new WebSocket.Server({ port: 1400 });;

server.on('connection', (ws) => {
    console.log('Client connected');
    
    // Path to the pyright language server
    const pyrightPath = path.join(__dirname, 'node_modules', 'pyright', 'dist', 'pyright-langserver.js');
    
    // Check if pyright exists at the specified path
    if (!fs.existsSync(pyrightPath)) {
        console.error('pyright not found at ' + pyrightPath);
        ws.close();
        return;
    }

    // Start the pyright language server
    const pyrightProcess = spawn('node', [pyrightPath, '--stdio']);

    // Handle data from pyright-langserver
    pyrightProcess.stdout.on('data', (data) => {
        ws.send(data);
    });

    pyrightProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pyrightProcess.on('close', (code) => {
        console.log(`pyright process exited with code ${code}`);
    });

    // Forward client messages to pyright-langserver
    ws.on('message', (message) => {
        console.log(message);
        pyrightProcess.stdin.write(message);
    });

    ws.on('close', () => {
        console.log('Client disconnected');
        pyrightProcess.kill();
    });
});

console.log('WebSocket server is running on ws://localhost:3000');
