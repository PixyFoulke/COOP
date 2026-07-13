
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


function saveSchedule(){

    const openTime =
        document.getElementById("openTime").value;

    const closeTime =
        document.getElementById("closeTime").value;

    const status =
        document.getElementById("scheduleStatus");


    if(!openTime || !closeTime){

        status.innerHTML =
            "Please select both times.";

        return;
    }


    status.innerHTML =
        "Saving schedule...";


    fetch(
        API + "/door/schedule",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                open_time: openTime,
                close_time: closeTime
            })
        }
    )

    .then(response => response.json())

    .then(data => {

        status.innerHTML =
            `Door will open at ${data.open_time}
            and close at ${data.close_time}.`;

    })

    .catch(error => {

        console.log(error);

        status.innerHTML =
            "Unable to save schedule.";

    });

}


function loadSchedule(){

    fetch(API + "/door/schedule")

    .then(response => response.json())

    .then(data => {

        if(data.open_time){

            document.getElementById("openTime").value =
                data.open_time;

        }

        if(data.close_time){

            document.getElementById("closeTime").value =
                data.close_time;

        }

        if(data.open_time && data.close_time){

            document.getElementById(
                "scheduleStatus"
            ).innerHTML =
                `Door opens at ${data.open_time}
                and closes at ${data.close_time}.`;

        }

    })

    .catch(error => {

        console.log(
            "Schedule loading error:",
            error
        );

    });

}


loadSchedule();