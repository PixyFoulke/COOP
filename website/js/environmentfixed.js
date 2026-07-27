
const API = "http://100.98.19.123:5000";


// Fixed location of the chicken coop
const COOP_LATITUDE = 40.0470;
const COOP_LONGITUDE = -83.1283;


function loadEnvironment(){

    const locationText =
        document.getElementById("location");


    const latitude = COOP_LATITUDE;
    const longitude = COOP_LONGITUDE;


    locationText.innerHTML =
        `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;


    fetch(
        API +
        `/weather?latitude=${latitude}&longitude=${longitude}`
    )

    .then(response => {

        if(!response.ok){

            throw new Error(
                `Weather request failed: ${response.status}`
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
            formatTime(data.sunrise);


        document.getElementById(
            "sunset"
        ).innerHTML =
            formatTime(data.sunset);


        document.getElementById(
            "rainChance"
        ).innerHTML =
            data.rain_chance + " %";


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

    })

    .catch(error => {

        console.log(
            "Weather error:",
            error
        );

        locationText.innerHTML =
            `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;

        document.getElementById(
            "weatherCondition"
        ).innerHTML =
            "Weather data unavailable";

    });

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