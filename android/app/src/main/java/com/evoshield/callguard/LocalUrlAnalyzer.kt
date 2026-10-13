package com.evoshield.callguard

import java.net.URI

data class LocalUrlResult(val verdict: String, val summary: String)

object LocalUrlAnalyzer {
    private val suspiciousWords = listOf("login", "verify", "account", "secure", "payment", "wallet", "claim", "kyc", "update")

    fun analyze(raw: String): LocalUrlResult {
        val normalized = if (raw.startsWith("http://") || raw.startsWith("https://")) raw else "https://$raw"
        val uri = try { URI(normalized) } catch (_: Exception) { return LocalUrlResult("REVIEW", "The link could not be parsed; verify it before opening.") }
        val host = uri.host?.lowercase() ?: return LocalUrlResult("REVIEW", "The link has no readable website name; verify it before opening.")
        val flags = mutableListOf<String>()
        if (uri.scheme != "https") flags += "It does not use HTTPS."
        if (host.matches(Regex("\\d{1,3}(\\.\\d{1,3}){3}"))) flags += "It uses a numeric internet address."
        if (host.startsWith("xn--") || ".xn--" in host) flags += "It uses encoded website-name characters."
        if (suspiciousWords.any(host::contains)) flags += "The website name uses sign-in, payment, or account-verification wording."
        val verdict = when {
            flags.size >= 2 -> "MEDIUM"
            flags.isNotEmpty() -> "REVIEW"
            else -> "LOW"
        }
        val summary = if (flags.isEmpty()) "No strong warning signs were found in this link. That does not prove the site is safe." else flags.joinToString(" ")
        return LocalUrlResult(verdict, summary)
    }
}
