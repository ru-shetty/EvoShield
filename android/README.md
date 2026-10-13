# EvoShield Call Guard for Android

This Android Studio project adds an opt-in, on-device speech monitor for calls. It targets Android 12 (API 31) and newer and uses Android's on-device speech recognizer only. The rules include common English and Hindi digital-arrest phrases; recognition quality depends on the phone's installed offline language model and configured language. It does not send audio or transcripts to EvoShield's server and does not save transcripts. The app keeps up to 50 local alert summaries, shown under **Recent call alerts**; it does not scan Android files, browser URLs, SMS, or other app notifications.

## Build and install

1. Open this `android` folder in Android Studio with JDK 17 and Android SDK 35 installed.
2. Let Gradle sync, connect an Android 12+ phone, and run the `app` configuration.
3. Open EvoShield Protection and tap **Enable message and link checks**. Android Settings opens; select EvoShield and grant Notification Access.
4. Make sure message preview text is enabled in the source app and Android notification settings. New previews from WhatsApp, WhatsApp Business, Google/Samsung Messages, Telegram, Signal, and Messenger are checked on-device. Message previews and full URLs are not uploaded or saved; only the source, website host/message label, risk level, summary, and time are kept in the local history.
5. For call monitoring, tap **Start call monitoring**, grant microphone and notification permissions, then return to WhatsApp and use speakerphone if needed. The persistent notification shows the monitor is active; use its **Stop** action to end the session.

Android checks only notifications that include visible preview text. Hidden previews, unsupported messaging apps, and content that never appears as a notification cannot be scanned. Link checks use simple on-device warning rules and are not a live reputation lookup. Android scan history stays on the phone and is separate from the Windows dashboard history.

The local on-device speech service must be available on the phone. The app reports an unavailable service instead of silently sending speech to a cloud recognizer.

## Android call-audio limitation

Android does not let an ordinary app directly capture another app's voice-communication playback. This prototype listens through the phone microphone in a user-started foreground session. WhatsApp may own the microphone during a call, and remote speech may only be audible to EvoShield on speakerphone. Headsets, device routing, and manufacturer behavior can prevent capture. The monitor reports that it cannot hear usable speech when the recognition service signals a capture problem; a quiet call can produce the same message. It cannot guarantee detection or block a call.
