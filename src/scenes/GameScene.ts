import Phaser from 'phaser';

interface SnakeSegment {
  x: number;
  y: number;
}

export class GameScene extends Phaser.Scene {
  private snake: SnakeSegment[] = [];
  private direction: { x: number; y: number } = { x: 1, y: 0 };
  private nextDirection: { x: number; y: number } = { x: 1, y: 0 };
  private food: { x: number; y: number } = { x: 0, y: 0 };
  private score: number = 0;
  private highScore: number = 0;
  private gameOver: boolean = false;
  private moveTimer: number = 0;
  private moveInterval: number = 150;
  
  private gridSize: number = 20;
  private gridWidth: number = 0;
  private gridHeight: number = 0;
  private offsetX: number = 0;
  private offsetY: number = 0;
  
  private graphics!: Phaser.GameObjects.Graphics;
  private scoreText!: Phaser.GameObjects.Text;
  private gameOverContainer!: Phaser.GameObjects.Container;
  
  private touchStartX: number = 0;
  private touchStartY: number = 0;

  constructor() {
    super({ key: 'GameScene' });
  }

  create() {
    const { width, height } = this.scale;
    
    // Рассчитываем игровое поле
    this.gridWidth = Math.floor((width - 40) / this.gridSize);
    this.gridHeight = Math.floor((height - 140) / this.gridSize);
    this.offsetX = (width - this.gridWidth * this.gridSize) / 2;
    this.offsetY = 80;
    
    this.graphics = this.add.graphics();
    this.highScore = parseInt(localStorage.getItem('snakeHighScore') || '0');
    
    // UI
    this.createUI(width);
    
    // Инициализация игры
    this.initGame();
    
    // Управление
    this.setupControls();
    
    // Создаем контейнер Game Over (скрыт)
    this.createGameOverScreen(width, height);
  }

  private createUI(width: number) {
    // Счёт
    const scoreContainer = this.add.container(width / 2, 40);
    
    const scoreBg = this.add.graphics();
    scoreBg.fillStyle(0x1a1a2e, 0.9);
    scoreBg.fillRoundedRect(-80, -25, 160, 50, 12);
    
    this.scoreText = this.add.text(0, 0, '0', {
      fontFamily: 'Arial Black, Arial, sans-serif',
      fontSize: '32px',
      color: '#00ff88'
    });
    this.scoreText.setOrigin(0.5);
    
    scoreContainer.add([scoreBg, this.scoreText]);

    // Кнопка паузы/выхода
    const backButton = this.add.text(30, 40, '✕', {
      fontSize: '32px',
      color: '#666666'
    });
    backButton.setOrigin(0.5);
    backButton.setInteractive({ useHandCursor: true });
    backButton.on('pointerdown', () => {
      this.scene.start('MenuScene');
    });
  }

  private initGame() {
    // Сброс состояния
    this.snake = [];
    this.score = 0;
    this.gameOver = false;
    this.direction = { x: 1, y: 0 };
    this.nextDirection = { x: 1, y: 0 };
    this.moveTimer = 0;
    this.moveInterval = 150;
    
    // Создаём змейку в центре
    const startX = Math.floor(this.gridWidth / 2);
    const startY = Math.floor(this.gridHeight / 2);
    
    for (let i = 0; i < 4; i++) {
      this.snake.push({ x: startX - i, y: startY });
    }
    
    // Спавним еду
    this.spawnFood();
    
    // Обновляем UI
    this.scoreText.setText('0');
    
    if (this.gameOverContainer) {
      this.gameOverContainer.setVisible(false);
    }
  }

  private setupControls() {
    // Клавиатура
    this.input.keyboard?.on('keydown', (event: KeyboardEvent) => {
      switch (event.code) {
        case 'ArrowUp':
        case 'KeyW':
          if (this.direction.y !== 1) this.nextDirection = { x: 0, y: -1 };
          break;
        case 'ArrowDown':
        case 'KeyS':
          if (this.direction.y !== -1) this.nextDirection = { x: 0, y: 1 };
          break;
        case 'ArrowLeft':
        case 'KeyA':
          if (this.direction.x !== 1) this.nextDirection = { x: -1, y: 0 };
          break;
        case 'ArrowRight':
        case 'KeyD':
          if (this.direction.x !== -1) this.nextDirection = { x: 1, y: 0 };
          break;
        case 'Space':
          if (this.gameOver) this.initGame();
          break;
      }
    });

    // Тач/свайп
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      this.touchStartX = pointer.x;
      this.touchStartY = pointer.y;
    });

    this.input.on('pointerup', (pointer: Phaser.Input.Pointer) => {
      const dx = pointer.x - this.touchStartX;
      const dy = pointer.y - this.touchStartY;
      const minSwipe = 30;

      if (Math.abs(dx) > Math.abs(dy)) {
        if (dx > minSwipe && this.direction.x !== -1) {
          this.nextDirection = { x: 1, y: 0 };
        } else if (dx < -minSwipe && this.direction.x !== 1) {
          this.nextDirection = { x: -1, y: 0 };
        }
      } else {
        if (dy > minSwipe && this.direction.y !== -1) {
          this.nextDirection = { x: 0, y: 1 };
        } else if (dy < -minSwipe && this.direction.y !== 1) {
          this.nextDirection = { x: 0, y: -1 };
        }
      }
    });
  }

  private createGameOverScreen(width: number, height: number) {
    this.gameOverContainer = this.add.container(width / 2, height / 2);
    this.gameOverContainer.setVisible(false);
    this.gameOverContainer.setDepth(100);

    // Затемнение
    const overlay = this.add.graphics();
    overlay.fillStyle(0x000000, 0.7);
    overlay.fillRect(-width / 2, -height / 2, width, height);

    // Панель
    const panel = this.add.graphics();
    panel.fillStyle(0x1a1a2e, 1);
    panel.fillRoundedRect(-150, -150, 300, 300, 20);
    panel.lineStyle(3, 0xff4444, 1);
    panel.strokeRoundedRect(-150, -150, 300, 300, 20);

    // Заголовок
    const gameOverText = this.add.text(0, -100, 'ИГРА\nОКОНЧЕНА', {
      fontFamily: 'Arial Black, Arial, sans-serif',
      fontSize: '36px',
      color: '#ff4444',
      align: 'center'
    });
    gameOverText.setOrigin(0.5);

    // Счёт
    const finalScoreLabel = this.add.text(0, -10, 'СЧЁТ', {
      fontFamily: 'Arial, sans-serif',
      fontSize: '16px',
      color: '#888888'
    });
    finalScoreLabel.setOrigin(0.5);

    const finalScoreValue = this.add.text(0, 25, '0', {
      fontFamily: 'Arial Black, Arial, sans-serif',
      fontSize: '48px',
      color: '#00ff88'
    });
    finalScoreValue.setOrigin(0.5);
    finalScoreValue.setName('finalScore');

    // Новый рекорд (скрыт по умолчанию)
    const newRecordText = this.add.text(0, 70, '🏆 НОВЫЙ РЕКОРД!', {
      fontFamily: 'Arial Black, Arial, sans-serif',
      fontSize: '20px',
      color: '#ffcc00'
    });
    newRecordText.setOrigin(0.5);
    newRecordText.setName('newRecord');
    newRecordText.setVisible(false);

    // Кнопка "Ещё раз"
    const retryButton = this.createRetryButton(0, 120);

    this.gameOverContainer.add([overlay, panel, gameOverText, finalScoreLabel, finalScoreValue, newRecordText, retryButton]);
  }

  private createRetryButton(x: number, y: number): Phaser.GameObjects.Container {
    const container = this.add.container(x, y);

    const bg = this.add.graphics();
    bg.fillStyle(0x00ff88, 1);
    bg.fillRoundedRect(-80, -25, 160, 50, 25);

    const text = this.add.text(0, 0, 'ЕЩЁ РАЗ', {
      fontFamily: 'Arial Black, Arial, sans-serif',
      fontSize: '22px',
      color: '#0a0a0f'
    });
    text.setOrigin(0.5);

    container.add([bg, text]);
    container.setSize(160, 50);
    container.setInteractive({ useHandCursor: true });

    container.on('pointerdown', () => {
      this.initGame();
    });

    return container;
  }

  private spawnFood() {
    let validPosition = false;
    
    while (!validPosition) {
      this.food.x = Phaser.Math.Between(0, this.gridWidth - 1);
      this.food.y = Phaser.Math.Between(0, this.gridHeight - 1);
      
      validPosition = !this.snake.some(seg => seg.x === this.food.x && seg.y === this.food.y);
    }
  }

  update(_time: number, delta: number) {
    if (this.gameOver) return;

    this.moveTimer += delta;
    
    if (this.moveTimer >= this.moveInterval) {
      this.moveTimer = 0;
      this.moveSnake();
    }
    
    this.draw();
  }

  private moveSnake() {
    this.direction = { ...this.nextDirection };
    
    const head = this.snake[0];
    const newHead: SnakeSegment = {
      x: head.x + this.direction.x,
      y: head.y + this.direction.y
    };

    // Проверка столкновения со стенами
    if (newHead.x < 0 || newHead.x >= this.gridWidth || 
        newHead.y < 0 || newHead.y >= this.gridHeight) {
      this.endGame();
      return;
    }

    // Проверка столкновения с собой
    if (this.snake.some(seg => seg.x === newHead.x && seg.y === newHead.y)) {
      this.endGame();
      return;
    }

    this.snake.unshift(newHead);

    // Проверка еды
    if (newHead.x === this.food.x && newHead.y === this.food.y) {
      this.score += 10;
      this.scoreText.setText(this.score.toString());
      this.spawnFood();
      
      // Ускорение
      if (this.moveInterval > 80) {
        this.moveInterval -= 2;
      }
    } else {
      this.snake.pop();
    }
  }

  private endGame() {
    this.gameOver = true;
    
    // Обновляем рекорд
    const isNewRecord = this.score > this.highScore;
    if (isNewRecord) {
      this.highScore = this.score;
      localStorage.setItem('snakeHighScore', this.highScore.toString());
    }

    // Показываем экран Game Over
    const finalScoreText = this.gameOverContainer.getByName('finalScore') as Phaser.GameObjects.Text;
    const newRecordText = this.gameOverContainer.getByName('newRecord') as Phaser.GameObjects.Text;
    
    finalScoreText.setText(this.score.toString());
    newRecordText.setVisible(isNewRecord);
    
    this.gameOverContainer.setVisible(true);
    this.gameOverContainer.setAlpha(0);
    this.gameOverContainer.setScale(0.8);
    
    this.tweens.add({
      targets: this.gameOverContainer,
      alpha: 1,
      scale: 1,
      duration: 300,
      ease: 'Back.easeOut'
    });
  }

  private draw() {
    this.graphics.clear();
    
    // Игровое поле
    this.graphics.fillStyle(0x0d0d15, 1);
    this.graphics.fillRoundedRect(
      this.offsetX - 5, 
      this.offsetY - 5, 
      this.gridWidth * this.gridSize + 10, 
      this.gridHeight * this.gridSize + 10, 
      10
    );
    
    // Сетка
    this.graphics.lineStyle(1, 0x1a1a2e, 0.3);
    for (let x = 0; x <= this.gridWidth; x++) {
      this.graphics.lineBetween(
        this.offsetX + x * this.gridSize, 
        this.offsetY,
        this.offsetX + x * this.gridSize, 
        this.offsetY + this.gridHeight * this.gridSize
      );
    }
    for (let y = 0; y <= this.gridHeight; y++) {
      this.graphics.lineBetween(
        this.offsetX, 
        this.offsetY + y * this.gridSize,
        this.offsetX + this.gridWidth * this.gridSize, 
        this.offsetY + y * this.gridSize
      );
    }

    // Еда
    const foodX = this.offsetX + this.food.x * this.gridSize + this.gridSize / 2;
    const foodY = this.offsetY + this.food.y * this.gridSize + this.gridSize / 2;
    
    // Свечение еды
    this.graphics.fillStyle(0xff4444, 0.3);
    this.graphics.fillCircle(foodX, foodY, this.gridSize / 2 + 4);
    this.graphics.fillStyle(0xff6666, 1);
    this.graphics.fillCircle(foodX, foodY, this.gridSize / 2 - 2);
    this.graphics.fillStyle(0xffaaaa, 1);
    this.graphics.fillCircle(foodX - 2, foodY - 2, 3);

    // Змейка
    this.snake.forEach((segment, index) => {
      const x = this.offsetX + segment.x * this.gridSize;
      const y = this.offsetY + segment.y * this.gridSize;
      const padding = 1;
      
      if (index === 0) {
        // Голова
        this.graphics.fillStyle(0x00ff88, 1);
        this.graphics.fillRoundedRect(
          x + padding, y + padding,
          this.gridSize - padding * 2, this.gridSize - padding * 2,
          6
        );
        
        // Глаза
        const eyeOffsetX = this.direction.x * 4;
        const eyeOffsetY = this.direction.y * 4;
        this.graphics.fillStyle(0xffffff, 1);
        this.graphics.fillCircle(x + this.gridSize / 2 + eyeOffsetX - 3, y + this.gridSize / 2 + eyeOffsetY - 2, 3);
        this.graphics.fillCircle(x + this.gridSize / 2 + eyeOffsetX + 3, y + this.gridSize / 2 + eyeOffsetY - 2, 3);
        this.graphics.fillStyle(0x000000, 1);
        this.graphics.fillCircle(x + this.gridSize / 2 + eyeOffsetX - 3, y + this.gridSize / 2 + eyeOffsetY - 2, 1.5);
        this.graphics.fillCircle(x + this.gridSize / 2 + eyeOffsetX + 3, y + this.gridSize / 2 + eyeOffsetY - 2, 1.5);
      } else {
        // Тело с градиентом
        const alpha = 1 - (index / this.snake.length) * 0.4;
        const green = Math.floor(255 - (index / this.snake.length) * 80);
        this.graphics.fillStyle(Phaser.Display.Color.GetColor(0, green, 100), alpha);
        this.graphics.fillRoundedRect(
          x + padding, y + padding,
          this.gridSize - padding * 2, this.gridSize - padding * 2,
          4
        );
      }
    });
  }
}




