#!/usr/bin/env python3

import re
import logging

def filter_sender_sms(phone_number:str, message:str):
    """
    This function filters sms sent and only validate user sms
    It skips all mobile network provider messages, promotions, and other non-user messages.
    Args:
        phone_number (str): The sender's phone number.
        message (str): The content of the SMS message.
    """
    if len(phone_number) < 10:
        logging.warning("SMS FILTERED | reason=short_sender | sender=%s", phone_number)
        return False

    # Exclude messages from known MTN Rwanda / service alphanumeric sender IDs
    sender_exclusion_patterns = [
        r"(?i)^(mtn|momo|mtnmomo|mobile\s*money|sms\s*info|infosms|myairtel|airtel)$",
    ]
    for pattern in sender_exclusion_patterns:
        if re.search(pattern, phone_number.strip()):
            logging.warning("SMS FILTERED | reason=sender_id | sender=%s | pattern=%s", phone_number, pattern)
            return False

    # Exclude messages whose content matches MTN Rwanda or non-user indicators
    patterns = [
        # --- MTN Rwanda MoMo transaction alerts ---
        r"(?i)\bmomo\b",
        r"(?i)mobile\s+money",
        r"(?i)(transferred|received|paid)\s+[\d,]+\s*rwf",
        r"(?i)transaction\s+(id|ref|reference|fee)",
        r"(?i)your\s+(mtn|momo)\s+(balance|account)",
        r"(?i)new\s+balance\s*:?\s*rwf",
        r"(?i)akazi\s+kuri\s+momo",                    # Kinyarwanda MoMo phrase

        # --- MTN Rwanda system / promotional ---
        r"(?i)dial\s+\*\d+#",                          # USSD instructions
        r"(?i)\*\d{3,}#",                              # embedded USSD codes
        r"(?i)(buy|activate|get)\s+(bundle|data|airtime)",
        r"(?i)your\s+(otp|pin|code)\s+(is|:)\s*\d+",

        # --- General promotional / spam indicators ---
        r"(?i)(promo|promotion|promotional|special\s+offer|exclusive\s+deal)",
        r"(?i)(unsubscribe|opt[\s-]?out|reply\s+stop|to\s+stop[\s,]+reply)",
        r"(?i)(click\s+here|visit\s+our\s+website|www\.|http)",

        # --- Banking / financial service alerts ---
        r"(?i)(bank\s+alert|account\s+balance|statement\s+available|transaction\s+alert)",
        r"(?i)\b(equity\s+bank|bk\s*bank|i&m\s*bank|cogebanque|kcb|ecobank)\b",

        # --- Other Rwandan service providers ---
        r"(?i)\b(airtel|tigo)\b",
        r"(?i)\b(rra|rssb|gov\.rw)\b",                # government / tax agencies

        # --- Account / security confirmations (any service) ---
        r"(?i)your\s+password\s+has\s+(been\s+)?(changed|updated|reset)",
        r"(?i)password\s+(change|reset|update)\s+(successful|confirmed|complete)",
        r"(?i)you\s+have\s+successfully\s+(changed|updated|reset)\s+your\s+password",
        r"(?i)(account|profile)\s+(has\s+been\s+)?(created|activated|verified|deactivated|suspended|locked)",
        r"(?i)your\s+(account|profile|email)\s+(is|has\s+been)\s+(verified|confirmed|activated)",
        r"(?i)(two[\s-]?factor|2fa)\s+(enabled|disabled|authentication)",
        r"(?i)login\s+(attempt|detected|from\s+new\s+device)",
        r"(?i)sign[\s-]?in\s+(alert|notification|from)",

        # --- Subscription confirmations (any service) ---
        r"(?i)you\s+have\s+(been\s+)?(successfully\s+)?(subscribed|unsubscribed)",
        r"(?i)(subscription|membership)\s+(activated|confirmed|renewed|cancelled|expired)",
        r"(?i)welcome\s+to\s+.{0,30}(plan|package|membership|subscription)",
        r"(?i)your\s+(free\s+)?trial\s+(has\s+)?(started|begins|expired|ending)",
        r"(?i)auto[\s-]?renew(al)?\s+(is|has\s+been|will\s+be)",

        # --- Delivery / order notifications ---
        r"(?i)your\s+(order|package|delivery|shipment)\s+(has\s+been|is|was)\s+(placed|confirmed|shipped|delivered|out\s+for\s+delivery)",
        r"(?i)order\s+(id|#|number)\s*[:\-]?\s*\w+",
        r"(?i)estimated\s+(delivery|arrival)\s+(date|time)",
    ]
    for pattern in patterns:
        if re.search(pattern, message.strip()):
            logging.warning("SMS FILTERED | reason=content_match | sender=%s | pattern=%s | message=%s", phone_number, pattern, message[:80])
            return False

    return True
