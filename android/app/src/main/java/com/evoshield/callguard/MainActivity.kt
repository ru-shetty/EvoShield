package com.evoshield.callguard

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var status: TextView
    private val requestCode = 301

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(36, 48, 36, 24)
        }
        layout.addView(TextView(this).apply { text = "EvoShield Call Guard"; textSize = 26f })
        layout.addView(TextView(this).apply {
            textSize = 16f
            text = "Start monitoring only when you are on a call. Speech is analyzed on this phone when on-device recognition is available. No call audio or transcript is saved. Android may prevent access to WhatsApp call audio; speakerphone may be required."
            setPadding(0, 20, 0, 24)
        })
        status = TextView(this).apply { textSize = 16f; text = "Monitoring is off."; setPadding(0, 0, 0, 24) }
        layout.addView(status)
        layout.addView(Button(this).apply { text = "Start call monitoring"; setOnClickListener { requestStart() } })
        layout.addView(Button(this).apply { text = "Stop monitoring"; setOnClickListener { stopMonitoring() } })
        setContentView(layout)
    }

    override fun onResume() {
        super.onResume()
        status.text = getSharedPreferences(CallMonitorService.PREFS, MODE_PRIVATE).getString("status", "Monitoring is off.")
            ?: "Monitoring is off."
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
