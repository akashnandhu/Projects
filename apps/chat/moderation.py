"""
Two-Tier Content Moderation Engine.
"""
import re

SELF_HARM_KEYWORDS = [
    r'suicide', r'self-harm', r'end my life', r'kill myself', r'want to die', 
    r'cut myself', r'overdose', r'no reason to live'
]

VIOLENCE_KEYWORDS = [
    r'bomb', r'shoot', r'attack', r'terrorism', r'kill them', r'threaten', 
    r'hostage', r'mass shooting'
]

SELF_HARM_REGEX = re.compile(r'\b(?:' + '|'.join(SELF_HARM_KEYWORDS) + r')\b', re.IGNORECASE)
VIOLENCE_REGEX = re.compile(r'\b(?:' + '|'.join(VIOLENCE_KEYWORDS) + r')\b', re.IGNORECASE)

def scan_text_tier1(text: str) -> dict:
    """
    Tier 1 - Regex Keyword Scanner (Instant)
    """
    matched_self_harm = SELF_HARM_REGEX.findall(text)
    matched_violence = VIOLENCE_REGEX.findall(text)
    
    matched_keywords = matched_self_harm + matched_violence
    
    risk_level = 'SAFE'
    if matched_violence:
        risk_level = 'PUBLIC_SAFETY_THREAT'
    elif matched_self_harm:
        risk_level = 'SELF_HARM_RISK'
        
    return {
        'risk_level': risk_level,
        'matched_keywords': matched_keywords
    }

def classify_intent(text: str) -> dict:
    """
    Tier 2 - Mock NLP Intent Classifier (Pluggable)
    This is clearly documented as a placeholder for a real NLP model.
    # TODO: Replace with a HuggingFace pipeline() call or OpenAI API call in production.
    """
    # Simple heuristic
    words = text.lower().split()
    risk_words = sum(1 for w in words if w in ['die', 'kill', 'shoot', 'bomb', 'overdose'])
    
    confidence = 0.0
    category = 'Safe'
    if risk_words >= 1:
        confidence = min(1.0, 0.4 + (0.2 * risk_words))
        if 'shoot' in words or 'bomb' in words or 'kill' in words and 'them' in words:
            category = 'Public_Safety_Threat'
        else:
            category = 'Self_Harm_Risk'
            
    return {
        'category': category,
        'confidence': confidence
    }

def moderate_message(text: str) -> dict:
    """
    Full moderation decision logic across both tiers.
    """
    tier1 = scan_text_tier1(text)
    tier2 = classify_intent(text)
    
    final_risk = tier1['risk_level']
    final_flagged = False
    
    # Compare combinations and max risk
    if tier2['category'] == 'Public_Safety_Threat' and tier2['confidence'] > 0.6:
        final_risk = 'PUBLIC_SAFETY_THREAT'
    elif tier2['category'] == 'Self_Harm_Risk' and final_risk == 'SAFE' and tier2['confidence'] > 0.6:
        final_risk = 'SELF_HARM_RISK'
        
    if final_risk != 'SAFE':
        final_flagged = True
        
    return {
        'is_flagged': final_flagged,
        'risk_level': final_risk,
        'matched_keywords': tier1['matched_keywords']
    }
