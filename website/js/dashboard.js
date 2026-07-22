
const API = "http://100.98.19.123:5000/status";


function updateData(){


fetch(API)

.then(response => response.json())


.then(data => {


    let status =
    document.getElementById("status");


    status.innerHTML =
    data.status;



    // STATUS COLORS

    status.className="value";


    if(data.status.includes("SAFE")){

        status.classList.add("safe");

    }

    else if(data.status.includes("THREAT")){

        status.classList.add("danger");

    }

    else{

        status.classList.add("warning");

    }



    document.getElementById("temperature").innerHTML =
    data.temperature + " °F";


    document.getElementById("humidity").innerHTML =
    data.humidity + " % Humidity";


    document.getElementById("chickens").innerHTML =
    data.chicken_count;



    if(data.light_state){

        document.getElementById("light").innerHTML =
        data.light_state;

    }



    if(data.threats.length > 0){

        document.getElementById("threats").innerHTML =
        data.threats.join(", ");

    }

    else{

        document.getElementById("threats").innerHTML =
        "None";

    }



    if(data.unknowns.length > 0){

        document.getElementById("unknowns").innerHTML =
        data.unknowns.join(", ");

    }

    else{

        document.getElementById("unknowns").innerHTML =
        "None";

    }


})


.catch(error => {

    console.log(error);

});


}



setInterval(updateData,1000);

updateData();