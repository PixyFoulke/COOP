
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


            let time = new Date(row.timestamp);


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


        loadThreats(data);


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

            type:"line",

            data:{

                labels:labels,

                datasets:[{

                    label:"Temperature °F",

                    data:values,

                    tension:0.3

                }]

            },

            options:{

                responsive:true,

                scales:{

                    y:{

                        title:{
                            display:true,
                            text:"°F"
                        }

                    },

                    x:{

                        title:{
                            display:true,
                            text:"Time"
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

            type:"line",

            data:{

                labels:labels,

                datasets:[{

                    label:"Humidity %",

                    data:values,

                    tension:0.3

                }]

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

            type:"line",

            data:{

                labels:labels,

                datasets:[{

                    label:"Chickens Inside Coop",

                    data:values,

                    tension:0.3

                }]

            }

        }

    );


}





function loadThreats(data){


    let container =
    document.getElementById(
        "threatHistory"
    );


    container.innerHTML = "";



    data.forEach(row => {


        if(
            row.threats &&
            row.threats !== "[]"
        ){


            let card =
            document.createElement(
                "div"
            );


            card.className =
            "card";


            card.innerHTML = `

                <h3>
                🚨 Threat Detected
                </h3>

                <p>
                ${row.timestamp}
                </p>

                <p>
                ${row.threats}
                </p>

                <img
                src="http://192.168.50.2:5000/threat_image"
                width="250">

            `;


            container.appendChild(card);


        }


    });


}





// LOAD WHEN PAGE OPENS

loadData();


// Refresh every minute

setInterval(
    loadData,
    60000
);