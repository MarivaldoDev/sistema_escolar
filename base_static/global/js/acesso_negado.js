let countdown = 5;

function updateCountdown() {
    document.getElementById("timer").textContent = countdown;
    if (countdown === 0) {
        window.location.href = '/'; 
    } else {
        countdown--;
        setTimeout(updateCountdown, 1000);
    }
}

window.onload = updateCountdown;