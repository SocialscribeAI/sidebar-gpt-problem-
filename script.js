window.onload = function() {
    var serverUrl = 'http://127.0.0.1:5000/generate_post';

    fetch(serverUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "text": "start" }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        var botResponse = data.content;
        var history = document.getElementById('chat-history');
        if (data.role && typeof data.role === 'string') {
            history.innerHTML += '<p><b>' + data.role.charAt(0).toUpperCase() + data.role.slice(1) + ':</b> ' + botResponse + '</p>';
        }
    })
    
    .catch(error => {
        console.error('Error:', error);
        var history = document.getElementById('chat-history');
        history.innerHTML += '<p><b>Error:</b> ' + error.message + '</p>';
    });
};

document.getElementById('chat-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var message = document.getElementById('message').value;
    var history = document.getElementById('chat-history');

    history.innerHTML += '<p><b>You:</b> ' + message + '</p>';

    var serverUrl = 'http://127.0.0.1:5000/generate_post';

    fetch(serverUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "text": message }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        var botResponse = data;

        history.innerHTML += '<p><b>Assistant:</b> ' + botResponse + '</p>';
        document.getElementById('message').value = '';

        // Scroll to the bottom of the chat history
        history.scrollTop = history.scrollHeight;
    })
    .catch((error) => {
        console.error('Error:', error);
        // Display the error message to the user
        history.innerHTML += '<p><b>Error:</b> ' + error.message + '</p>';
    });
});

document.getElementById('filter-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var post_topic = document.getElementById('post_topic').value;
    var social_platform = document.getElementById('social_platform').value;
    var example_post_1 = document.getElementById('example_post_1').value;
    var example_post_2 = document.getElementById('example_post_2').value;
    var example_post_3 = document.getElementById('example_post_3').value;

    var serverUrl = 'http://127.0.0.1:5000/generate_post';

    fetch(serverUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "post_topic": post_topic, "social_platform": social_platform, "example_post_1": example_post_1, "example_post_2": example_post_2, "example_post_3": example_post_3 }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Here you can process the response from the server based on your needs
    })
    .catch((error) => {
        console.error('Error:', error);
        var history = document.getElementById('chat-history');
        history.innerHTML += '<p><b>Error:</b> ' + error.message + '</p>';
    });
});
