"""
Multilingual Translation Service
Supports: English (EN), Hindi (HI), Marathi (MR)
Uses Google Translate API for real-time translation
"""
import os
from typing import Optional, Dict, List
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Predefined translations for common medical terms (for offline support)
MEDICAL_TERM_TRANSLATIONS = {
    # English -> Hindi -> Marathi
    "symptom": {"HI": "लक्षण", "MR": "लक्षण"},
    "fever": {"HI": "बुखार", "MR": "ताप"},
    "headache": {"HI": "सिरदर्द", "MR": "डोकेदुखी"},
    "cough": {"HI": "खांसी", "MR": "खोकला"},
    "cold": {"HI": "सर्दी", "MR": "सर्दी"},
    "body_aches": {"HI": "शरीर में दर्द", "MR": "शरीरदुखी"},
    "appointment": {"HI": "नियुक्ति", "MR": "भेट"},
    "doctor": {"HI": "डॉक्टर", "MR": "डॉक्टर"},
    "specialist": {"HI": "विशेषज्ञ", "MR": "तज्ञ"},
    "disease": {"HI": "रोग", "MR": "रोग"},
    "treatment": {"HI": "उपचार", "MR": "उपचार"},
    "medicine": {"HI": "दवा", "MR": "औषध"},
    "prescription": {"HI": "नुस्खा", "MR": "प्रिस्क्रिप्शन"},
    "consultation": {"HI": "परामर्श", "MR": "सल्ला"},
    "clinic": {"HI": "क्लिनिक", "MR": "क्लिनिक"},
    "hospital": {"HI": "अस्पताल", "MR": "रुग्णालय"},
    "patient": {"HI": "रोगी", "MR": "रोगी"},
    "emergency": {"HI": "आपातकाल", "MR": "आपातकाल"},
    "allergic": {"HI": "एलर्जी", "MR": "ऍलर्जी"},
    "urgent": {"HI": "तुरंत", "MR": "तातडीने"},
}

# Language codes mapping
LANGUAGE_CODES = {
    "EN": "en",
    "HI": "hi",
    "MR": "mr",
    "English": "EN",
    "Hindi": "HI",
    "Marathi": "MR"
}


class TranslationService:
    """Handle text translation between languages"""
    
    def __init__(self):
        """Initialize translation service"""
        self.use_google_translate = os.getenv("USE_GOOGLE_TRANSLATE", "false").lower() == "true"
        self.google_translate_api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
        
        if self.use_google_translate and self.google_translate_api_key:
            try:
                from google.cloud import translate_v2
                self.translate_client = translate_v2.Client(
                    api_key=self.google_translate_api_key
                )
                logger.info("Google Translate API initialized")
            except Exception as e:
                logger.warning(f"Google Translate API initialization failed: {e}. Using offline translations.")
                self.use_google_translate = False
        else:
            self.use_google_translate = False
            logger.info("Using offline translation database")
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of input text
        Returns: "EN", "HI", or "MR"
        """
        try:
            # Hindi script detection
            if self._contains_devanagari(text):
                # Check if more likely Hindi or Marathi
                return "HI"  # Simplified; can be enhanced with more heuristics
            
            # Marathi script is subset of Devanagari, check specific Marathi words
            marathi_indicators = ["ण", "य्य", "ळ"]  # Marathi-specific characters
            if any(char in text for char in marathi_indicators):
                return "MR"
            
            # Default to English
            return "EN"
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "EN"
    
    def _contains_devanagari(self, text: str) -> bool:
        """Check if text contains Devanagari script (Hindi/Marathi)"""
        devanagari_range = range(0x0900, 0x0950)
        return any(ord(char) in devanagari_range for char in text)
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text from source language to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (EN, HI, MR)
            target_lang: Target language code (EN, HI, MR)
        
        Returns:
            Translated text
        """
        # If same language, return as-is
        if source_lang == target_lang:
            return text
        
        # Try Google Translate first
        if self.use_google_translate:
            try:
                result = self._translate_google(text, source_lang, target_lang)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Google Translate failed: {e}. Falling back to offline translation.")
        
        # Fallback to offline translation
        return self._translate_offline(text, source_lang, target_lang)
    
    def _translate_google(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translate using Google Translate API"""
        try:
            source_code = LANGUAGE_CODES.get(source_lang, "en")
            target_code = LANGUAGE_CODES.get(target_lang, "en")
            
            result = self.translate_client.translate_text(
                text,
                source_language=source_code,
                target_language=target_code
            )
            return result["translatedText"]
        except Exception as e:
            logger.error(f"Google Translate error: {e}")
            return None
    
    def _translate_offline(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Offline translation using predefined dictionary
        Handles medical terms well, falls back to returning original for unknown words
        """
        words = text.lower().split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = word.strip('.,!?;:')
            
            if clean_word in MEDICAL_TERM_TRANSLATIONS:
                if target_lang in MEDICAL_TERM_TRANSLATIONS[clean_word]:
                    translated_words.append(
                        MEDICAL_TERM_TRANSLATIONS[clean_word][target_lang]
                    )
                else:
                    translated_words.append(word)
            else:
                # Keep unknown words as-is (can be enhanced with dictionary API)
                translated_words.append(word)
        
        return " ".join(translated_words)
    
    def translate_list(self, items: List[str], target_lang: str) -> List[str]:
        """Translate a list of strings"""
        source_lang = self.detect_language(items[0]) if items else "EN"
        return [self.translate(item, source_lang, target_lang) for item in items]
    
    def translate_dict(self, data: Dict, target_lang: str, fields: List[str]) -> Dict:
        """
        Translate specific fields in a dictionary
        
        Args:
            data: Dictionary to translate
            target_lang: Target language
            fields: List of field names to translate
        
        Returns:
            Dictionary with translated fields
        """
        translated = data.copy()
        
        for field in fields:
            if field in translated and isinstance(translated[field], str):
                translated[field] = self.translate(
                    translated[field],
                    "EN",
                    target_lang
                )
            elif field in translated and isinstance(translated[field], list):
                translated[field] = self.translate_list(translated[field], target_lang)
        
        return translated
    
    def normalize_to_english(self, text: str) -> str:
        """
        Normalize multilingual input to English
        Useful for processing before sending to LLM
        """
        detected_lang = self.detect_language(text)
        if detected_lang == "EN":
            return text
        return self.translate(text, detected_lang, "EN")


class LocalizationManager:
    """Manage localized responses and UI strings"""
    
    LOCALIZED_STRINGS = {
        "welcome": {
            "EN": "Welcome to AI Healthcare Assistant",
            "HI": "AI हेल्थकेयर सहायक में आपका स्वागत है",
            "MR": "AI हेल्थकेयर सहायकामध्ये आपले स्वागत आहे"
        },
        "describe_symptoms": {
            "EN": "Please describe your symptoms",
            "HI": "कृपया अपने लक्षणों का वर्णन करें",
            "MR": "कृपया आपले लक्षणांचे वर्णन करा"
        },
        "analyzing": {
            "EN": "Analyzing your symptoms...",
            "HI": "आपके लक्षणों का विश्लेषण किया जा रहा है...",
            "MR": "आपले लक्षण विश्लेषण केले जात आहे..."
        },
        "recommendations": {
            "EN": "Recommended specialists",
            "HI": "अनुशंसित विशेषज्ञ",
            "MR": "शिफारस केलेले तज्ञ"
        },
        "book_appointment": {
            "EN": "Book Appointment",
            "HI": "नियुक्ति बुक करें",
            "MR": "भेट बुक करा"
        },
        "appointment_confirmed": {
            "EN": "Appointment confirmed!",
            "HI": "नियुक्ति की पुष्टि हुई!",
            "MR": "भेट पुष्टी झाली!"
        },
        "medical_disclaimer": {
            "EN": "⚠️ MEDICAL DISCLAIMER: This is an AI-generated analysis and NOT a medical diagnosis. Please consult with a qualified healthcare professional for accurate diagnosis and treatment.",
            "HI": "⚠️ चिकित्सा अस्वीकरण: यह एक AI-जनित विश्लेषण है और चिकित्सा निदान नहीं है। सटीक निदान और उपचार के लिए कृपया एक योग्य स्वास्थ्यसेवा पेशेवर से परामर्श लें।",
            "MR": "⚠️ वैद्यकीय अस्वीकरण: हे एक AI-निर्मित विश्लेषण आहे आणि वैद्यकीय निदान नाही. अचूक निदान आणि उपचारासाठी कृपया योग्य स्वास्थ्यसेवा व्यावसायिकांचा सल्ला घ्या."
        },
        "error_generic": {
            "EN": "An error occurred. Please try again.",
            "HI": "एक त्रुटि हुई। कृपया पुनः प्रयास करें।",
            "MR": "एक त्रुटी आली. कृपया पुन्हा प्रयत्न करा."
        }
    }
    
    @staticmethod
    def get_localized_string(key: str, language: str = "EN") -> str:
        """Get localized string by key and language"""
        if key in LocalizationManager.LOCALIZED_STRINGS:
            return LocalizationManager.LOCALIZED_STRINGS[key].get(language, 
                   LocalizationManager.LOCALIZED_STRINGS[key].get("EN", key))
        return key
    
    @staticmethod
    def get_all_translations(key: str) -> Dict[str, str]:
        """Get all language translations for a key"""
        return LocalizationManager.LOCALIZED_STRINGS.get(key, {"EN": key})


# Singleton instance
_translation_service = None


def get_translation_service() -> TranslationService:
    """Get or create TranslationService singleton"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
