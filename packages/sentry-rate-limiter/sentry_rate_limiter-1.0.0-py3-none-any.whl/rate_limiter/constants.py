GIT_COMMIT_HASH = None
PII_REGEX_PATTERNS = {
    "email": r"([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)",
    "phone": r"(\+\d{1,3}[- ]?)?\d{10}[\s , )]",
    "phone2": r"(?:\+?\d{1,3}|0)?([6-9]\d{9})\b",
    "pan": r"[A-Z]{5}[0-9]{4}[A-Z]{1}",
    "aadhar": r"[0-9]{4}[ -]?[0-9]{4}[ -]?[0-9]{4}[" " , . )]",
    "recording_url": str(r'[https?: // " ]\S+\.mp3[ \ {t1} . , " ]?'.format(t1="'")),
}

EXCLUDE_EXCEPTION_CLASSES = {
    "AggregateAudioFileException",
    "SentryIgnoredException",
    "TransportException",
}

EXCLUDE_EXCEPTION_MSG_PREFIXES = [
    "Couldn't load object 'core.playermission.",  # raised by celery_haystack task for ghost PMs
    "Got error while trying to copy audio file",
    "Got error while trying to aggregate audio",
    "Error while sending webhook post to Kernel at ",
    "[Errno 32] Broken pipe",
    "KernelPostDatapointsBlockType failed: HTTPSConnectionPool("
    "host='kernel.squadplatform.com', port=443): Max retries exceeded with url",
    "dropping flushed data due to transport failure back-off",
    "Unable to reach APM Server",
    "Failed to submit message: 'HTTP 503: queue is full'",
    "DialerLeadTracker obj absent",
    "Lock already acquired in aggreg",
]

SILENCED_LOGGER_MESSAGES = {
    # logger: list of message__startswith
    "apps.voice.crm_integrations.models": [
        "<RPFZ21: UpStox: Handle Squad Event Failed",
        "<SC5V21: Neostencil: Handle Squad Event Failed",
    ],
    "elasticapm.transport": ["Failed to submit message", "Unable to reach APM Server"],
}

RESTRICTED_PROPAGATION_SERIES = {1, 2, 4, 8, 16, 32, 64, 128, 256}
STANDARD_PROPAGATION_SERIES = {1, 2, 3, 4, 9, 16, 25, 36, 49}
