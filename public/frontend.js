
const HOST = ''
const city = 'Budapest';

const init = async ()=>{
    const {log, temp, current, update, isOn} = await ajax(HOST + 'status', 'GET')

    document.getElementById('current').innerText = current
    document.getElementById('temp_set').innerText = temp

    window.log = log;
    console.log(log)

    if (isOn) {
        document.getElementsByTagName('body')[0].style.cssText = 'background: #950'
    }

    var lastUpdateDate = new Date(update);
    var luElement = document.getElementById('last-update')

    if (isNaN(lastUpdateDate.getTime())) {  // d.valueOf() could also work
        // date is not valid
        luElement.innerHTML = lastUpdate;
    } else {
        // date is valid
        var diffMs = (new Date() - lastUpdateDate); // milliseconds between now & Christmas
        var diffMins = Math.round(((diffMs % 86400000) % 3600000) / 60000);
        luElement.innerHTML = 'last updated ' + diffMins + ' minutes ago'
        if (diffMins > 10) {
            luElement.style.background = "rgba(200,10,10,0.5)"
        }
    }
}

init()


loadTempOutside();

function set(value) {
    ajax('/set/', 'post', {temp: value, type: 'web'});
}


function loadTempOutside() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            const temp = JSON.parse(this.responseText).main.temp - 273.15
            const tempRounded = Math.round(temp * 100) / 100
            document.getElementById("outside").innerText = tempRounded;
        }
    };

    url = "//api.openweathermap.org/data/2.5/weather?APPID=" + window.openWeatherMapApiKey + "&q=" + city
    xhttp.open("GET", url, true);
    xhttp.send();
}

function ajax(url, method, data) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    };

    return fetch(url, options)
        .then(response => response.json())
}


function loadHistory(){
    var color = Chart.helpers.color;
    var red = 'rgb(255, 22, 22)', blue = 'rgb(54, 162, 235)';
    var config = {
        type: 'line',
        data: {
            datasets: [{
                label: 'SET',
                backgroundColor: color(red).alpha(0.5).rgbString(),
                borderColor: red,
                fill: false,
                data: log.map(function (i) { return { x: new Date(i.date), y: Number(i.set) } }),
            }, {
                label: 'MEASURED',
                backgroundColor: color(blue).alpha(0.5).rgbString(),
                borderColor: blue,
                fill: false,
                data: log.map(function (i) { return { x: new Date(i.date), y: Number(i.sensor) } }),
            }]
        },
        options: {
            responsive: true,
            scales: {
                xAxes: [{
                    type: 'time',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Date'
                    },
                    ticks: {
                        major: {
                            fontStyle: 'bold',
                            fontColor: '#FF0000'
                        }
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'value'
                    }
                }]
            }
        }
    };


    var ctx = document.getElementById('stat')
    var myChart = new Chart(ctx, config);
}
