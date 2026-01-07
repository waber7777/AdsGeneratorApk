import { createCanvas } from 'canvas';
import fs from 'fs';

const size = 512;
const canvas = createCanvas(size, size);
const ctx = canvas.getContext('2d');

// Фон - тёмный градиент
const gradient = ctx.createLinearGradient(0, 0, size, size);
gradient.addColorStop(0, '#0a0a1a');
gradient.addColorStop(1, '#1a1a3a');
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, size, size);

// Сетка на фоне
ctx.strokeStyle = 'rgba(0, 255, 136, 0.1)';
ctx.lineWidth = 1;
for (let i = 0; i < size; i += 32) {
  ctx.beginPath();
  ctx.moveTo(i, 0);
  ctx.lineTo(i, size);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(0, i);
  ctx.lineTo(size, i);
  ctx.stroke();
}

// Змейка - спираль
ctx.lineCap = 'round';
ctx.lineJoin = 'round';

// Тело змеи (толстая линия с градиентом)
const snakeGradient = ctx.createLinearGradient(100, 400, 400, 100);
snakeGradient.addColorStop(0, '#006644');
snakeGradient.addColorStop(0.5, '#00cc66');
snakeGradient.addColorStop(1, '#00ff88');

ctx.strokeStyle = snakeGradient;
ctx.lineWidth = 50;
ctx.beginPath();
ctx.moveTo(120, 400);
ctx.quadraticCurveTo(100, 300, 150, 250);
ctx.quadraticCurveTo(200, 200, 280, 220);
ctx.quadraticCurveTo(360, 240, 380, 180);
ctx.quadraticCurveTo(400, 120, 350, 100);
ctx.stroke();

// Свечение вокруг змеи
ctx.shadowColor = '#00ff88';
ctx.shadowBlur = 30;
ctx.strokeStyle = '#00ff88';
ctx.lineWidth = 40;
ctx.beginPath();
ctx.moveTo(120, 400);
ctx.quadraticCurveTo(100, 300, 150, 250);
ctx.quadraticCurveTo(200, 200, 280, 220);
ctx.quadraticCurveTo(360, 240, 380, 180);
ctx.quadraticCurveTo(400, 120, 350, 100);
ctx.stroke();

ctx.shadowBlur = 0;

// Голова змеи
ctx.fillStyle = '#00ff88';
ctx.beginPath();
ctx.arc(350, 100, 35, 0, Math.PI * 2);
ctx.fill();

// Глаза
ctx.fillStyle = '#ffffff';
ctx.beginPath();
ctx.arc(340, 90, 10, 0, Math.PI * 2);
ctx.fill();
ctx.beginPath();
ctx.arc(365, 90, 10, 0, Math.PI * 2);
ctx.fill();

// Зрачки
ctx.fillStyle = '#000000';
ctx.beginPath();
ctx.arc(342, 88, 5, 0, Math.PI * 2);
ctx.fill();
ctx.beginPath();
ctx.arc(367, 88, 5, 0, Math.PI * 2);
ctx.fill();

// Яблоко/еда
ctx.shadowColor = '#ff4444';
ctx.shadowBlur = 20;
ctx.fillStyle = '#ff4444';
ctx.beginPath();
ctx.arc(200, 380, 30, 0, Math.PI * 2);
ctx.fill();

ctx.shadowBlur = 0;

// Блик на яблоке
ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
ctx.beginPath();
ctx.arc(190, 370, 10, 0, Math.PI * 2);
ctx.fill();

// Листик на яблоке
ctx.fillStyle = '#00cc44';
ctx.beginPath();
ctx.ellipse(200, 348, 8, 15, -0.5, 0, Math.PI * 2);
ctx.fill();

// Сохраняем
const buffer = canvas.toBuffer('image/png');
fs.writeFileSync('icon-512.png', buffer);
console.log('Иконка создана: icon-512.png');

// Создаём также версии для Android
const sizes = [48, 72, 96, 144, 192];
for (const s of sizes) {
  const smallCanvas = createCanvas(s, s);
  const smallCtx = smallCanvas.getContext('2d');
  smallCtx.drawImage(canvas, 0, 0, s, s);
  fs.writeFileSync(`icon-${s}.png`, smallCanvas.toBuffer('image/png'));
  console.log(`Иконка создана: icon-${s}.png`);
}




