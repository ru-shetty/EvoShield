from algorithms.digital_arrest_detection import DigitalArrestDetector


def test_digital_arrest_detection():

    detector = DigitalArrestDetector()

    text = """
    This is Cyber Crime Police.
    Your Aadhaar is involved in a criminal case.
    Stay on call.
    Share OTP immediately.
    """

    result = detector.detect(text)

    assert result["digital_arrest_probability"] > 50