
console.log("Updated door.js loaded");

console.log("Door page ready");


const API = "http://192.168.50.2:5000";



function openDoor(){

    console.log("Opening door");


    document.getElementById("doorStatus").innerHTML =
    "Opening...";


    fetch(
        API + "/door/open",
        {
            method: "POST"
        }
    )

    .then(response => response.json())

    .then(data => {

        console.log(data.message);


        document.getElementById("doorStatus").innerHTML =
        "Open command sent";

    })

    .catch(error => {

        console.log(error);


        document.getElementById("doorStatus").innerHTML =
        "Door error";

    });

}




function closeDoor(){

    console.log("Closing door");


    document.getElementById("doorStatus").innerHTML =
    "Closing...";


    fetch(
        API + "/door/close",
        {
            method: "POST"
        }
    )

    .then(response => response.json())

    .then(data => {

        console.log(data.message);


        document.getElementById("doorStatus").innerHTML =
        "Close command sent";

    })

    .catch(error => {

        console.log(error);


        document.getElementById("doorStatus").innerHTML =
        "Door error";

    });

}


function updateScheduleDisplay(){

    const mode =
        document.getElementById(
            "scheduleMode"
        ).value;

    const sunSchedule =
        document.getElementById(
            "sunSchedule"
        );

    const manualSchedule =
        document.getElementById(
            "manualSchedule"
        );


    if(mode === "sunrise_sunset"){

        sunSchedule.style.display =
            "block";

        manualSchedule.style.display =
            "none";

    }

    else{

        sunSchedule.style.display =
            "none";

        manualSchedule.style.display =
            "block";

    }

}


function saveSchedule(){

    const mode =
        document.getElementById(
            "scheduleMode"
        ).value;

    const openTime =
        document.getElementById(
            "openTime"
        ).value;

    const closeTime =
        document.getElementById(
            "closeTime"
        ).value;

    const status =
        document.getElementById(
            "scheduleStatus"
        );


    if(
        mode === "manual"
        && (!openTime || !closeTime)
    ){

        status.innerHTML =
            "Please select both manual times.";

        return;

    }


    if(
        mode === "manual"
        && openTime === closeTime
    ){

        status.innerHTML =
            "Open and close times must be different.";

        return;

    }


    status.innerHTML =
        "Saving schedule...";


    fetch(
        API + "/door/schedule",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                mode: mode,
                open_time: openTime,
                close_time: closeTime
            })
        }
    )

    .then(response => {

        return response.json().then(data => {

            if(!response.ok){

                throw new Error(
                    data.error ||
                    "Schedule could not be saved"
                );

            }

            return data;

        });

    })

    .then(data => {

        if(data.mode === "sunrise_sunset"){

            status.innerHTML =
                "Saved: door will open at sunrise "
                + "and close at sunset.";

        }

        else{

            status.innerHTML =
                `Saved: opens at ${data.open_time} `
                + `and closes at ${data.close_time}.`;

        }

    })

    .catch(error => {

        console.error(
            "Schedule save error:",
            error
        );

        status.innerHTML =
            "Error: " + error.message;

    });

}


function loadSchedule(){

    fetch(API + "/door/schedule")

    .then(response => response.json())

    .then(data => {

        const mode =
            data.mode || "sunrise_sunset";

        document.getElementById(
            "scheduleMode"
        ).value = mode;


        if(data.open_time){

            document.getElementById(
                "openTime"
            ).value = data.open_time;

        }


        if(data.close_time){

            document.getElementById(
                "closeTime"
            ).value = data.close_time;

        }


        updateScheduleDisplay();


        const status =
            document.getElementById(
                "scheduleStatus"
            );


        if(mode === "sunrise_sunset"){

            status.innerHTML =
                "Door opens at sunrise "
                + "and closes at sunset.";

        }

        else{

            status.innerHTML =
                `Door opens at ${data.open_time} `
                + `and closes at ${data.close_time}.`;

        }

    })

    .catch(error => {

        console.error(
            "Schedule loading error:",
            error
        );

        document.getElementById(
            "scheduleStatus"
        ).innerHTML =
            "Unable to load schedule.";

    });

}


loadSchedule();