import Phaser from 'phaser';
import YandexAds from '../plugins/YandexAds';

export class MenuScene extends Phaser.Scene {
  private b1Ready: boolean = false;
  private b2Ready: boolean = false;

  constructor() {
    super({ key: 'MenuScene' });
  }

  create() {
    const { width, height } = this.scale;

    // Фоновый градиент
    this.createBackground(width, height);

    // Декоративные частицы
    this.createParticles(width, height);

    // Название
    const titleText = this.add.text(width / 2, height * 0.12, 'ТЕСТ РЕКЛАМЫ\nЯНДЕКС', {
      fontFamily: 'Arial Black, Arial, sans-serif',
      fontSize: '42px',
      color: '#ff6b00',
      align: 'center',
      stroke: '#442200',
      strokeThickness: 6,
      shadow: {
        offsetX: 0,
        offsetY: 0,
        color: '#ff6b00',
        blur: 20,
        fill: true
      }
    });
    titleText.setOrigin(0.5);

    // Анимация пульсации
    this.tweens.add({
      targets: titleText,
      scaleX: 1.05,
      scaleY: 1.05,
      duration: 1500,
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1
    });

    // Информация о Ad Unit ID внизу
    const infoText = this.add.text(width / 2, height * 0.92, 
      'Ad Unit ID:\n' +
      'R-M-17963472-2 (Rewarded)\n' +
      'R-M-17963472-1 (Interstitial)', {
      fontFamily: 'Arial, sans-serif',
      fontSize: '11px',
      color: '#444444',
      align: 'center'
    });
    infoText.setOrigin(0.5);

    // Настраиваем HTML кнопки
    this.setupHtmlButtons();
    
    // Начальный статус
    const statusEl = document.getElementById('status-text');
    if (statusEl) {
      statusEl.textContent = 'Нажмите кнопку для загрузки рекламы';
      statusEl.style.color = '#aaaaaa';
    }
  }

  private setupHtmlButtons() {
    const b1 = document.getElementById('b1');
    const b2 = document.getElementById('b2');

    if (b1) {
      b1.onclick = async () => {
        this.showStatus('Загружаю Rewarded рекламу...');
        
        try {
          // Загружаем рекламу
          await YandexAds.loadRewardedAd();
          
          // Ждём загрузки (максимум 15 секунд)
          let attempts = 0;
          const maxAttempts = 75; // 75 * 200ms = 15 секунд
          
          while (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 200));
            const ready = await YandexAds.isRewardedAdReady();
            
            if (ready.ready) {
              // Реклама загружена, показываем
              this.showStatus('Показываю Rewarded рекламу...');
              const result = await YandexAds.showRewardedAd();
              
              if (result.success) {
                this.showStatus(`✓ Награда: ${result.rewardAmount} ${result.rewardType}`, '#00ff88');
              } else {
                this.showStatus(`✗ Ошибка: ${result.error}`, '#ff4444');
              }
              return;
            }
            attempts++;
          }
          
          // Реклама не загрузилась за 15 секунд
          this.showStatus('✗ Рекламы нет', '#ff4444');
          
        } catch (e: any) {
          this.showStatus(`✗ Рекламы нет`, '#ff4444');
        }
      };
    }

    if (b2) {
      b2.onclick = async () => {
        this.showStatus('Загружаю Interstitial рекламу...');
        
        try {
          // Загружаем рекламу
          await YandexAds.loadInterstitialAd();
          
          // Ждём загрузки (максимум 15 секунд)
          let attempts = 0;
          const maxAttempts = 75; // 75 * 200ms = 15 секунд
          
          while (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 200));
            const ready = await YandexAds.isInterstitialAdReady();
            
            if (ready.ready) {
              // Реклама загружена, показываем
              this.showStatus('Показываю Interstitial рекламу...');
              const result = await YandexAds.showInterstitialAd();
              
              if (result.success) {
                this.showStatus('✓ Interstitial показан успешно', '#00ff88');
              } else {
                this.showStatus(`✗ Ошибка: ${result.error}`, '#ff4444');
              }
              return;
            }
            attempts++;
          }
          
          // Реклама не загрузилась за 15 секунд
          this.showStatus('✗ Рекламы нет', '#ff4444');
          
        } catch (e: any) {
          this.showStatus(`✗ Рекламы нет`, '#ff4444');
        }
      };
    }
  }

  private async checkAdsReady() {
    try {
      const [rewarded, interstitial] = await Promise.all([
        YandexAds.isRewardedAdReady(),
        YandexAds.isInterstitialAdReady()
      ]);
      
      this.b1Ready = rewarded.ready;
      this.b2Ready = interstitial.ready;
      
      const status = `B1 (Rewarded): ${this.b1Ready ? '✓ Готово' : '⏳ Загрузка...'}\n` +
                     `B2 (Interstitial): ${this.b2Ready ? '✓ Готово' : '⏳ Загрузка...'}`;
      
      const statusEl = document.getElementById('status-text');
      if (statusEl && !statusEl.textContent?.includes('✗') && 
          !statusEl.textContent?.includes('Награда') &&
          !statusEl.textContent?.includes('успешно')) {
        statusEl.textContent = status;
        statusEl.style.color = '#aaaaaa';
      }
    } catch (e) {
      const statusEl = document.getElementById('status-text');
      if (statusEl) {
        statusEl.textContent = 'Плагин недоступен\n(запустите на Android)';
        statusEl.style.color = '#ff6b00';
      }
    }
  }

  private showStatus(text: string, color: string = '#ffffff') {
    const statusEl = document.getElementById('status-text');
    if (statusEl) {
      statusEl.textContent = text;
      statusEl.style.color = color;
    }
    
    // Сброс статуса через 3 секунды
    this.time.delayedCall(3000, () => {
      this.checkAdsReady();
    });
  }

  private createBackground(width: number, height: number) {
    const graphics = this.add.graphics();
    
    for (let y = 0; y < height; y += 4) {
      const ratio = y / height;
      const r = Math.floor(10 + ratio * 15);
      const g = Math.floor(10 + ratio * 10);
      const b = Math.floor(15 + ratio * 30);
      graphics.fillStyle(Phaser.Display.Color.GetColor(r, g, b), 1);
      graphics.fillRect(0, y, width, 4);
    }

    graphics.lineStyle(1, 0x1a1a2e, 0.5);
    const gridSize = 40;
    for (let x = 0; x < width; x += gridSize) {
      graphics.lineBetween(x, 0, x, height);
    }
    for (let y = 0; y < height; y += gridSize) {
      graphics.lineBetween(0, y, width, y);
    }
  }

  private createParticles(width: number, height: number) {
    for (let i = 0; i < 15; i++) {
      const particle = this.add.circle(
        Phaser.Math.Between(0, width),
        Phaser.Math.Between(0, height),
        Phaser.Math.Between(1, 3),
        0xff6b00,
        Phaser.Math.FloatBetween(0.1, 0.3)
      );

      this.tweens.add({
        targets: particle,
        y: particle.y - Phaser.Math.Between(50, 150),
        alpha: 0,
        duration: Phaser.Math.Between(3000, 6000),
        ease: 'Linear',
        repeat: -1,
        onRepeat: () => {
          particle.y = height + 10;
          particle.x = Phaser.Math.Between(0, width);
          particle.alpha = Phaser.Math.FloatBetween(0.1, 0.3);
        }
      });
    }
  }
}
