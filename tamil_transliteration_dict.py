"""
TAMIL_TECH_TRANSLITERATIONS
----------------------------
Maps common English interview/tech terms to their Tamil-script phonetic
transliteration, so Piper + Valluvar (monolingual Tamil model) pronounces
them close to correct instead of reading raw Latin letters.

Grouped by category for easy maintenance. Add company names, specific
tool names, or role titles under the most relevant section (or a new
one) as you hit gaps in real scripts.

Matching is case-insensitive and whole-word only (won't touch substrings,
so "database" matches but "databases" won't unless also listed).
"""

TAMIL_TECH_TRANSLITERATIONS = {
    # --- Core tech/role vocabulary ---
    "API": "ஏபிஐ",
    "APIs": "ஏபிஐஸ்",
    "database": "டேட்டாபேஸ்",
    "databases": "டேட்டாபேஸஸ்",
    "algorithm": "அல்காரிதம்",
    "algorithms": "அல்காரிதம்ஸ்",
    "interview": "இன்டர்வியூ",
    "project": "ப்ராஜெக்ட்",
    "projects": "ப்ராஜெக்ட்ஸ்",
    "experience": "எக்ஸ்பீரியன்ஸ்",
    "team": "டீம்",
    "company": "கம்பெனி",
    "role": "ரோல்",
    "skills": "ஸ்கில்ஸ்",
    "analyst": "அனலிஸ்ட்",
    "data": "டேட்டா",
    "system": "சிஸ்டம்",
    "systems": "சிஸ்டம்ஸ்",
    "system's": "சிஸ்டம்",
    "business": "பிசினஸ்",
    "technical": "டெக்னிக்கல்",
    "software": "சாஃப்ட்வேர்",
    "engineer": "இன்ஜினியர்",
    "developer": "டெவலப்பர்",
    "manager": "மேனேஜர்",
    "client": "கிளையன்ட்",
    "clients": "கிளையன்ட்ஸ்",
    "stakeholder": "ஸ்டேக்ஹோல்டர்",
    "stakeholders": "ஸ்டேக்ஹோல்டர்ஸ்",
    "requirement": "ரிக்வயர்மென்ட்",
    "requirements": "ரிக்வயர்மென்ட்ஸ்",
    "solution": "சொல்யூஷன்",
    "solutions": "சொல்யூஷன்ஸ்",
    "process": "ப்ராசஸ்",
    "processes": "ப்ராசஸஸ்",
    "report": "ரிப்போர்ட்",
    "reports": "ரிப்போர்ட்ஸ்",
    "reporting": "ரிப்போர்ட்டிங்",
    "meeting": "மீட்டிங்",
    "deadline": "டெட்லைன்",
    "feedback": "ஃபீட்பேக்",
    "resume": "ரெஸ்யூம்",
    "job": "ஜாப்",
    "offer": "ஆஃபர்",
    "salary": "சாலரி",
    "visa": "விசா",
    "relocation": "ரீலொகேஷன்",
    "pipeline": "பைப்லைன்",
    "framework": "ஃப்ரேம்வொர்க்",
    "architecture": "ஆர்க்கிடெக்சர்",
    "testing": "டெஸ்டிங்",
    "deployment": "டிப்ளாயமெண்ட்",
    "analytics": "அனலிட்டிக்ஸ்",
    "coordinator": "கோர்டினேட்டர்",
    "coordination": "கோர்டினேஷன்",
    "onboarding": "ஆன்போர்டிங்",
    "email": "ஈமெயில்",

    # --- BA / Systems Analyst / Data Analyst domain terms ---
    "BRD": "பிஆர்டி",
    "SRS": "எஸ்ஆர்எஸ்",
    "UAT": "யுஏடி",
    "gap analysis": "கேப் அனாலிசிஸ்",
    "workflow": "வொர்க்ஃப்ளோ",
    "workflows": "வொர்க்ஃப்ளோஸ்",
    "use case": "யூஸ் கேஸ்",
    "use cases": "யூஸ் கேஸிஸ்",
    "user story": "யூசர் ஸ்டோரி",
    "user stories": "யூசர் ஸ்டோரீஸ்",
    "backlog": "பேக்லாக்",
    "sprint": "ஸ்பிரிண்ட்",
    "sprints": "ஸ்பிரிண்ட்ஸ்",
    "scrum": "ஸ்க்ரம்",
    "kanban": "கான்பான்",
    "stakeholder management": "ஸ்டேக்ஹோல்டர் மேனேஜ்மென்ட்",
    "root cause": "ரூட் காஸ்",
    "root cause analysis": "ரூட் காஸ் அனாலிசிஸ்",
    "KPI": "கேபிஐ",
  "KPIs": "கேபிஐஸ்",
    "dashboard": "டாஷ்போர்ட்",
    "dashboards": "டாஷ்போர்ட்ஸ்",
    "compliance": "காம்ப்ளையன்ஸ்",
    "audit": "ஆடிட்",
    "incident": "இன்சிடென்ட்",
    "incident report": "இன்சிடென்ட் ரிப்போர்ட்",
    "risk assessment": "ரிஸ்க் அசெஸ்மென்ட்",
    "escalation": "எஸ்கலேஷன்",
    "SLA": "எஸ்எல்ஏ",
    "documentation": "டாகுமெண்டேஷன்",
    "presentation": "ப்ரெசென்டேஷன்",

    # --- Programming / dev tools ---
    "SQL": "எஸ்க்யூஎல்",
    "Python": "பைதான்",
    "Java": "ஜாவா",
    "JavaScript": "ஜாவாஸ்கிரிப்ட்",
    "HTML": "எச்டிஎம்எல்",
    "CSS": "சிஎஸ்எஸ்",
    "Git": "கிட்",
    "GitHub": "கிட்ஹப்",
    "Excel": "எக்செல்",
    "PowerPoint": "பவர்பாயிண்ட்",
    "Tableau": "டேபிலோ",
    "Power BI": "பவர் பிஐ",
    "JIRA": "ஜிரா",
    "Confluence": "கான்ஃப்ளூயன்ஸ்",
    "Salesforce": "சேல்ஸ்ஃபோர்ஸ்",
    "cloud": "க்ளவுட்",
    "AWS": "ஏடபிள்யூஎஸ்",
    "Azure": "அஷூர்",
    "server": "சர்வர்",
    "servers": "சர்வர்ஸ்",
    "network": "நெட்வொர்க்",
    "code": "கோட்",
    "coding": "கோடிங்",
    "bug": "பக்",
    "bugs": "பக்ஸ்",
    "debugging": "டீபகிங்",
    "automation": "ஆட்டோமேஷன்",
    "integration": "இண்டெக்ரேஷன்",
    "migration": "மைக்ரேஷன்",

    # --- General interview / soft-skill vocabulary ---
    "team player": "டீம் ப்ளேயர்",
  "leadership": "லீடர்ஷிப்",
    "communication": "கம்யூனிகேஷன்",
    "problem solving": "ப்ராப்ளம் சால்விங்",
    "deadline management": "டெட்லைன் மேனேஜ்மென்ட்",
    "time management": "டைம் மேனேஜ்மென்ட்",
    "collaboration": "கொலாபரேஷன்",
    "initiative": "இனிஷியேட்டிவ்",
    "strength": "ஸ்ட்ரெங்த்",
    "strengths": "ஸ்ட்ரெங்த்ஸ்",
    "weakness": "வீக்நெஸ்",
    "weaknesses": "வீக்நெஸிஸ்",
    "opportunity": "ஆப்பர்ச்சூனிட்டி",
    "challenge": "சேலெஞ்ஜ்",
    "challenges": "சேலெஞ்ஜிஸ்",
    "achievement": "அச்சீவ்மென்ட்",
    "achievements": "அச்சீவ்மென்ட்ஸ்",
    "responsibility": "ரெஸ்பான்சிபிலிட்டி",
    "responsibilities": "ரெஸ்பான்சிபிலிட்டீஸ்",

    # --- Recruitment / relocation-specific (relevant to EU/UK job search) ---
    "recruiter": "ரிக்ரூட்டர்",
    "HR": "எச்ஆர்",
    "onsite": "ஆன்சைட்",
    "remote": "ரிமோட்",
    "hybrid": "ஹைப்ரிட்",
    "notice period": "நோட்டீஸ் பீரியட்",
    "sponsorship": "ஸ்பான்சர்ஷிப்",
    "work permit": "வொர்க் பர்மிட்",
    "contract": "காண்ட்ராக்ட்",
    "permanent": "பெர்மனெண்ட்",
    "probation": "ப்ரொபேஷன்",

    # --- Common connector/filler words that show up in code-switched speech ---
    "use": "யூஸ்",
    "using": "யூசிங்",
    "used": "யூஸ்ட்",
    "also": "ஆல்சோ",
    "actually": "ஆக்சுவலி",
    "basically": "பேசிக்லி",
}


try:
    from tamil_top200_transliteration_additions import (
        TOP_200_REMAINING_ENGLISH_TRANSLITERATIONS,
    )
except ImportError:
    TOP_200_REMAINING_ENGLISH_TRANSLITERATIONS = {}

TAMIL_TECH_TRANSLITERATIONS.update(TOP_200_REMAINING_ENGLISH_TRANSLITERATIONS)

try:
    from tamil_glossary_module import TAMIL_GLOSSARY_REPLACEMENTS
except ImportError:
    TAMIL_GLOSSARY_REPLACEMENTS = []

# Project glossary entries use the same tuple format as TECH_REPLACEMENTS.
# Apply them through the shared transliterate_tech_terms() path so Piper,
# Roja tests, Valluvar runs, and Indic fallback stay consistent.
for _term, _replacement in TAMIL_GLOSSARY_REPLACEMENTS:
    TAMIL_TECH_TRANSLITERATIONS.setdefault(_term, _replacement)

# Keep acronym pronunciations stable and avoid lower-case id matching inside
# ordinary words in tests/scripts. Use uppercase ID for the acronym.
TAMIL_TECH_TRANSLITERATIONS["IT"] = "\u0b90\u0b9f\u0bbf"
TAMIL_TECH_TRANSLITERATIONS["KYC"] = "\u0b95\u0bc7\u0b92\u0baf\u0bcd\u0b9a\u0bbf"
TAMIL_TECH_TRANSLITERATIONS.pop("id", None)
TAMIL_TECH_TRANSLITERATIONS.pop("side", None)
TAMIL_TECH_TRANSLITERATIONS.pop("simple", None)
TAMIL_TECH_TRANSLITERATIONS.pop("meaning", None)
TAMIL_TECH_TRANSLITERATIONS["webhook"] = "\u0bb5\u0bc6\u0baa\u0bcd\u0bb9\u0bc1\u0b95\u0bcd"


# Fallback English -> Tamil-script phonetic approximation for words not in the
# curated glossary. This is intentionally conservative: glossary entries remain
# the source of truth, and this only runs when transliterate_remaining_latin=True.
_LATIN_LETTER_NAMES = {
    "a": "\u0b8f", "b": "\u0baa\u0bbf", "c": "\u0b9a\u0bbf", "d": "\u0b9f\u0bbf",
    "e": "\u0b88", "f": "\u0b8e\u0baa\u0bcd", "g": "\u0b9c\u0bbf", "h": "\u0b8e\u0b9a\u0bcd",
    "i": "\u0b90", "j": "\u0b9c\u0bc7", "k": "\u0b95\u0bc7", "l": "\u0b8e\u0bb2\u0bcd",
    "m": "\u0b8e\u0bae\u0bcd", "n": "\u0b8e\u0ba9\u0bcd", "o": "\u0b93", "p": "\u0baa\u0bbf",
    "q": "\u0b95\u0bcd\u0baf\u0bc2", "r": "\u0b86\u0bb0\u0bcd", "s": "\u0b8e\u0bb8\u0bcd", "t": "\u0b9f\u0bbf",
    "u": "\u0baf\u0bc2", "v": "\u0bb5\u0bbf", "w": "\u0b9f\u0baa\u0bbf\u0bb3\u0bcd\u0baf\u0bc2",
    "x": "\u0b8e\u0b95\u0bcd\u0bb8\u0bcd", "y": "\u0bb5\u0bc8", "z": "\u0b9c\u0bc6\u0b9f\u0bcd",
}

_PHONETIC_UNITS = [
    ("tion", "\u0bb7\u0ba9\u0bcd"),
    ("sion", "\u0bb7\u0ba9\u0bcd"),
    ("cial", "\u0bb7\u0bbf\u0baf\u0bb2\u0bcd"),
    ("tial", "\u0bb7\u0bbf\u0baf\u0bb2\u0bcd"),
    ("ment", "\u0bae\u0bc6\u0ba3\u0bcd\u0b9f\u0bcd"),
    ("ance", "\u0baf\u0ba9\u0bcd\u0bb8\u0bcd"),
    ("ence", "\u0bc6\u0ba9\u0bcd\u0bb8\u0bcd"),
    ("ough", "\u0b93"),
    ("augh", "\u0b86\u0b83\u0baa\u0bcd"),
    ("eigh", "\u0b8f"),
    ("igh", "\u0b90"),
    ("air", "\u0b8f\u0bb0\u0bcd"),
    ("ear", "\u0b87\u0baf\u0bb0\u0bcd"),
    ("our", "\u0b85\u0bb5\u0bb0\u0bcd"),
    ("ing", "\u0bbf\u0b99\u0bcd"),
    ("ed", "\u0b9f\u0bcd"),
    ("ph", "\u0b83\u0baa\u0bcd"),
    ("sh", "\u0bb7\u0bcd"),
    ("ch", "\u0b9a\u0bcd"),
    ("th", "\u0ba4\u0bcd"),
    ("ck", "\u0b95\u0bcd"),
    ("ng", "\u0b99\u0bcd"),
    ("qu", "\u0b95\u0bcd\u0bb5"),
    ("wh", "\u0bb5"),
    ("wr", "\u0bb0"),
    ("kn", "\u0ba8"),
    ("oo", "\u0bc2"),
    ("ee", "\u0bc0"),
    ("ea", "\u0bc0"),
    ("ai", "\u0bc7"),
    ("ay", "\u0bc7"),
    ("oa", "\u0bcb"),
    ("ow", "\u0bcc"),
    ("ou", "\u0bcc"),
]

_FALLBACK_WORD_OVERRIDES = {
    "question": "\u0b95\u0bcd\u0bb5\u0bc6\u0bb8\u0bcd\u0b9a\u0ba9\u0bcd",
    "created": "\u0b95\u0bcd\u0bb0\u0bbf\u0baf\u0bc7\u0b9f\u0bcd\u0b9f\u0b9f\u0bcd",
    "parcel": "\u0baa\u0bbe\u0bb0\u0bcd\u0b9a\u0bb2\u0bcd",
    "transfer": "\u0b9f\u0bcd\u0bb0\u0bbe\u0ba9\u0bcd\u0bb8\u0bcd\u0b83\u0baa\u0bb0\u0bcd",
    "sent": "\u0b9a\u0bc6\u0ba9\u0bcd\u0b9f\u0bcd",
    "normal": "\u0ba8\u0bbe\u0bb0\u0bcd\u0bae\u0bb2\u0bcd",
    "which": "\u0bb5\u0bbf\u0b9a\u0bcd",
    "authentication": "\u0b86\u0ba4\u0bcd\u0ba4\u0bc6\u0ba9\u0bcd\u0b9f\u0bbf\u0b95\u0bc7\u0bb7\u0ba9\u0bcd",
    "refresh": "\u0bb0\u0bbf\u0b83\u0baa\u0bcd\u0bb0\u0bc6\u0bb7\u0bcd",
    "successful": "\u0b9a\u0b95\u0bcd\u0b9a\u0bb8\u0bcd\u0b83\u0baa\u0bc1\u0bb2\u0bcd",
    "workers": "\u0bb5\u0bca\u0bb0\u0bcd\u0b95\u0bb0\u0bcd\u0bb8\u0bcd",
    "rate": "\u0bb0\u0bc7\u0b9f\u0bcd",
    "type": "\u0b9f\u0bc8\u0baa\u0bcd",
    "same": "\u0b9a\u0bc7\u0bae\u0bcd",
    "end": "\u0b8e\u0ba3\u0bcd\u0b9f\u0bcd",
    "run": "\u0bb0\u0ba9\u0bcd",
    "partial": "\u0baa\u0bbe\u0bb0\u0bcd\u0bb7\u0bbf\u0baf\u0bb2\u0bcd",
    "payout": "\u0baa\u0bc7\u0b85\u0bb5\u0bc1\u0b9f\u0bcd",
    "trail": "\u0b9f\u0bcd\u0bb0\u0bc6\u0baf\u0bbf\u0bb2\u0bcd",
    "version": "\u0bb5\u0bc6\u0bb0\u0bcd\u0bb7\u0ba9\u0bcd",
    "unknownword": "\u0b85\u0ba9\u0bcd\u0ba8\u0bcb\u0ba9\u0bcd\u0bb5\u0bc7\u0bb0\u0bcd\u0b9f\u0bcd",
}

_CONSONANTS = {
    "b": "\u0baa", "c": "\u0b95", "d": "\u0b9f", "f": "\u0b83\u0baa", "g": "\u0b95",
    "h": "\u0bb9", "j": "\u0b9c", "k": "\u0b95", "l": "\u0bb2", "m": "\u0bae",
    "n": "\u0ba9", "p": "\u0baa", "q": "\u0b95", "r": "\u0bb0", "s": "\u0bb8",
    "t": "\u0b9f", "v": "\u0bb5", "w": "\u0bb5", "x": "\u0b95\u0bcd\u0bb8",
    "y": "\u0baf", "z": "\u0bb8",
}

_VOWELS = {
    "a": ("\u0b85", ""),
    "e": ("\u0b8e", "\u0bc6"),
    "i": ("\u0b87", "\u0bbf"),
    "o": ("\u0b92", "\u0bca"),
    "u": ("\u0b85", "\u0bc1"),
}

_PULLI = "\u0bcd"


def _latin_word_to_tamil_phonetic(word: str) -> str:
    """Best-effort Tamil-script sound-alike for an unmapped English word."""
    if not word:
        return word

    stripped = word.strip("'-")
    if not stripped:
        return word

    # IDs, acronyms, and short all-caps tokens sound better as letter names.
    if stripped.isupper() and len(stripped) <= 6:
        return "".join(_LATIN_LETTER_NAMES.get(ch.lower(), ch) for ch in stripped)

    lower = stripped.lower()
    if lower in _FALLBACK_WORD_OVERRIDES:
        return _FALLBACK_WORD_OVERRIDES[lower]

    if len(lower) > 3 and lower.endswith("e") and lower[-2] not in "aeiou":
        lower = lower[:-1]

    out: list[str] = []
    i = 0
    while i < len(lower):
        matched = False
        for src, tamil in _PHONETIC_UNITS:
            if lower.startswith(src, i):
                out.append(tamil)
                i += len(src)
                matched = True
                break
        if matched:
            continue

        ch = lower[i]
        next_ch = lower[i + 1] if i + 1 < len(lower) else ""
        if ch in _CONSONANTS:
            base = _CONSONANTS[ch]
            if next_ch in _VOWELS:
                _, sign = _VOWELS[next_ch]
                out.append(base + sign)
                i += 2
            else:
                out.append(base + _PULLI)
                i += 1
        elif ch in _VOWELS:
            independent, _ = _VOWELS[ch]
            out.append(independent)
            i += 1
        else:
            out.append(ch)
            i += 1

    result = "".join(out)
    if word.endswith("'s"):
        result += "\u0bb8\u0bcd"
    return result


def transliterate_tech_terms(text: str, transliterate_remaining_latin: bool = False) -> str:
    """Replace English tech terms with Tamil-script phonetic equivalents.

    Handles both multi-word phrases (e.g. "gap analysis", "use case") and
    single words. Multi-word entries are matched first (longest-match
    priority) so they aren't partially overwritten by single-word entries.
    Matching is case-insensitive; all other Tamil/English text is left
    untouched.
    """
    import re

    # Sort keys by word count (desc) then length (desc) so multi-word
    # phrases are matched before their component single words.
    sorted_keys = sorted(
        TAMIL_TECH_TRANSLITERATIONS.keys(),
        key=lambda k: (-len(k.split()), -len(k)),
    )
    exact_lookup = dict(TAMIL_TECH_TRANSLITERATIONS)
    lower_lookup: dict[str, str] = {}
    upper_lookup: dict[str, str] = {}
    for key, value in TAMIL_TECH_TRANSLITERATIONS.items():
        lower_key = key.lower()
        if key.isupper():
            upper_lookup[lower_key] = value
        elif lower_key not in lower_lookup:
            lower_lookup[lower_key] = value

    lookup = {**lower_lookup, **upper_lookup}

    pattern = re.compile(
        r"(?<![A-Za-z])(" + "|".join(re.escape(k) for k in sorted_keys) + r")(?![A-Za-z])",
        re.IGNORECASE,
    )

    def repl(match):
        original = match.group(0)
        key = original.lower()
        if original in exact_lookup:
            return exact_lookup[original]
        if original.isupper():
            return upper_lookup.get(key, original)
        return lower_lookup.get(key, original)

    converted = pattern.sub(repl, text)

    if not transliterate_remaining_latin:
        return converted

    return re.sub(
        r"(?<![A-Za-z])([A-Za-z][A-Za-z'-]*)(?![A-Za-z])",
        lambda match: _latin_word_to_tamil_phonetic(match.group(1)),
        converted,
    )


if __name__ == "__main__":
    sample = (
        "வணக்கம், நான் ஒரு Data Analyst ஆக Business Systems Analyst role "
        "க்கு interview க்கு போறேன். என் project experience database "
        "மற்றும் API testing, gap analysis, use case documentation ல இருக்கு. "
        "நான் SQL, Excel, Power BI use பண்ணி dashboards உருவாக்கியிருக்கேன்."
    )
    print("BEFORE:", sample)
    print("AFTER: ", transliterate_tech_terms(sample))
