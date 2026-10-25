package com.evoshield.callguard

import android.Manifest
import android.app.Activity
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.graphics.Color
import android.graphics.Typeface
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.Spinner
import android.widget.TextView
import android.widget.ArrayAdapter
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import org.json.JSONArray
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MainActivity : Activity() {
    private lateinit var content: LinearLayout
    private lateinit var drawer: LinearLayout
    private lateinit var statusLine: TextView
    private var selected = "today"
    private val requestCode = 301
    private val notificationPermissionRequestCode = 302
    private val imageNotificationPermissionRequestCode = 303
    private val imagePickerRequestCode = 401
    private lateinit var callTypeSpinner: Spinner
    private lateinit var imageStatus: TextView

    private val background = Color.rgb(11, 18, 32)
    private val panel = Color.rgb(18, 29, 47)
    private val line = Color.rgb(38, 54, 75)
    private val primary = Color.rgb(242, 247, 252)
    private val muted = Color.rgb(151, 167, 189)
    private val accent = Color.rgb(100, 216, 200)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        buildShell()
        renderPage()
    }

    override fun onResume() {
        super.onResume()
        if (::statusLine.isInitialized) updateProtectionStatus()
        if (::content.isInitialized) renderPage()
    }

    private fun buildShell() {
        val root = FrameLayout(this).apply { setBackgroundColor(background) }
        val page = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(background)
        }
        val top = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(18), dp(12), dp(18), dp(12))
            setBackgroundColor(panel)
        }
        top.addView(Button(this).apply {
            text = "☰"
            textSize = 20f
            setTextColor(accent)
            setBackgroundColor(Color.TRANSPARENT)
            setOnClickListener { drawer.visibility = if (drawer.visibility == View.VISIBLE) View.GONE else View.VISIBLE }
        }, LinearLayout.LayoutParams(dp(48), dp(46)))
        top.addView(TextView(this).apply {
            text = "◈  EvoShield"
            textSize = 19f
            setTextColor(primary)
            setTypeface(null, Typeface.BOLD)
        }, LinearLayout.LayoutParams(0, dp(46), 1f))
        statusLine = TextView(this).apply { textSize = 11f; setTextColor(accent); gravity = Gravity.CENTER_VERTICAL }
        top.addView(statusLine)
        page.addView(top)

        val scroll = ScrollView(this)
        content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(22), dp(20), dp(36))
        }
        scroll.addView(content)
        page.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        root.addView(page)

        drawer = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(14), dp(22), dp(14), dp(18))
            setBackgroundColor(Color.rgb(13, 23, 39))
            visibility = View.GONE
            elevation = dp(12).toFloat()
        }
        drawer.addView(label("WORKSPACE"))
        navButton("Today", "today")
        navButton("History", "history")
        drawer.addView(label("CHECKED INPUTS"))
        navButton("Messages", "message")
        navButton("Website links", "url")
        navButton("Calls", "call")
        navButton("Files · not on Android", "file")
        navButton("Images", "image")
        drawer.addView(TextView(this).apply {
            text = "Messages and links are checked from visible notifications. Call monitoring is started by you."
            textSize = 12f
            setTextColor(muted)
            setPadding(dp(10), dp(24), dp(8), dp(8))
        })
        root.addView(drawer, FrameLayout.LayoutParams(dp(244), -1, Gravity.START))
        setContentView(root)
        updateProtectionStatus()
    }

    private fun label(text: String) = TextView(this).apply {
        this.text = text
        textSize = 10f
        letterSpacing = .12f
        setTextColor(muted)
        setPadding(dp(10), dp(16), dp(10), dp(8))
    }

    private fun navButton(title: String, route: String) {
        drawer.addView(Button(this).apply {
            text = title
            textSize = 14f
            gravity = Gravity.START or Gravity.CENTER_VERTICAL
            setTextColor(if (selected == route) accent else primary)
            setAllCaps(false)
            setBackgroundColor(if (selected == route) Color.rgb(23, 40, 58) else Color.TRANSPARENT)
            setPadding(dp(12), 0, dp(8), 0)
            setOnClickListener {
                selected = route
                for (index in 0 until drawer.childCount) {
                    val child = drawer.getChildAt(index)
                    if (child is Button) {
                        val active = child.text.toString() == title
                        child.setTextColor(if (active) accent else primary)
                        child.setBackgroundColor(if (active) Color.rgb(23, 40, 58) else Color.TRANSPARENT)
                    }
                }
                drawer.visibility = View.GONE
                renderPage()
            }
        }, LinearLayout.LayoutParams(-1, dp(46)))
    }

    private fun renderPage() {
        if (!::content.isInitialized) return
        content.removeAllViews()
        val title = when (selected) {
            "history" -> "History"
            "message" -> "Messages"
            "url" -> "Website links"
            "call" -> "Call protection"
            "file" -> "Files"
            "image" -> "Images"
            else -> "Today"
        }
        content.addView(TextView(this).apply {
            text = "PERSONAL SECURITY"
            textSize = 10f
            letterSpacing = .15f
            setTextColor(accent)
        })
        content.addView(TextView(this).apply {
            text = title
            textSize = 29f
            setTextColor(primary)
            setTypeface(null, Typeface.BOLD)
            setPadding(0, dp(4), 0, dp(4))
        })
        content.addView(TextView(this).apply {
            text = when (selected) {
                "today" -> "Your checked items from today, grouped by time."
                "history" -> "Browse saved checks by type and time."
                "call" -> "Start a call session or review saved call alerts."
                "image" -> "Choose an image to check its visible text for phishing and scam wording. OCR runs on this phone."
                "file" -> "File scanning is not available in this Android app. Use the Windows dashboard for supported file checks."
                else -> "Checks from visible supported-app notifications are saved on this phone."
            }
            textSize = 13f
            setTextColor(muted)
            setPadding(0, 0, 0, dp(18))
        })

        addOverviewCard()
        if (selected in setOf("today", "history", "message", "url")) addNotificationControls()
        if (selected == "call") addCallControls()
        if (selected == "image") {
            addImageControls()
            renderHistory()
            return
        }
        if (selected == "file") {
            addCardMessage("Android does not currently scan files. File checks are available from the Windows dashboard and configured Windows folders.")
            return
        }
        renderHistory()
    }

    private fun addOverviewCard() {
        val prefs = getSharedPreferences(CallMonitorService.PREFS, MODE_PRIVATE)
        val items = try { JSONArray(prefs.getString(LocalEntityHistory.KEY, "[]")) } catch (_: Exception) { JSONArray() }
        var todayCount = 0
        var highCount = 0
        var messageCount = 0
        var linkCount = 0
        val today = SimpleDateFormat("yyyyMMdd", Locale.getDefault()).format(Date())
        for (i in 0 until items.length()) {
            val item = items.optJSONObject(i) ?: continue
            if (SimpleDateFormat("yyyyMMdd", Locale.getDefault()).format(Date(item.optLong("time"))) == today) todayCount++
            if (item.optString("verdict") == "HIGH") highCount++
            if (item.optString("type") == "Message") messageCount++
            if (item.optString("type") == "Website link") linkCount++
        }
        val hero = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(18), dp(20), dp(18), dp(20))
            background = android.graphics.drawable.GradientDrawable(
                android.graphics.drawable.GradientDrawable.Orientation.TL_BR,
                intArrayOf(Color.rgb(13, 43, 66), Color.rgb(8, 23, 39), Color.rgb(11, 41, 53))
            ).apply { cornerRadius = dp(16).toFloat(); setStroke(dp(1), Color.rgb(31, 82, 111)) }
        }
        val copy = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        copy.addView(TextView(this).apply { text = "INTELLIGENT THREAT MONITORING"; textSize = 10f; letterSpacing = .12f; setTextColor(accent) })
        copy.addView(TextView(this).apply { text = "Welcome to EvoShield"; textSize = 21f; setTextColor(primary); setTypeface(null, Typeface.BOLD); setPadding(0, dp(4), 0, dp(4)) })
        copy.addView(TextView(this).apply { text = "Review messages, links, and call alerts checked on this phone."; textSize = 12f; setTextColor(muted) })
        hero.addView(copy, LinearLayout.LayoutParams(0, -2, 1f))
        hero.addView(TextView(this).apply { text = "⬡"; textSize = 48f; setTextColor(accent); gravity = Gravity.CENTER; setShadowLayer(dp(15).toFloat(), 0f, 0f, Color.rgb(16, 133, 201)) }, LinearLayout.LayoutParams(dp(58), -2))
        content.addView(hero, marginParams(bottom = 14))

        val first = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        first.addView(metricCard("CHECKS TODAY", todayCount.toString(), accent), LinearLayout.LayoutParams(0, -2, 1f).apply { rightMargin = dp(6) })
        first.addView(metricCard("HIGH RISK", highCount.toString(), Color.rgb(255, 125, 134)), LinearLayout.LayoutParams(0, -2, 1f).apply { leftMargin = dp(6) })
        content.addView(first, marginParams(bottom = 9))
        val second = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        second.addView(metricCard("MESSAGES", messageCount.toString(), Color.rgb(76, 150, 255)), LinearLayout.LayoutParams(0, -2, 1f).apply { rightMargin = dp(6) })
        second.addView(metricCard("WEBSITE LINKS", linkCount.toString(), Color.rgb(245, 198, 109)), LinearLayout.LayoutParams(0, -2, 1f).apply { leftMargin = dp(6) })
        content.addView(second, marginParams(bottom = 16))
    }

    private fun metricCard(title: String, value: String, tint: Int) = card().apply {
        addView(TextView(this@MainActivity).apply { text = title; textSize = 9f; letterSpacing = .08f; setTextColor(muted) })
        addView(TextView(this@MainActivity).apply { text = value; textSize = 25f; setTextColor(tint); setTypeface(null, Typeface.BOLD); setPadding(0, dp(4), 0, 0) })
    }

    private fun addImageControls() {
        val card = card()
        card.addView(TextView(this).apply {
            text = "Image text check"
            textSize = 16f
            setTextColor(primary)
            setTypeface(null, Typeface.BOLD)
        })
        card.addView(TextView(this).apply {
            text = "Choose an image from your phone. EvoShield reads visible text on-device, saves a short result in History, and notifies you if the wording looks suspicious. It does not upload or keep the image or extracted text."
            textSize = 13f
            setTextColor(muted)
            setPadding(0, dp(6), 0, dp(10))
        })
        card.addView(Button(this).apply {
            text = "Choose image and scan"
            setAllCaps(false)
            setOnClickListener {
                if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), imageNotificationPermissionRequestCode)
                } else launchImagePicker()
            }
        })
        imageStatus = TextView(this).apply { textSize = 13f; setTextColor(accent); setPadding(0, dp(10), 0, 0) }
        card.addView(imageStatus)
        content.addView(card, marginParams(bottom = 16))
    }

    private fun launchImagePicker() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "image/*"
        }
        startActivityForResult(intent, imagePickerRequestCode)
    }

    @Deprecated("Use Activity Result APIs")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != imagePickerRequestCode || resultCode != RESULT_OK) return
        val uri = data?.data ?: return
        scanSelectedImage(uri)
    }

    private fun scanSelectedImage(uri: Uri) {
        if (::imageStatus.isInitialized) imageStatus.text = "Reading visible text on this phone…"
        val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
        try {
            val image = InputImage.fromFilePath(this, uri)
            recognizer.process(image)
                .addOnSuccessListener { result ->
                    val extractedText = result.text
                    val subject = try {
                        contentResolver.query(uri, arrayOf(android.provider.OpenableColumns.DISPLAY_NAME), null, null, null)?.use { cursor ->
                            if (cursor.moveToFirst()) cursor.getString(0) else null
                        }
                    } catch (_: Exception) { null } ?: "Selected image"
                    val detection = if (extractedText.isBlank()) ImageTextDetection("LOW", "No readable text was found in this image.") else ImageTextThreatDetector.analyze(extractedText)
                    LocalEntityHistory.add(this, "Image", "On-device OCR", subject, detection.verdict, detection.summary)
                    if (detection.verdict == "HIGH" || detection.verdict == "MEDIUM") showImageThreat(subject, detection)
                    if (::imageStatus.isInitialized) imageStatus.text = "${if (detection.verdict == "LOW") "No strong warning signs" else detection.verdict + " risk"}: ${detection.summary}"
                    renderPage()
                }
                .addOnFailureListener { error ->
                    if (::imageStatus.isInitialized) imageStatus.text = "Could not read this image: ${error.localizedMessage ?: "OCR failed"}"
                }
                .addOnCompleteListener { recognizer.close() }
        } catch (error: Exception) {
            recognizer.close()
            if (::imageStatus.isInitialized) imageStatus.text = "Could not open this image: ${error.localizedMessage ?: "unsupported image"}"
        }
    }

    private fun showImageThreat(subject: String, detection: ImageTextDetection) {
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(NotificationChannel(CallMonitorService.CHANNEL, "EvoShield protection", NotificationManager.IMPORTANCE_HIGH))
        manager.notify((System.currentTimeMillis() and 0x7fffffff).toInt(), Notification.Builder(this, CallMonitorService.CHANNEL)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(if (detection.verdict == "HIGH") "High-risk wording in image" else "Suspicious wording in image")
            .setContentText("$subject: ${detection.summary}".take(220))
            .setAutoCancel(true)
            .build())
    }

    private fun addNotificationControls() {
        val enabled = Settings.Secure.getString(contentResolver, "enabled_notification_listeners").orEmpty().contains(packageName)
        val card = card()
        card.addView(TextView(this).apply {
            text = if (enabled) "Message and link monitoring is enabled" else "Turn on message and link checks"
            textSize = 15f
            setTextColor(primary)
            setTypeface(null, Typeface.BOLD)
        })
        card.addView(TextView(this).apply {
            text = "Checks visible notification previews from supported messaging apps. Results are stored on this phone."
            textSize = 12f
            setTextColor(muted)
            setPadding(0, dp(4), 0, dp(8))
        })
        if (!enabled) card.addView(Button(this).apply {
            text = "Enable message, link, and threat alerts"
            setAllCaps(false)
            setOnClickListener { requestNotificationAccess() }
        })
        content.addView(card, marginParams(bottom = 16))
    }

    private fun addCallControls() {
        val card = card()
        card.addView(TextView(this).apply {
            text = "Choose voice, video, or both. Both checks standard call-scam language plus video-call coercion cues. Analysis uses audio speech only; it does not inspect video frames. Android may require speakerphone for call audio."
            textSize = 13f
            setTextColor(muted)
        })
        callTypeSpinner = Spinner(this).apply {
            adapter = ArrayAdapter(this@MainActivity, android.R.layout.simple_spinner_dropdown_item, listOf("Voice call", "Video call", "Both voice and video calls"))
            setSelection(getSharedPreferences(CallMonitorService.PREFS, MODE_PRIVATE).getString("call_type", "voice").let { when (it) { "video" -> 1; "both" -> 2; else -> 0 } })
        }
        card.addView(callTypeSpinner)
        status = TextView(this).apply { textSize = 13f; setTextColor(accent); setPadding(0, dp(10), 0, dp(8)) }
        card.addView(status)
        card.addView(Button(this).apply { text = "Start call monitoring"; setAllCaps(false); setOnClickListener { requestStart() } })
        card.addView(Button(this).apply { text = "Stop monitoring"; setAllCaps(false); setOnClickListener { stopMonitoring() } })
        content.addView(card, marginParams(bottom = 16))
        updateCallStatus()
    }

    private lateinit var status: TextView

    private fun renderHistory() {
        val prefs = getSharedPreferences(CallMonitorService.PREFS, MODE_PRIVATE)
        val stored = try { JSONArray(prefs.getString(LocalEntityHistory.KEY, "[]")) } catch (_: Exception) { JSONArray() }
        val entries = (0 until stored.length()).mapNotNull { stored.optJSONObject(it) }
            .filter { item ->
                when (selected) {
                    "today" -> sameDay(item.optLong("time"), System.currentTimeMillis())
                    "message" -> item.optString("type") == "Message"
                    "url" -> item.optString("type") == "Website link"
                    "call" -> item.optString("type") == "Call alert"
                    "image" -> item.optString("type") == "Image"
                    else -> true
                }
            }
        val title = when (selected) {
            "today" -> "Recent checks today"
            "history" -> "All checked items"
            "message" -> "Message checks"
            "url" -> "Link checks"
            "call" -> "Call alerts"
            "image" -> "Image checks"
            else -> "Checked items"
        }
        content.addView(TextView(this).apply { text = title; textSize = 17f; setTextColor(primary); setTypeface(null, Typeface.BOLD); setPadding(0, dp(8), 0, dp(10)) })
        if (entries.isEmpty()) {
            addCardMessage(if (selected == "today") "No checks recorded today yet." else "No saved checks in this section yet.")
            return
        }
        var lastDate = ""
        for (item in entries) {
            val time = item.optLong("time")
            val dateKey = SimpleDateFormat("yyyyMMdd", Locale.getDefault()).format(Date(time))
            if (dateKey != lastDate) {
                lastDate = dateKey
                content.addView(TextView(this).apply {
                    text = if (dateKey == todayKey()) "TODAY" else DateFormat.getDateInstance(DateFormat.MEDIUM).format(Date(time)).uppercase(Locale.getDefault())
                    textSize = 10f
                    letterSpacing = .12f
                    setTextColor(muted)
                    setPadding(0, dp(10), 0, dp(4))
                })
            }
            val row = card()
            val verdict = when (item.optString("verdict")) {
                "HIGH" -> "HIGH RISK"
                "MEDIUM" -> "SUSPICIOUS"
                "REVIEW" -> "NEEDS REVIEW"
                else -> "LOWER RISK"
            }
            row.addView(TextView(this).apply { text = "${item.optString("type")}  ·  $verdict"; textSize = 12f; setTextColor(if (item.optString("verdict") == "HIGH") Color.rgb(255, 125, 134) else accent); setTypeface(null, Typeface.BOLD) })
            row.addView(TextView(this).apply { text = item.optString("subject"); textSize = 15f; setTextColor(primary); setPadding(0, dp(4), 0, dp(2)) })
            row.addView(TextView(this).apply { text = item.optString("summary"); textSize = 13f; setTextColor(muted) })
            row.addView(TextView(this).apply { text = "${item.optString("source")}  ·  ${DateFormat.getDateTimeInstance(DateFormat.MEDIUM, DateFormat.SHORT).format(Date(time))}"; textSize = 11f; setTextColor(muted); setPadding(0, dp(8), 0, 0) })
            content.addView(row, marginParams(bottom = 9))
        }
    }

    private fun addCardMessage(message: String) {
        val card = card()
        card.addView(TextView(this).apply { text = message; textSize = 14f; setTextColor(muted) })
        content.addView(card, marginParams(bottom = 12))
    }

    private fun card() = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        setPadding(dp(16), dp(15), dp(16), dp(15))
        setBackgroundColor(panel)
        background = android.graphics.drawable.GradientDrawable().apply {
            setColor(panel)
            cornerRadius = dp(14).toFloat()
            setStroke(dp(1), line)
        }
    }

    private fun marginParams(bottom: Int) = LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(bottom) }
    private fun sameDay(a: Long, b: Long) = SimpleDateFormat("yyyyMMdd", Locale.getDefault()).format(Date(a)) == SimpleDateFormat("yyyyMMdd", Locale.getDefault()).format(Date(b))
    private fun todayKey() = SimpleDateFormat("yyyyMMdd", Locale.getDefault()).format(Date())
    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()

    private fun updateProtectionStatus() {
        if (!::statusLine.isInitialized) return
        val listeners = Settings.Secure.getString(contentResolver, "enabled_notification_listeners").orEmpty()
        statusLine.text = if (listeners.contains(packageName)) "●  ON" else "●  SETUP"
    }

    private fun updateCallStatus() {
        if (::status.isInitialized) status.text = getSharedPreferences(CallMonitorService.PREFS, MODE_PRIVATE).getString("status", "Monitoring is off.") ?: "Monitoring is off."
    }

    private fun requestStart() {
        val permissions = mutableListOf(Manifest.permission.RECORD_AUDIO)
        if (Build.VERSION.SDK_INT >= 33) permissions += Manifest.permission.POST_NOTIFICATIONS
        val missing = permissions.filter { checkSelfPermission(it) != PackageManager.PERMISSION_GRANTED }
        if (missing.isNotEmpty()) requestPermissions(missing.toTypedArray(), requestCode) else startMonitoring()
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == imageNotificationPermissionRequestCode) {
            if (Build.VERSION.SDK_INT < 33 || checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) launchImagePicker()
            else if (::imageStatus.isInitialized) imageStatus.text = "Allow EvoShield notifications to receive image threat alerts."
            return
        }
        if (requestCode == notificationPermissionRequestCode) {
            if (Build.VERSION.SDK_INT < 33 || checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) {
                startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
            }
            return
        }
        if (requestCode != this.requestCode) return
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED &&
            (Build.VERSION.SDK_INT < 33 || checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED)) startMonitoring()
        else updateCallStatus()
    }

    private fun requestNotificationAccess() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), notificationPermissionRequestCode)
        } else {
            startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
        }
    }

    private fun startMonitoring() {
        val callType = if (::callTypeSpinner.isInitialized) when (callTypeSpinner.selectedItemPosition) { 1 -> "video"; 2 -> "both"; else -> "voice" } else "voice"
        getSharedPreferences(CallMonitorService.PREFS, MODE_PRIVATE).edit().putString("call_type", callType).apply()
        val intent = Intent(this, CallMonitorService::class.java).putExtra(CallMonitorService.EXTRA_CALL_TYPE, callType)
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(intent) else startService(intent)
        if (::status.isInitialized) status.text = "Starting call monitoring…"
    }

    private fun stopMonitoring() {
        stopService(Intent(this, CallMonitorService::class.java))
        if (::status.isInitialized) status.text = "Monitoring stopped."
    }
}
