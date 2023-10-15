async function sendMessage() {
    const hostName = window.location.origin;
    let messageForm = document.forms['messageForm']
    let username = messageForm['telegramUsername'].value;
    let message = messageForm['message'].value;
    let key = parseInt(messageForm['securityKey'].value);

    document.getElementById('submit-button').disabled = true
    setTimeout(() => document.getElementById('submit-button').disabled = false,4000)

    if (isNaN(key)) {
        alert("Please enter a number in security key field.");
        return 0;
    }

    let reqJson = {
        "username" : username,
        "message" : message,
        "securitykey" : key
    }
    console.log(reqJson)

    let query = await fetch(hostName+'/api/sendmessage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(reqJson)
    } )

    let respJson = await query.json();
    console.log(respJson)
    if (respJson.hasOwnProperty('error')) {
        alert("Error: "+respJson['error']);
        return 0;
    }
    if (respJson['status'] != 'success') {
        alert("Unknown error occured. Please contact developer.");
        return 0;
    }

    alert("Status: "+ respJson['status'])  
}
