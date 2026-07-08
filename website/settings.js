
const SETTINGS_API =
"http://192.168.50.2:5000/settings";


function saveSettings(){


let data = {

    chicken_count:
    document.getElementById("chicken_count").value,


    email:
    document.getElementById("email").value

};



fetch(SETTINGS_API, {

    method:"POST",

    headers:{
        "Content-Type":"application/json"
    },

    body:JSON.stringify(data)

})


.then(response => response.json())


.then(result => {

    alert("Settings saved!");

})


.catch(error => {

    console.log(error);

});


}