### Bond's thermo

I had a few raspberries lying around, I refreshed my Python knowledge
and made a custom remote controlled thermostat from with a relay.

Consists of two parts
### Web Interface
_running on my pulbic facing VM_

- simple express api with basicauth
- running on my VM
- saves state to local files

### Python Thermostat Controller
_running on the rPI_

- measures temperature via an Adafruit MCP9808 sensor (I2C bus)
- handles buttons (pins 12, 20)
- queries the API for initial settings (REST with basicAuth)
- sends updates to the API
- works offline too
- saves state to local files

### Setup

#### PI
- Instal a fresh pi
- check out this repo
- add users to the `users.json` file
- add `python ` startup to `crontab`
- create `users.json` file from example.

#### Web Interface
- install node
- set recommended security measures
- check out repo
- run `npm i`
- create `secrets.js` file from example with openWeatherMap api key.
- add `node thermo-api.js` to `forever`

---

I was at:
- express api kinda working
  - ✅ trace to log when status is hit.
  - log should be sent even on network error
    - trace last log entry date
    - sync clocks
- python should start sending api updates to the new service
  - send when:
    - ✅ measured temp changed
    - ✅ button pressed
  - ✅ poll last updated temp setting, see which one is more recent
- web interface pretty much working

