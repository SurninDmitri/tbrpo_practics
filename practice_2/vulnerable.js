const express = require('express');
const app = express();
const sqlite3 = require('sqlite3');

app.use(express.urlencoded({ extended: true }));
const db = new sqlite3.Database(':memory:');

// УЯЗВИМОСТЬ #1: SQL Injection (CWE-89)
app.get('/user', (req, res) => {
    const username = req.query.username;
    db.get(`SELECT * FROM users WHERE username = '${username}'`, (err, row) => {
        res.json(row);
    });
});

// УЯЗВИМОСТЬ #2: XSS (CWE-79)
app.get('/hello', (req, res) => {
    const name = req.query.name;
    res.send(`<h1>Hello, ${name}!</h1>`);  // ❌ Прямой вывод
});

// УЯЗВИМОСТЬ #3: Command Injection (CWE-78)
app.get('/ping', (req, res) => {
    const host = req.query.host;
    const { exec } = require('child_process');
    exec(`ping -c 1 ${host}`, (error, stdout) => {
        res.send(stdout);
    });
});

app.listen(3000);
