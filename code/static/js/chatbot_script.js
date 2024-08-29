const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let particles = [];
let isFormingNetwork = false;
const layers = 6;
const nodesPerLayer = [5, 10, 10, 10, 10, 5];
const totalParticles = nodesPerLayer.reduce((a, b) => a + b, 0);

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

class Particle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() * 2 - 1) * 2;
        this.vy = (Math.random() * 2 - 1) * 2;
        this.targetX = null;
        this.targetY = null;
        this.layer = null;
    }

    move() {
        if (!isFormingNetwork) {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        } else {
            this.x += (this.targetX - this.x) * 0.05;
            this.y += (this.targetY - this.y) * 0.05;
        }
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
    }
}

function createParticles() {
    particles = [];
    for (let i = 0; i < totalParticles; i++) {
        particles.push(new Particle(Math.random() * canvas.width, Math.random() * canvas.height));
    }
}

function drawLines() {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.lineWidth = 1;
    
    if (isFormingNetwork) {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                if (Math.abs(particles[i].layer - particles[j].layer) === 1) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    } else {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dist = Math.hypot(particles[i].x - particles[j].x, particles[i].y - particles[j].y);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let particle of particles) {
        particle.move();
        particle.draw();
    }

    drawLines();

    requestAnimationFrame(animate);
}

function formNeuralNetwork() {
    isFormingNetwork = true;
    const spacing = {
        x: canvas.width / (layers + 1),
        y: canvas.height / (Math.max(...nodesPerLayer) + 1)
    };

    let particleIndex = 0;
    for (let layer = 0; layer < layers; layer++) {
        const nodeCount = nodesPerLayer[layer];
        const layerHeight = (nodeCount - 1) * spacing.y;
        const startY = (canvas.height - layerHeight) / 2;

        for (let node = 0; node < nodeCount; node++) {
            particles[particleIndex].targetX = spacing.x * (layer + 1);
            particles[particleIndex].targetY = startY + spacing.y * node;
            particles[particleIndex].layer = layer;
            particleIndex++;
        }
    }
}

function scatterParticles() {
    isFormingNetwork = false;
    particles.forEach((particle) => {
        particle.vx = (Math.random() * 2 - 1) * 2;
        particle.vy = (Math.random() * 2 - 1) * 2;
        particle.layer = null;
    });
}

createParticles();
animate();

// Chatbot functionality
let uploadedImage = null;

document.getElementById('image-upload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        uploadedImage = file;
        const reader = new FileReader();
        reader.onload = function(e) {
            const previewContainer = document.getElementById('image-preview-container');
            const preview = document.getElementById('image-preview');
            preview.src = e.target.result;
            previewContainer.style.display = 'block';
        }
        reader.readAsDataURL(file);
    }
});

document.getElementById('remove-image').addEventListener('click', function() {
    const previewContainer = document.getElementById('image-preview-container');
    const imageUpload = document.getElementById('image-upload');
    previewContainer.style.display = 'none';
    imageUpload.value = '';
    uploadedImage = null;
});

function addMessage(content, sender, isImage = false) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    
    if (isImage) {
        const img = document.createElement('img');
        img.src = isImage === true ? URL.createObjectURL(content) : content;
        img.alt = "Chat image";
        img.classList.add('chat-image');
        messageElement.appendChild(img);
    } else {
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('content');
        contentDiv.textContent = content;
        messageElement.appendChild(contentDiv);
    }
    
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showThinking() {
    const messagesContainer = document.getElementById('chatbot-messages');
    const thinkingElement = document.createElement('div');
    thinkingElement.classList.add('message', 'bot', 'thinking');
    
    const gifImage = document.createElement('img');
    gifImage.src = 'static/images/batman-thinking.gif';  // Replace with your gif path
    gifImage.alt = 'Thinking';
    
    const textSpan = document.createElement('span');
    textSpan.textContent = 'Bot is Thinking...';
    
    thinkingElement.appendChild(gifImage);
    thinkingElement.appendChild(textSpan);
    
    messagesContainer.appendChild(thinkingElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return thinkingElement;
}

function sendMessage() {
    const userMessage = document.getElementById('user-input').value.trim();
    if (userMessage === '' && !uploadedImage) return;

    if (uploadedImage) {
        addMessage(uploadedImage, 'user', true);
    }
    if (userMessage) {
        addMessage(userMessage, 'user');
    }
    document.getElementById('user-input').value = '';

    formNeuralNetwork();

    const thinkingElement = showThinking();

    // Send message to backend
    const formData = new FormData();
    formData.append('user_question', userMessage);
    
    let endpoint = '/ask_question';
    if (uploadedImage) {
        formData.append('file', uploadedImage);
        endpoint = '/analyze_skin';
    }

    fetch(endpoint, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        scatterParticles();
        thinkingElement.remove();
        addMessage(data.result, 'bot');
        
        // If the response includes an image URL, display it
        if (data.image_url) {
            addMessage(data.image_url, 'bot', data.image_url);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        scatterParticles();
        thinkingElement.remove();
        addMessage('Sorry, there was an error processing your request.', 'bot');
    });

    // Clear the image preview and reset uploadedImage
    document.getElementById('image-preview-container').style.display = 'none';
    document.getElementById('image-upload').value = '';
    uploadedImage = null;
}

document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});