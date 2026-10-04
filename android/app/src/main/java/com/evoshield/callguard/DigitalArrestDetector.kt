package com.evoshield.callguard

data class Detection(val category: String, val probability: Double, val indicators: List<String>)

object DigitalArrestDetector {
    private val rules = linkedMapOf(
        "government/police impersonation" to listOf("police", "cyber crime", "cybercrime", "cbi", "customs officer", "government officer", "income tax officer", "court officer", "supreme court", "central bureau of investigation", "cyber cell", "cyber police", "police ki taraf se", "पुलिस", "साइबर क्राइम", "साइबर पुलिस"),
        "threat language" to listOf("you will be arrested", "you are under arrest", "arrest warrant", "arrest you", "legal action", "criminal case", "police case", "warrant issued", "jail", "imprisonment", "aapko giraftar kiya jayega", "aap giraftar hain", "giraftar kar lenge", "गिरफ्तार किया जाएगा", "गिरफ्तारी वारंट", "जेल भेज देंगे"),
        "urgency" to listOf("immediately", "urgent", "right now", "within 10 minutes", "within 30 minutes", "do it now", "act immediately", "do not disconnect", "abhi turant", "phone mat kaato", "call mat kaato", "फोन मत काटो", "कॉल मत काटो", "अभी तुरंत"),
        "financial request" to listOf("send money", "transfer money", "pay now", "make payment", "bank transfer", "upi payment", "account number", "pay the fine", "pay the penalty", "paise bhejo", "paisa transfer karo", "fine jama karo", "जुर्माना भरो", "पैसे भेजो", "पैसा ट्रांसफर करो"),
        "sensitive information request" to listOf("otp", "one time password", "pin", "aadhaar", "aadhar", "pan card", "pan number", "bank details", "debit card", "credit card", "otp batao", "otp bataye", "aadhaar number batao", "ओटीपी बताओ", "आधार नंबर बताओ"),
        "fake document" to listOf("fake warrant", "arrest notice", "legal notice", "court notice", "case document", "government notice", "official document", "verification document", "nakli warrant", "fake police notice", "नकली वारंट", "फर्जी वारंट"),
        "call pressure" to listOf("do not disconnect", "stay on the call", "keep the video call on", "do not tell anyone", "do not contact anyone", "stay connected", "keep your camera on", "kisi ko mat batana", "video call par raho", "किसी को मत बताना", "वीडियो कॉल पर रहो")
    )
    private val weights = listOf(.20, .20, .10, .15, .15, .10, .10)

    fun analyze(text: String): Detection {
        val normalized = text.lowercase().replace(Regex("\\s+"), " ")
        val found = rules.keys.zip(rules.values).mapNotNull { (label, phrases) ->
            if (phrases.any(normalized::contains)) label else null
        }
        val score = found.sumOf { label -> weights[rules.keys.indexOf(label)] }.coerceAtMost(1.0)
        val category = when {
            score >= .60 -> "DIGITAL_ARREST"
            score >= .30 -> "SUSPICIOUS"
            else -> "NORMAL"
        }
        return Detection(category, score, found)
    }
}
