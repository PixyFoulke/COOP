
const API = "http://192.168.50.2:5000";


// CHART REFERENCES
let tempChart;
let humidityChart;
let chickenChart;


function loadData(){

    fetch(API + "/history")

    .then(response => response.json())

    .then(data => {

        let times = [];
        let temperatures = [];
        let humidity = [];
        let chickens = [];


        data.forEach(row => {

            let time = new Date(
                row.timestamp.replace(" ", "T")
            );

            times.push(
                time.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit"
                })
            );

            temperatures.push(
                row.temperature
            );

            humidity.push(
                row.humidity
            );

            chickens.push(
                row.chickens
            );

        });


        createTemperatureChart(
            times,
            temperatures
        );

        createHumidityChart(
            times,
            humidity
        );

        createChickenChart(
            times,
            chickens
        );

        loadThreats();

    })

    .catch(error => {

        console.log(
            "Data error:",
            error
        );

    });

}


function createTemperatureChart(labels, values){

    let ctx =
        document.getElementById(
            "temperatureChart"
        );

    if(tempChart){
        tempChart.destroy();
    }

    tempChart = new Chart(
        ctx,
        {
            type: "line",

            data: {
                labels: labels,

                datasets: [{
                    label: "Temperature °F",
                    data: values,
                    tension: 0.3,
                    spanGaps: false
                }]
            },

            options: {
                responsive: true,

                scales: {
                    y: {
                        title: {
                            display: true,
                            text: "Temperature °F"
                        }
                    },

                    x: {
                        title: {
                            display: true,
                            text: "Time"
                        }
                    }
                }
            }
        }
    );

}


function createHumidityChart(labels, values){

    let ctx =
        document.getElementById(
            "humidityChart"
        );

    if(humidityChart){
        humidityChart.destroy();
    }

    humidityChart = new Chart(
        ctx,
        {
            type: "line",

            data: {
                labels: labels,

                datasets: [{
                    label: "Humidity %",
                    data: values,
                    tension: 0.3,
                    spanGaps: false
                }]
            },

            options: {
                responsive: true,

                scales: {
                    y: {
                        title: {
                            display: true,
                            text: "Humidity %"
                        }
                    },

                    x: {
                        title: {
                            display: true,
                            text: "Time"
                        }
                    }
                }
            }
        }
    );

}


function createChickenChart(labels, values){

    let ctx =
        document.getElementById(
            "chickenChart"
        );

    if(chickenChart){
        chickenChart.destroy();
    }

    chickenChart = new Chart(
        ctx,
        {
            type: "line",

            data: {
                labels: labels,

                datasets: [{
                    label: "Chickens Inside Coop",
                    data: values,
                    tension: 0.3,
                    spanGaps: false
                }]
            },

            options: {
                responsive: true,

                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },

                        title: {
                            display: true,
                            text: "Chicken Count"
                        }
                    },

                    x: {
                        title: {
                            display: true,
                            text: "Time"
                        }
                    }
                }
            }
        }
    );

}


function loadThreats(){

    let container =
        document.getElementById(
            "threatHistory"
        );

    container.innerHTML =
        "<p>Loading threat history...</p>";


    fetch(API + "/threats/history")

    .then(response => {

        if(!response.ok){
            throw new Error(
                "Could not load threat history"
            );
        }

        return response.json();

    })

    .then(threats => {

        container.innerHTML = "";

        if(threats.length === 0){

            container.innerHTML =
                "<p>No threats detected in the past 24 hours.</p>";

            return;
        }


        threats.forEach(threat => {

            let card =
                document.createElement(
                    "div"
                );

            card.className =
                "threat-card";


            let detectedTime =
                new Date(
                    threat.timestamp.replace(
                        " ",
                        "T"
                    )
                );


            card.innerHTML = `

                <img
                    class="threat-image"
                    src="${API}${threat.image_url}"
                    alt="Detected threat"
                >

                <div class="threat-details">

                    <h3>
                        🚨 ${threat.threat_type}
                    </h3>

                    <p>
                        ${detectedTime.toLocaleString()}
                    </p>

                </div>

            `;


            container.appendChild(
                card
            );

        });

    })

    .catch(error => {

        console.log(
            "Threat history error:",
            error
        );

        container.innerHTML =
            "<p>Unable to load threat history.</p>";

    });

}


// LOAD WHEN PAGE OPENS
loadData();


// REFRESH EVERY MINUTE
setInterval(
    loadData,
    60000
);