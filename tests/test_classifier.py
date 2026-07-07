from src.classify_behaviour import classify_text

def test_password_classification():
    category, recommendation = classify_text("User forgot password and MFA login failed")
    assert category == "Memory / Access"

def test_phishing_classification():
    category, recommendation = classify_text("User reported suspicious phishing email")
    assert category == "Attention / Security"
