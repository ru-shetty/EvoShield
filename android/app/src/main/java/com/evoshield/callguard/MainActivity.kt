package com.evoshield.callguard

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.provider.Settings
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import org.json.JSONArray
import java.text.DateFormat
import java.util.Date

class MainActivity : Activity() {
    private lateinit var status: TextView
    private lateinit var notificationStatus: TextView
    private lateinit var history: LinearLayout
    private val requestCode = 301

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(36, 48, 36, 24)
        }
        val page = ScrollView(this)
        page.addView(layout)
        layout.addView(TextView(this).apply { text = "EvoShield Protection"; textSize = 26f })
        layout.addView(TextView(this).apply {
            text = "Checks visible message notifications from WhatsApp, Google/Samsung Messages, Telegram, Signal, and Messenger. Text and links are analyzed on this phone; notification content is not uploaded."
            textSize = 14f
            setPadding(0, 14, 0, 14)
        })
        layout.addView(Button(this).apply {
            text = "Enable message and link checks"
            setOnClickListener { startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)) }
        })
        notificationStatus = TextView(this).apply {
            textSize = 13f
            setPadding(0, 8, 0, 20)
        }
        layout.addView(notificationStatus)
        layout.addView(TextView(this).apply {
            text = "Only supported messaging apps are inspected. Notification previews may be incomplete if your phone hides message text."
            textSize = 13f
            setPadding(0, 8, 0, 20)
        })
        layout.addView(TextView(this).apply {
            textSize = 16f
            text = "Start monitoring only when you are on a call. Speech is analyzed on this phone when on-device recognition is available. No call audio or transcript is saved. Android may prevent access to WhatsApp call audio; speakerphone may be required."
            setPadding(0, 20, 0, 24)
        })
        status = TextView(this).apply { textSize = 16f; text = "Monitoring is off."; setPadding(0, 0, 0, 24) }
        layout.addView(status)
        layout.addView(Button(this).apply { text = "Start call monitoring"; setOnClickListener { requestStart() } })
        layout.addView(Button(this).apply { text = "Stop monitoring"; setOnClickListener { stopMonitoring() } })
        layout.addView(TextView(this).apply { text = "Recent call alerts"; textSize = 20f; setPadding(0, 28, 0, 8) })
        layout.addView(TextView(this).apply { text = "Only alert summaries are saved on this phone. Call audio and transcripts are not stored."; textSize = 13f; setPadding(0, 0, 0, 12) })
        history = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        layout.addView(history)
        setContentView(page)
    }

    override fun onResume() {
        super.onResume()
        status.text = getSharedPreferences(CallMonitorService.PREFS, MODE_PRIVATE).getString("status", "Monitoring is off.")
            ?: "Monitoring is off."
        val listeners = Settings.Secure.getString(contentResolver, "enabled_notification_listeners").orEmpty()
        notificationStatus.text = if (listeners.contains(packageName)) {
            "Message and link checks: enabled"
        } else {
            "Message and link checks: off. Tap Enable message and link checks, then grant access in Android Settings."
        }
        showHistory()
    }

    private fun showHistory() {
        history.removeAllViews()
        val prefs = getSharedPreferences(CallMonitorService.PREFS, MODE_PRIVATE)
        val raw = prefs.getString(LocalEntityHistory.KEY, "[]")
        val alerts = try { JSONArray(raw) } catch (_: Exception) { JSONArray() }
        val oldCalls = try { JSONArray(prefs.getString(CallMonitorService.ALERT_HISTORY, "[]")) } catch (_: Exception) { JSONArray() }
        if (alerts.length() == 0 && oldCalls.length() == 0) {
            history.addView(TextView(this).apply { text = "No checked items yet. Enable notification access or start call monitoring."; textSize = 15f; setPadding(0, 8, 0, 16) })
            return
        }
        for (index in 0 until alerts.length()) {
            val item = alerts.optJSONObject(index) ?: continue
            val risk = when (item.optString("verdict")) {
                "HIGH" -> "High risk"
                "MEDIUM" -> "Suspicious"
                "REVIEW" -> "Needs review"
                else -> "Lower risk"
            }
            val title = "${item.optString("type", "Checked item")}: ${item.optString("subject", "")} · $risk"
            val time = DateFormat.getDateTimeInstance(DateFormat.MEDIUM, DateFormat.SHORT)
                .format(Date(item.optLong("time")))
            history.addView(TextView(this).apply {
                text = "$title\n${item.optString("summary")}\n${item.optString("source")} · $time"
                textSize = 14f
                setPadding(0, 12, 0, 12)
            })
        }
        for (index in 0 until oldCalls.length()) {
            val item = oldCalls.optJSONObject(index) ?: continue
            val title = if (item.optString("category") == "DIGITAL_ARREST") "Call alert: high risk" else "Call alert: suspicious"
            history.addView(TextView(this).apply {
                text = "$title\n${item.optString("reasons")}"
                textSize = 14f
                setPadding(0, 12, 0, 12)
            })
        }
    }

    private fun requestStart() {
        val permissions = mutableListOf(Manifest.permission.RECORD_AUDIO)
        if (Build.VERSION.SDK_INT >= 33) permissions += Manifest.permission.POST_NOTIFICATIONS
        val missing = permissions.filter { checkSelfPermission(it) != PackageManager.PERMISSION_GRANTED }
        if (missing.isNotEmpty()) requestPermissions(missing.toTypedArray(), requestCode) else startMonitoring()
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        val micGranted = checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED
        val notificationsGranted = Build.VERSION.SDK_INT < 33 || checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
        if (requestCode == this.requestCode && micGranted && notificationsGranted) {
            startMonitoring()
        } else if (!micGranted) {
            status.text = "Microphone permission is required to analyze call speech."
        } else {
            status.text = "Notification permission is required to show when monitoring is active and warn during a call."
        }
    }

    private fun startMonitoring() {
        val intent = Intent(this, CallMonitorService::class.java)
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(intent) else startService(intent)
        status.text = "Starting. Return to WhatsApp and use speakerphone if needed."
    }

    private fun stopMonitoring() {
        stopService(Intent(this, CallMonitorService::class.java))
        status.text = "Monitoring stopped."
    }
}
