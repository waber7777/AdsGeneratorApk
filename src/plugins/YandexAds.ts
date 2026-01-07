import { registerPlugin } from '@capacitor/core';

export interface RewardedResult {
  success: boolean;
  error?: string;
  rewardAmount?: number;
  rewardType?: string;
}

export interface InterstitialResult {
  success: boolean;
  error?: string;
}

export interface AdReadyResult {
  ready: boolean;
}

export interface YandexAdsPlugin {
  loadRewardedAd(): Promise<void>;
  loadInterstitialAd(): Promise<void>;
  showRewardedAd(): Promise<RewardedResult>;
  showInterstitialAd(): Promise<InterstitialResult>;
  isRewardedAdReady(): Promise<AdReadyResult>;
  isInterstitialAdReady(): Promise<AdReadyResult>;
}

const YandexAds = registerPlugin<YandexAdsPlugin>('YandexAds');

export default YandexAds;










