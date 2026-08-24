from algorithms.digital_arrest_detector import DigitalArrestDetector
detector = DigitalArrestDetector()

sample_text = """
I am a Cyber Crime Police officer.

Your Aadhaar is linked to a criminal investigation.

Do not disconnect this call.

Share your OTP immediately.

Failure to cooperate may result in arrest.
"""

result = detector.detect(sample_text)

print("\n===== DIGITAL ARREST DETECTION RESULT =====")
print(result)