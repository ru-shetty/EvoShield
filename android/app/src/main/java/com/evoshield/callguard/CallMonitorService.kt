package com.evoshield.callguard

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import java.util.Locale

class CallMonitorService : Service(), RecognitionListener {
    private var recognizer: SpeechRecognizer? = null
    private val handler = Handler(Looper.getMainLooper())
    private var running = false
    private var noSpeechCount = 0
    private var lastAlertCategory = "NORMAL"
    private val recentUtterances = ArrayDeque<String>()

    override fun onCreate() {
        super.onCreate()
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(NotificationChannel(CHANNEL, "Call protection", NotificationManager.IMPORTANCE_HIGH))
        startForeground(NOTIFICATION_ID, statusNotification("Starting on-device speech recognition"), ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            stopMonitoring()
            return START_NOT_STICKY
        }
        if (Build.VERSION.SDK_INT < 31 || !SpeechRecognizer.isOnDeviceRecognitionAvailable(this)) {
            updateStatus("On-device speech recognition is not available on this phone")
            stopMonitoring()
            return START_NOT_STICKY
        }
        running = true
        recognizer = SpeechRecognizer.createOnDeviceSpeechRecognizer(this).also { it.setRecognitionListener(this) }
        startListening()
        return START_NOT_STICKY
    }

    private fun startListening() {
        if (!running) return
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault().toLanguageTag())
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
        }
        try {
            recognizer?.startListening(intent)
            updateStatus("Listening locally. Use speakerphone for the clearest call audio.")
        } catch (_: Exception) {
            updateStatus("Call audio is not available to EvoShield. Try speakerphone and restart monitoring.")
        }
    }

    override fun onPartialResults(results: Bundle?) = analyzeResults(results)

    override fun onResults(results: Bundle?) {
        analyzeResults(results)
        if (running) handler.postDelayed(::startListening, 250)
    }

    override fun onError(error: Int) {
        if (!running) return
        if (error == SpeechRecognizer.ERROR_NO_MATCH || error == SpeechRecognizer.ERROR_SPEECH_TIMEOUT) {
            noSpeechCount++
            if (noSpeechCount >= 4) updateStatus("No call speech is reaching EvoShield. WhatsApp may own the microphone; try speakerphone.")
        } else if (error == SpeechRecognizer.ERROR_RECOGNIZER_BUSY) {
            updateStatus("The microphone is busy with the call. EvoShield cannot hear it on this device.")
        } else {
            updateStatus("Speech capture paused. Check microphone permission and try again.")
        }
        handler.postDelayed(::startListening, 1200)
    }

    private fun analyzeResults(bundle: Bundle?) {
        val text = bundle?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()?.trim().orEmpty()
        if (text.isBlank()) return
        noSpeechCount = 0
        if (recentUtterances.isEmpty() || recentUtterances.last() != text) recentUtterances.addLast(text)
        while (recentUtterances.size > 8) recentUtterances.removeFirst()
        val detection = DigitalArrestDetector.analyze(recentUtterances.joinToString(" "))
        if (detection.category == "DIGITAL_ARREST" || detection.category == "SUSPICIOUS") {
            updateStatus("${detection.category.replace('_', ' ')} · ${(detection.probability * 100).toInt()}% · ${detection.indicators.joinToString()}")
            if (detection.category != lastAlertCategory || lastAlertCategory == "NORMAL") showThreat(detection)
            lastAlertCategory = detection.category
        } else {
            lastAlertCategory = "NORMAL"
        }
    }

    private fun showThreat(detection: Detection) {
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(ALERT_ID, Notification.Builder(this, CHANNEL)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(if (detection.category == "DIGITAL_ARREST") "Possible digital-arrest scam" else "Suspicious call language")
            .setContentText("${detection.indicators.joinToString()}. Never share OTPs or transfer money under pressure.")
            .setCategory(Notification.CATEGORY_ALARM)
            .setPriority(Notification.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build())
    }

    private fun statusNotification(message: String): Notification {
        val stop = PendingIntent.getService(this, 0, Intent(this, CallMonitorService::class.java).setAction(ACTION_STOP), PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        return Notification.Builder(this, CHANNEL)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentTitle("EvoShield call monitoring is active")
            .setContentText(message)
            .setOngoing(true)
            .addAction(0, "Stop", stop)
            .build()
    }

    private fun updateStatus(message: String) {
        getSharedPreferences(PREFS, MODE_PRIVATE).edit().putString("status", message).apply()
        getSystemService(NotificationManager::class.java).notify(NOTIFICATION_ID, statusNotification(message))
    }

    private fun stopMonitoring() {
        running = false
        getSharedPreferences(PREFS, MODE_PRIVATE).edit().putString("status", "Monitoring stopped.").apply()
        handler.removeCallbacksAndMessages(null)
        recognizer?.destroy()
        recognizer = null
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    override fun onDestroy() {
        running = false
        handler.removeCallbacksAndMessages(null)
        recognizer?.destroy()
        recognizer = null
        super.onDestroy()
    }

    override fun onReadyForSpeech(params: Bundle?) { }
    override fun onBeginningOfSpeech() { }
    override fun onRmsChanged(rmsdB: Float) { }
    override fun onBufferReceived(buffer: ByteArray?) { }
    override fun onEndOfSpeech() { }
    override fun onEvent(eventType: Int, params: Bundle?) { }
    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        const val ACTION_STOP = "com.evoshield.callguard.STOP"
        const val PREFS = "call_monitor"
        private const val CHANNEL = "evoshield_call_monitor"
        private const val NOTIFICATION_ID = 7101
        private const val ALERT_ID = 7102
    }
}
