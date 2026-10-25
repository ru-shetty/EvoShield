package com.evoshield.callguard

data class ImageTextDetection(val verdict: String, val summary: String)

object ImageTextThreatDetector {
    private val suspiciousPhrases = listOf(
        "verify your account", "account has been suspended", "account is suspended",
        "enter your password", "confirm your identity", "send money immediately",
        "pay the fine", "claim your refund", "click the link", "scan this qr"
    )

    fun analyze(text: String): ImageTextDetection {
        val normalized = text.lowercase().replace(Regex("\\s+"), " ")
        val arrest = DigitalArrestDetector.analyze(normalized, "both")
        val phrase = suspiciousPhrases.any(normalized::contains)
        val credential = listOf("password", "otp", "one-time code", "pin", "bank details", "login").any(normalized::contains)
        val urgency = listOf("urgent", "immediately", "within 24 hours", "act now", "today only").any(normalized::contains)
        val money = listOf("payment", "transfer", "pay now", "refund", "bank account", "fine").any(normalized::contains)

        if (arrest.category == "DIGITAL_ARREST") {
            return ImageTextDetection("HIGH", "Possible digital-arrest scam wording: ${arrest.indicators.joinToString()}. Do not pay or share codes under pressure.")
        }
        if (phrase || (credential && urgency) || (money && urgency) || arrest.category == "SUSPICIOUS") {
            val reasons = buildList {
                if (phrase) add("phishing-style instructions")
                if (credential) add("password, code, or account details")
                if (money) add("payment or money requests")
                if (urgency) add("pressure to act quickly")
                addAll(arrest.indicators)
            }.distinct()
            return ImageTextDetection("MEDIUM", "Suspicious wording in the image: ${reasons.joinToString()}. Verify independently before acting.")
        }
        return ImageTextDetection("LOW", "No strong scam warning signs were found in the readable image text.")
    }
}
