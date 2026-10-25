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
import org.json.JSONArray
import org.json.JSONObject
import java.util.Date
import java.util.Locale

class CallMonitorService : Service(), RecognitionListener {
    private var recognizer: SpeechRecognizer? = null
    private val handler = Handler(Looper.getMainLooper())
    private var running = false
    private var noSpeechCount = 0
    private var lastAlertCategory = "NORMAL"
    private var callType = "voice"
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
        callType = when (intent?.getStringExtra(EXTRA_CALL_TYPE)) {
            "video" -> "video"
            "both" -> "both"
            else -> "voice"
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
            val modeLabel = when (callType) { "video" -> "video call"; "both" -> "voice and video calls"; else -> "voice call" }
            updateStatus("Listening for scam speech in $modeLabel locally. Use speakerphone for the clearest audio.")
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
        val detection = DigitalArrestDetector.analyze(recentUtterances.joinToString(" "), callType)
        if (detection.category == "DIGITAL_ARREST" || detection.category == "SUSPICIOUS") {
            val reasons = detection.indicators.joinToString(" ") { explainIndicator(it) }
            val statusMessage = if (detection.category == "DIGITAL_ARREST") {
                "Possible digital-arrest scam. $reasons"
            } else {
                "Suspicious call language. $reasons"
            }
            updateStatus(statusMessage)
            if (detection.category != lastAlertCategory || lastAlertCategory == "NORMAL") showThreat(detection)
            lastAlertCategory = detection.category
        } else {
            lastAlertCategory = "NORMAL"
        }
    }

    private fun showThreat(detection: Detection) {
        val manager = getSystemService(NotificationManager::class.java)
        val reasons = detection.indicators.joinToString(" ") { explainIndicator(it) }
        saveAlert(detection.category, reasons, callType)
        val callLabel = when (callType) { "video" -> "Video call"; "both" -> "Voice and video calls"; else -> "Voice call" }
        LocalEntityHistory.add(this, "Call alert", callLabel, "$callLabel scam warning",
            if (detection.category == "DIGITAL_ARREST") "HIGH" else "MEDIUM", reasons)
        manager.notify(ALERT_ID, Notification.Builder(this, CHANNEL)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(if (detection.category == "DIGITAL_ARREST") "Possible digital-arrest scam in $callLabel" else "Suspicious $callLabel language")
            .setContentText("$reasons Never share one-time codes or transfer money under pressure.")
            .setCategory(Notification.CATEGORY_ALARM)
            .setPriority(Notification.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build())
    }

    private fun saveAlert(category: String, reasons: String, callType: String) {
        val prefs = getSharedPreferences(PREFS, MODE_PRIVATE)
        val old = try { JSONArray(prefs.getString(ALERT_HISTORY, "[]")) } catch (_: Exception) { JSONArray() }
        val updated = JSONArray()
        updated.put(JSONObject().put("category", category).put("reasons", reasons).put("call_type", callType).put("time", System.currentTimeMillis()))
        for (index in 0 until minOf(old.length(), MAX_SAVED_ALERTS - 1)) updated.put(old.getJSONObject(index))
        prefs.edit().putString(ALERT_HISTORY, updated.toString()).apply()
    }

    private fun explainIndicator(indicator: String): String = when (indicator) {
        "government/police impersonation" -> "The caller claims to be police or another government authority."
        "threat language" -> "They threaten arrest or legal action."
        "urgency" -> "They pressure you to act immediately."
        "financial request" -> "They ask you to pay or transfer money."
        "sensitive information request" -> "They ask for an OTP, PIN, identity number, or banking details."
        "fake document" -> "They refer to an official-looking notice or warrant."
        "call pressure" -> "They pressure you to stay on the call or keep it secret."
        "video call manipulation" -> "They pressure you to keep your camera on, show identity documents, or share your screen."
        else -> "The call contains language commonly used to pressure or frighten people."
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
        const val EXTRA_CALL_TYPE = "call_type"
        const val PREFS = "call_monitor"
        const val ALERT_HISTORY = "alert_history"
        private const val MAX_SAVED_ALERTS = 50
        const val CHANNEL = "evoshield_call_monitor"
        private const val NOTIFICATION_ID = 7101
        private const val ALERT_ID = 7102
    }
}
