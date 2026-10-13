package com.evoshield.callguard

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

object LocalEntityHistory {
    const val KEY = "checked_entities"
    private const val MAX_ITEMS = 100

    @Synchronized
    fun add(context: Context, type: String, source: String, subject: String, verdict: String, summary: String) {
        val prefs = context.getSharedPreferences(CallMonitorService.PREFS, Context.MODE_PRIVATE)
        val old = try { JSONArray(prefs.getString(KEY, "[]")) } catch (_: Exception) { JSONArray() }
        val updated = JSONArray().put(JSONObject()
            .put("type", type)
            .put("source", source)
            .put("subject", subject)
            .put("verdict", verdict)
            .put("summary", summary.take(500))
            .put("time", System.currentTimeMillis()))
        for (index in 0 until minOf(old.length(), MAX_ITEMS - 1)) updated.put(old.getJSONObject(index))
        prefs.edit().putString(KEY, updated.toString()).apply()
    }
}
