
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


                /*
                Save location and sun times so the
                Settings page can send them to the Pi.
                */

                localStorage.setItem(
                    "latitude",
                    latitude
                );

                localStorage.setItem(
                    "longitude",
                    longitude
                );

                localStorage.setItem(
                    "sunrise",
                    formatTime24Hour(data.sunrise)
                );

                localStorage.setItem(
                    "sunset",
                    formatTime24Hour(data.sunset)
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


/*
Converts the sunrise or sunset time into
24-hour HH:MM format for Python.

Example:
8:42 PM becomes 20:42
*/

function formatTime24Hour(dateTime){

    if(!dateTime){

        return "";

    }


    const date =
        new Date(dateTime);


    const hours =
        String(date.getHours()).padStart(2, "0");

    const minutes =
        String(date.getMinutes()).padStart(2, "0");


    return `${hours}:${minutes}`;

}


loadEnvironment();


setInterval(
    loadEnvironment,
    900000
);