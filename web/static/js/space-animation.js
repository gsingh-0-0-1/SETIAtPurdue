const canvas = document.getElementById('nightSky');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const stars = [];
const starColors = ['#ffffff', '#ffddaa', '#aaddff', '#ffff00', '#8888dd'];
const shootingStars = [];

function hexToRgb(hex) {
    const bigint = parseInt(hex.slice(1), 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `${r},${g},${b}`;
}

function Star(x, y, radius, alpha, color) {
    this.x = x;
    this.y = y;
    this.radius = radius;
    this.alpha = alpha;
    this.alphaChange = Math.random() * 0.01 + 0.005;
    this.color = color;
}

Star.prototype.draw = function() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
    ctx.fillStyle = `rgba(${this.color}, ${this.alpha})`;
    ctx.fill();
};

Star.prototype.update = function() {
    this.alpha += this.alphaChange;
    if (this.alpha >= 1 || this.alpha <= 0) {
        this.alphaChange = -this.alphaChange;
    }
    this.draw();
};


function ShootingStar(x, y) {
    this.x = x;
    this.y = y;
    this.length = Math.random() * 80 + 20;
    this.speed = Math.random() * 10 + 5;
    this.alpha = 1;
}

ShootingStar.prototype.draw = function() {
    ctx.beginPath();
    ctx.moveTo(this.x, this.y);
    ctx.lineTo(this.x - this.length, this.y + this.length);
    ctx.strokeStyle = `rgba(255, 255, 255, ${this.alpha})`;
    ctx.lineWidth = 2;
    ctx.stroke();
};

ShootingStar.prototype.update = function() {
    this.x -= this.speed;
    this.y += this.speed;
    this.alpha -= 0.01;
    this.draw();
};

function createShootingStar() {
    const x = canvas.width / 2 + Math.random() * canvas.width / 2;
    const y = Math.random() * canvas.height / 4; 
    shootingStars.push(new ShootingStar(x, y));
}

function randomPow(n) {
	var val = 1;
	for (var i = 0; i < n; i++) {
		val = val * Math.random()
	}
	return val
}

function init() {
    for (let i = 0; i < 200; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const radius = randomPow(1) * 3;
        const alpha = Math.random();
	const color = hexToRgb(starColors[Math.floor(Math.random() * starColors.length)]);
        stars.push(new Star(x, y, radius, alpha, color));
    }
    createShootingStar()
}

function animate() {
    requestAnimationFrame(animate);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    stars.forEach(star => {
        star.update();
    });

    shootingStars.forEach((shootingStar, index) => {
        shootingStar.update();
        if (shootingStar.alpha <= 0) {
            shootingStars.splice(index, 1);
	    setTimeout(createShootingStar, Math.random() * 1000 + 1000);
        }
    });
}

init();
animate();

