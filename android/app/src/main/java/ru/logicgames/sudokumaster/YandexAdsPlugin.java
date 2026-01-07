package ru.logicgames.sudokumaster;

import android.app.Activity;
import android.util.Log;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import com.yandex.mobile.ads.common.AdError;
import com.yandex.mobile.ads.common.AdRequestConfiguration;
import com.yandex.mobile.ads.common.AdRequestError;
import com.yandex.mobile.ads.common.ImpressionData;
import com.yandex.mobile.ads.common.MobileAds;
import com.yandex.mobile.ads.interstitial.InterstitialAd;
import com.yandex.mobile.ads.interstitial.InterstitialAdEventListener;
import com.yandex.mobile.ads.interstitial.InterstitialAdLoadListener;
import com.yandex.mobile.ads.interstitial.InterstitialAdLoader;
import com.yandex.mobile.ads.rewarded.Reward;
import com.yandex.mobile.ads.rewarded.RewardedAd;
import com.yandex.mobile.ads.rewarded.RewardedAdEventListener;
import com.yandex.mobile.ads.rewarded.RewardedAdLoadListener;
import com.yandex.mobile.ads.rewarded.RewardedAdLoader;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

@CapacitorPlugin(name = "YandexAds")
public class YandexAdsPlugin extends Plugin {
    private static final String TAG = "YandexAdsPlugin";
    
    // Ad Unit ID от Яндекса
    private static final String REWARDED_AD_UNIT_ID = "R-M-18197198-1";
    private static final String INTERSTITIAL_AD_UNIT_ID = "R-M-18197198-2";
    
    private RewardedAdLoader rewardedAdLoader;
    private RewardedAd rewardedAd;
    
    private InterstitialAdLoader interstitialAdLoader;
    private InterstitialAd interstitialAd;
    
    private PluginCall pendingRewardedCall;
    private PluginCall pendingInterstitialCall;

    @Override
    public void load() {
        super.load();
        Log.d(TAG, "YandexAdsPlugin загружен");
        
        // Инициализация SDK на UI потоке
        getActivity().runOnUiThread(() -> {
            MobileAds.initialize(getContext(), () -> {
                Log.d(TAG, "Yandex Mobile Ads SDK инициализирован");
                setupRewardedAdLoader();
                setupInterstitialAdLoader();
            });
        });
    }
    
    private void setupRewardedAdLoader() {
        rewardedAdLoader = new RewardedAdLoader(getContext());
        rewardedAdLoader.setAdLoadListener(new RewardedAdLoadListener() {
            @Override
            public void onAdLoaded(@NonNull RewardedAd ad) {
                Log.d(TAG, "Rewarded реклама загружена");
                rewardedAd = ad;
                notifyListeners("rewardedAdLoaded", new JSObject());
            }

            @Override
            public void onAdFailedToLoad(@NonNull AdRequestError error) {
                Log.e(TAG, "Ошибка загрузки Rewarded рекламы: " + error.getDescription());
                JSObject data = new JSObject();
                data.put("error", error.getDescription());
                notifyListeners("rewardedAdFailedToLoad", data);
            }
        });
        
        // Загрузка только по требованию (при нажатии кнопки)
        // loadRewardedAdInternal();
    }
    
    private void setupInterstitialAdLoader() {
        interstitialAdLoader = new InterstitialAdLoader(getContext());
        interstitialAdLoader.setAdLoadListener(new InterstitialAdLoadListener() {
            @Override
            public void onAdLoaded(@NonNull InterstitialAd ad) {
                Log.d(TAG, "Interstitial реклама загружена");
                interstitialAd = ad;
                notifyListeners("interstitialAdLoaded", new JSObject());
            }

            @Override
            public void onAdFailedToLoad(@NonNull AdRequestError error) {
                Log.e(TAG, "Ошибка загрузки Interstitial рекламы: " + error.getDescription());
                JSObject data = new JSObject();
                data.put("error", error.getDescription());
                notifyListeners("interstitialAdFailedToLoad", data);
            }
        });
        
        // Загрузка только по требованию (при нажатии кнопки)
        // loadInterstitialAdInternal();
    }
    
    private void loadRewardedAdInternal() {
        AdRequestConfiguration config = new AdRequestConfiguration.Builder(REWARDED_AD_UNIT_ID).build();
        rewardedAdLoader.loadAd(config);
        Log.d(TAG, "Начата загрузка Rewarded рекламы");
    }
    
    private void loadInterstitialAdInternal() {
        AdRequestConfiguration config = new AdRequestConfiguration.Builder(INTERSTITIAL_AD_UNIT_ID).build();
        interstitialAdLoader.loadAd(config);
        Log.d(TAG, "Начата загрузка Interstitial рекламы");
    }

    @PluginMethod
    public void loadRewardedAd(PluginCall call) {
        getActivity().runOnUiThread(() -> {
            loadRewardedAdInternal();
            call.resolve();
        });
    }
    
    @PluginMethod
    public void loadInterstitialAd(PluginCall call) {
        getActivity().runOnUiThread(() -> {
            loadInterstitialAdInternal();
            call.resolve();
        });
    }

    @PluginMethod
    public void showRewardedAd(PluginCall call) {
        getActivity().runOnUiThread(() -> {
            if (rewardedAd == null) {
                JSObject result = new JSObject();
                result.put("success", false);
                result.put("error", "Реклама ещё не загружена");
                call.resolve(result);
                return;
            }
            
            pendingRewardedCall = call;
            
            rewardedAd.setAdEventListener(new RewardedAdEventListener() {
                @Override
                public void onAdShown() {
                    Log.d(TAG, "Rewarded реклама показана");
                    notifyListeners("rewardedAdShown", new JSObject());
                }

                @Override
                public void onAdFailedToShow(@NonNull AdError error) {
                    Log.e(TAG, "Ошибка показа Rewarded рекламы: " + error.getDescription());
                    if (pendingRewardedCall != null) {
                        JSObject result = new JSObject();
                        result.put("success", false);
                        result.put("error", error.getDescription());
                        pendingRewardedCall.resolve(result);
                        pendingRewardedCall = null;
                    }
                }

                @Override
                public void onAdDismissed() {
                    Log.d(TAG, "Rewarded реклама закрыта");
                    rewardedAd = null;
                    // Автоматическая перезагрузка отключена - загрузка только по требованию
                    // loadRewardedAdInternal();
                    notifyListeners("rewardedAdDismissed", new JSObject());
                }

                @Override
                public void onAdClicked() {
                    Log.d(TAG, "Клик по Rewarded рекламе");
                    notifyListeners("rewardedAdClicked", new JSObject());
                }

                @Override
                public void onAdImpression(@Nullable ImpressionData data) {
                    Log.d(TAG, "Impression Rewarded рекламы");
                }

                @Override
                public void onRewarded(@NonNull Reward reward) {
                    Log.d(TAG, "Награда получена: " + reward.getAmount() + " " + reward.getType());
                    if (pendingRewardedCall != null) {
                        JSObject result = new JSObject();
                        result.put("success", true);
                        result.put("rewardAmount", reward.getAmount());
                        result.put("rewardType", reward.getType());
                        pendingRewardedCall.resolve(result);
                        pendingRewardedCall = null;
                    }
                    JSObject data = new JSObject();
                    data.put("amount", reward.getAmount());
                    data.put("type", reward.getType());
                    notifyListeners("rewardedAdRewarded", data);
                }
            });
            
            rewardedAd.show(getActivity());
        });
    }

    @PluginMethod
    public void showInterstitialAd(PluginCall call) {
        getActivity().runOnUiThread(() -> {
            if (interstitialAd == null) {
                JSObject result = new JSObject();
                result.put("success", false);
                result.put("error", "Реклама ещё не загружена");
                call.resolve(result);
                return;
            }
            
            pendingInterstitialCall = call;
            
            interstitialAd.setAdEventListener(new InterstitialAdEventListener() {
                @Override
                public void onAdShown() {
                    Log.d(TAG, "Interstitial реклама показана");
                    notifyListeners("interstitialAdShown", new JSObject());
                }

                @Override
                public void onAdFailedToShow(@NonNull AdError error) {
                    Log.e(TAG, "Ошибка показа Interstitial рекламы: " + error.getDescription());
                    if (pendingInterstitialCall != null) {
                        JSObject result = new JSObject();
                        result.put("success", false);
                        result.put("error", error.getDescription());
                        pendingInterstitialCall.resolve(result);
                        pendingInterstitialCall = null;
                    }
                }

                @Override
                public void onAdDismissed() {
                    Log.d(TAG, "Interstitial реклама закрыта");
                    interstitialAd = null;
                    // Автоматическая перезагрузка отключена - загрузка только по требованию
                    // loadInterstitialAdInternal();
                    if (pendingInterstitialCall != null) {
                        JSObject result = new JSObject();
                        result.put("success", true);
                        pendingInterstitialCall.resolve(result);
                        pendingInterstitialCall = null;
                    }
                    notifyListeners("interstitialAdDismissed", new JSObject());
                }

                @Override
                public void onAdClicked() {
                    Log.d(TAG, "Клик по Interstitial рекламе");
                    notifyListeners("interstitialAdClicked", new JSObject());
                }

                @Override
                public void onAdImpression(@Nullable ImpressionData data) {
                    Log.d(TAG, "Impression Interstitial рекламы");
                }
            });
            
            interstitialAd.show(getActivity());
        });
    }
    
    @PluginMethod
    public void isRewardedAdReady(PluginCall call) {
        JSObject result = new JSObject();
        result.put("ready", rewardedAd != null);
        call.resolve(result);
    }
    
    @PluginMethod
    public void isInterstitialAdReady(PluginCall call) {
        JSObject result = new JSObject();
        result.put("ready", interstitialAd != null);
        call.resolve(result);
    }
}

