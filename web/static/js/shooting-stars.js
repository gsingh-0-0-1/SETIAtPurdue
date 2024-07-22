const canvas = document.getElementById('shootingStarsCanvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const shootingStars = [];

function random(min, max) {
    return Math.random() * (max - min) + min;
}

class ShootingStar {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = random(-canvas.width, canvas.width);
        this.y = random(-canvas.height, canvas.height);
        this.z = random(0, canvas.width);
        this.pz = this.z;
        this.speed = random(4, 7);
    }

    update() {
        this.pz = this.z;
        this.z -= this.speed;
        if (this.z < 1) {
            this.reset();
        }
    }

    draw() {
        const sx = (this.x / this.z) * canvas.width + canvas.width / 2;
        const sy = (this.y / this.z) * canvas.height + canvas.height / 2;
        const psx = (this.x / this.pz) * canvas.width + canvas.width / 2;
        const psy = (this.y / this.pz) * canvas.height + canvas.height / 2;

        ctx.beginPath();
        ctx.moveTo(psx, psy);
        ctx.lineTo(sx, sy);
        ctx.strokeStyle = 'rgba(255, 255, 255, 1)';
        ctx.lineWidth = random(1, 3);
        ctx.stroke();
    }
}

function createShootingStars(count) {
    for (let i = 0; i < count; i++) {
        shootingStars.push(new ShootingStar());
    }
}

function animate() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    shootingStars.forEach(star => {
        star.update();
        star.draw();
    });
    requestAnimationFrame(animate);
}

createShootingStars(250);
animate();

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

