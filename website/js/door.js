
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