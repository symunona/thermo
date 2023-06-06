/**
 * ™P Termo at Bond's place.
 */

'use strict'

const DEFAULT_PORT = 3005

const MEASURE_FILE = 'measured'
const TEMP_FILE = 'temp'
const API_LOG_FILE = 'api.log'

const MIN_TEMP = 10
const MAX_TEMP = 30

const fs = require('fs')

const express = require("express")
const basicAuth = require('express-basic-auth')

const users = JSON.parse(fs.readFileSync('./users.json', 'utf-8'))
const app = express();

app.use(basicAuth({ users: users, challenge: true }))
app.use(express.json());
app.use('/', express.static('public', { extensions: ['html', 'css', 'jpg'] }))


app.listen(process.env.port || DEFAULT_PORT, () => {
    log(`----------------------------------------------------------`)
    log(`Server started on port ${process.env.port || DEFAULT_PORT}`)
    log(`Enabled users: ${Object.keys(users).join(', ')}`)
})

let doReload = false


// app.get('/'(req, res, next)=> {
//     res.send(fs.readFileSync('public/index.html', 'utf8'))
// })

app.get("/status", (req, res, next) => {

    let settingsLog = []
    try {
        settingsLog = fs.readFileSync('log', 'utf-8')
    }
    catch (e) {
        log('Logfile error')
    }

    const values = {
        temp: fs.readFileSync('temp', 'utf8'),
        current: fs.readFileSync('measured', 'utf8'),
        update: getLastModifiedDate(),
        on: 'Nope',
        log: settingsLog,
        reload: true,
        isOn: false
    }
    if (values.temp > values.current) {
        values.isOn = true
    }
    if (doReload) {
        doReload = false
        log('RELOAD: signal sent, resetting.')
    }
    res.json(values)
});

app.post("/set", (req, res) => {
    const temp = parseInt(req.body.temp)
    if (isNaN(temp)) {
        res.writeHead(400)
        res.json({ error: 'temp is not a number' })
        log('[ERROR] temp is not a number')
        return
    }
    if (temp < MIN_TEMP || temp > MAX_TEMP) {
        res.writeHead(400)
        res.json({ error: 'temp is out of range' })
        log(`[ERROR] temp is out of range ${temp}`)
        return
    }

    fs.writeFileSync(TEMP_FILE, temp.toString());
    log(`[API] temp set to ${temp} (${req.body.type})`)

    res.json({temp})
    res.end()
})

app.post("/log", (req, res) => {
    log('[CLIENT] ' + req.body.message)
    res.end()
})


app.post("/measured", (req, res) => {
    const temp = parseInt(req.body.temp)
    if (isNaN(temp)) {
        res.writeHead(400)
        res.json({ error: 'temp is not a number' })
        log('[ERROR] measured is not a number')
        return
    }
    if (temp < MIN_TEMP || temp > MAX_TEMP) {
        res.writeHead(400)
        res.json({ error: 'temp is out of range' })
        log(`[ERROR] measured is out of range ${temp}`)
        return
    }

    fs.writeFileSync(MEASURE_FILE, temp);
    log(`temp set to ${temp} (${req.body.type})`)

    res.writeHead(200)
    res.end()
})


app.post("/reload", (req, res) => {
    fs.writeFileSync(MEASURE_FILE, temp);
    log(`RELOAD: on next query`)
    doReload = true
    res.writeHead(200)
    res.end()
})



function log(srt) {
    const timeStamp = '[' + new Date().toISOString() + '] '
    if (!fs.existsSync(API_LOG_FILE)) {
        fs.writeFileSync(API_LOG_FILE, timeStamp + 'Logging Started!')
    }
    fs.appendFileSync(API_LOG_FILE, timeStamp + srt + '\n')
    console.log(timeStamp + srt)
}

function getLastModifiedDate() {
    try {
        var stats = fs.statSync("measured");
        return stats.mtime;
    }
    catch (e) {
        return e.message
    }
}


