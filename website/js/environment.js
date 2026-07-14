
const API = "http://192.168.50.2:5000";


function loadEnvironment(){

    const locationText =
        document.getElementById("location");


    if(!navigator.geolocation){

        locationText.innerHTML =
            "Location not supported";

        return;
    }


    locationText.innerHTML =
        "Requesting location...";


    navigator.geolocation.getCurrentPosition(

        position => {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;


            locationText.innerHTML =
                `${latitude.toFixed(4)},
                ${longitude.toFixed(4)}`;


            fetch(
                API +
                `/weather?latitude=${latitude}&longitude=${longitude}`
            )

            .then(response => {

                if(!response.ok){

                    throw new Error(
                        "Weather request failed"
                    );

                }

                return response.json();

            })

            .then(data => {

                document.getElementById(
                    "outsideTemperature"
                ).innerHTML =
                    data.temperature + " °F";


                document.getElementById(
                    "feelsLike"
                ).innerHTML =
                    data.feels_like + " °F";


                document.getElementById(
                    "weatherCondition"
                ).innerHTML =
                    data.condition;


                document.getElementById(
                    "outsideHumidity"
                ).innerHTML =
                    data.humidity + " %";


                document.getElementById(
                    "windSpeed"
                ).innerHTML =
                    data.wind_speed + " mph";


                document.getElementById(
                    "sunrise"
                ).innerHTML =
                    formatTime(
                        data.sunrise
                    );


                document.getElementById(
                    "sunset"
                ).innerHTML =
                    formatTime(
                        data.sunset
                    );


                document.getElementById(
                    "rainChance"
                ).innerHTML =
                    data.rain_chance + " %";

            })

            .catch(error => {

                console.log(
                    "Weather error:",
                    error
                );

                locationText.innerHTML =
                    "Weather data unavailable";

            });

        },


        error => {

            console.log(
                "Location error:",
                error
            );


            if(error.code === 1){

                locationText.innerHTML =
                    "Location permission denied";

            }

            else if(error.code === 2){

                locationText.innerHTML =
                    "Location unavailable";

            }

            else{

                locationText.innerHTML =
                    "Location request timed out";

            }

        },


        {
            enableHighAccuracy: false,
            timeout: 10000,
            maximumAge: 600000
        }

    );

}


function formatTime(dateTime){

    if(!dateTime){

        return "--";

    }


    const date =
        new Date(dateTime);


    return date.toLocaleTimeString(
        [],
        {
            hour: "numeric",
            minute: "2-digit"
        }
    );

}


loadEnvironment();


setInterval(
    loadEnvironment,
    900000
);