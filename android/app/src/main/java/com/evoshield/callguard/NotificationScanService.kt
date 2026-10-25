package com.evoshield.callguard

import android.app.Notification
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import java.net.URI

class NotificationScanService : NotificationListenerService() {
    private val urlPattern = Regex("(?i)(?:https?://)?(?:www\\.)?[a-z0-9][a-z0-9.-]*\\.[a-z]{2,}(?:/[^\\s<>]*)?")
    private val supportedPackages = setOf(
        "com.whatsapp", "com.whatsapp.w4b", "com.google.android.apps.messaging",
        "com.samsung.android.messaging", "com.android.mms", "org.telegram.messenger",
        "org.thoughtcrime.securesms", "com.facebook.orca"
    )

    override fun onListenerConnected() {
        super.onListenerConnected()
        val manager = getSystemService(android.app.NotificationManager::class.java)
        manager.createNotificationChannel(android.app.NotificationChannel(
            CallMonitorService.CHANNEL, "EvoShield protection", android.app.NotificationManager.IMPORTANCE_HIGH
        ))
    }

    override fun onNotificationPosted(notification: StatusBarNotification) {
        if (notification.packageName !in supportedPackages) return
        val extras = notification.notification.extras ?: return
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString().orEmpty()
        val body = buildList {
            add(extras.getCharSequence(Notification.EXTRA_TEXT)?.toString().orEmpty())
            add(extras.getCharSequence(Notification.EXTRA_BIG_TEXT)?.toString().orEmpty())
            extras.getCharSequenceArray(Notification.EXTRA_TEXT_LINES)?.forEach { add(it.toString()) }
        }.filter(String::isNotBlank).distinct().joinToString(" ").take(4000)
        if (body.isBlank()) return

        val dedupe = "${notification.packageName}:${notification.id}:${body.hashCode()}"
        val prefs = getSharedPreferences(CallMonitorService.PREFS, MODE_PRIVATE)
        val old = prefs.getString("notification_seen", "").orEmpty().split('|').filter(String::isNotBlank)
        if (dedupe in old) return
        prefs.edit().putString("notification_seen", (listOf(dedupe) + old.take(99)).joinToString("|")).apply()

        val source = appLabel(notification.packageName)
        val detection = DigitalArrestDetector.analyze("$title $body")
        val messageVerdict = when (detection.category) {
            "DIGITAL_ARREST" -> "HIGH"
            "SUSPICIOUS" -> "MEDIUM"
            else -> "LOW"
        }
        val messageSummary = when (detection.category) {
            "DIGITAL_ARREST" -> "Possible digital-arrest scam: ${detection.indicators.joinToString()}. Do not pay or share codes under pressure."
            "SUSPICIOUS" -> "Suspicious message wording: ${detection.indicators.joinToString()}. Verify through a trusted contact."
            else -> "No strong digital-arrest warning signs were found in this notification preview."
        }
        LocalEntityHistory.add(this, "Message", source, title.ifBlank { "Message notification" }, messageVerdict, messageSummary)

        urlPattern.findAll(body).map { it.value.trimEnd('.', ',', ')', ']', '?', '!') }.distinct().forEach { link ->
            val result = LocalUrlAnalyzer.analyze(link)
            val host = try { URI(if (link.startsWith("http")) link else "https://$link").host ?: "Website link" } catch (_: Exception) { "Website link" }
            LocalEntityHistory.add(this, "Website link", source, host, result.verdict, result.summary)
            if (result.verdict in setOf("HIGH", "MEDIUM", "REVIEW")) {
                getSystemService(android.app.NotificationManager::class.java).notify(
                    "url:$dedupe:$host".hashCode(),
                    Notification.Builder(this, CallMonitorService.CHANNEL)
                        .setSmallIcon(android.R.drawable.ic_dialog_alert)
                        .setContentTitle("Suspicious website link")
                        .setContentText("$host: ${result.summary}".take(220))
                        .setAutoCancel(true)
                        .build()
                )
            }
        }
        if (messageVerdict == "HIGH" || messageVerdict == "MEDIUM") {
            val manager = getSystemService(android.app.NotificationManager::class.java)
            manager.notify(dedupe.hashCode(), Notification.Builder(this, CallMonitorService.CHANNEL)
                .setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setContentTitle(if (messageVerdict == "HIGH") "Possible scam message" else "Suspicious message")
                .setContentText("$source: $messageSummary")
                .setAutoCancel(true)
                .build())
        }
    }

    private fun appLabel(packageName: String): String = try {
        packageManager.getApplicationLabel(packageManager.getApplicationInfo(packageName, 0)).toString()
    } catch (_: Exception) { packageName }
}
