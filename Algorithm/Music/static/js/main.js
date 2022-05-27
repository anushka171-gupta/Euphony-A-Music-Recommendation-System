
function login() {

    var username = document.getElementById('username').value
    var password = document.getElementById('password').value
    var csrf = document.getElementById('csrf').value

    if(username == '' && password == '') {
        alert('Username and Password cannot be Empty')
    }

    var data = {
        'username': username,
        'password': password
    }

    fetch('/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf           
        },
       
        body: JSON.stringify(data)
    }).then(result => result.json())
    .then(response => {
        
        if(response.status == 200) {
            window.location.href = '/Music/explore'
        }
        else {
            alert(response.message)
        }
    })

}

function register(){
    var username = document.getElementById('username').value
    var password = document.getElementById('password').value
    var first_name = document.getElementById('first_name').value
    var last_name = document.getElementById('last_name').value

    var csrf = document.getElementById('csrf').value

    if(username == '' && password == ''){
        alert('Username and Password cannot be Empty')
    }

    var data = {
        'username' : username,
        'password' : password,
        'first_name' : first_name,
        'last_name' : last_name
    }

    fetch('/api/register/' , {
        method : 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken' : csrf,
        },
       
        body : JSON.stringify(data)
    }).then(result => result.json())
    .then(response => {
        console.log(response)
        if(response.status == 200){
            window.location.href = '/Music/explore'
        }
        else{
            alert(response.message)
        }

    })

}