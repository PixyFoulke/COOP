
const API = "http://192.168.50.2:5000/status";


function updateData(){


    fetch(API)

    .then(response => response.json())

    .then(data => {


        document.getElementById("status").innerHTML =
        data.status;


        document.getElementById("temperature").innerHTML =
        data.temperature + " °F";


        document.getElementById("humidity").innerHTML =
        data.humidity + " %";


        document.getElementById("chickens").innerHTML =
        data.chicken_count;



        if(data.threats.length > 0){

            document.getElementById("threats").innerHTML =
            data.threats.join(", ");

        }

        else {

            document.getElementById("threats").innerHTML =
            "None";

        }



        if(data.unknowns.length > 0){

            document.getElementById("unknowns").innerHTML =
            data.unknowns.join(", ");

        }

        else {

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