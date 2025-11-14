import re
from datetime import datetime

# -------------------------
# CONSTANTES
# -------------------------
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
USD_TO_EUR = 0.92
DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]

# -------------------------
# FONCTIONS DE NETTOYAGE
# -------------------------

def clean_email(email):
    """Nettoie un email et vérifie le format."""
    if not isinstance(email, str):
        return None
    e = email.strip().lower()
    return e if re.match(EMAIL_REGEX, e) else None

def clean_country(country):
    """Normalise le nom des pays."""
    COUNTRY_MAP = {
        "fr": "France",
        "france": "France",
        "french republic": "France",
        "be": "Belgique",
        "belgique": "Belgique",
        "ch" : "suisse"
    }
    if not isinstance(country, str):
        return None
    c = country.strip().lower()
    return COUNTRY_MAP.get(c, country.title())

def clean_phone(phone, default_country_code='33'):
    """Nettoie le numéro de téléphone et ajoute l'indicatif si nécessaire."""
    if not isinstance(phone, str):
        return None
    digits = ''.join(c for c in phone if c.isdigit())
    if len(digits) <= 9:
        digits = default_country_code + digits
    return digits

def clean_date(date_str):
    """Convertit une date en format ISO 'YYYY-MM-DD'."""
    if not isinstance(date_str, str):
        return None
    date_str = date_str.strip()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except:
            continue
    return None

def clean_weight(weight: str, unit: str):
    """Convertit les poids en kg en utilisant weight et weight_unit."""
    if weight is None or unit is None:
        return None

    try:
        w = float(weight)
    except:
        return None

    u = unit.lower().strip()

    if u == "kg":
        return w
    if u == "g":
        return w / 1000
    if u in ["lb", "lbs"]:
        return w * 0.453592

    return None

def clean_price(price):
    """Convertit un prix en float et unifie en EUR si $."""
    if isinstance(price, (int, float)):
        return float(price)
    if not isinstance(price, str):
        return None
    txt = price.replace(",", ".")
    value = float(re.sub(r"[^0-9\.]", "", txt))
    if "$" in price or "usd" in price.lower():
        return round(value * USD_TO_EUR, 2)
    return round(value, 2)
# Convertir et unifier montants en EUR
def convert_amount(row):
    try:
        # Nettoyer le montant pour garder seulement les chiffres et le point décimal
        amt = float(re.sub(r"[^0-9.]","",str(row['amount'])))
        # Vérifier la devise et convertir si USD
        cur = row['currency'].strip().upper() if isinstance(row['currency'], str) else "€"
        if cur in ["USD","$"]:
            amt = round(amt*USD_TO_EUR,2)
        # Forcer toutes les lignes à EUR
        row['currency'] = "€"
        return amt
    except:
        row['currency'] = "€"
        return None


