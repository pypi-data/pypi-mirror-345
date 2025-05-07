import hashlib
import json
import logging
import re
import time
import traceback
import uuid
from random import randint

from kombu.utils.encoding import ensure_bytes
from sentry_sdk.integrations.logging import ignore_logger

from rate_limiter.constants import (
    GIT_COMMIT_HASH,
    PII_REGEX_PATTERNS,
    EXCLUDE_EXCEPTION_CLASSES,
    EXCLUDE_EXCEPTION_MSG_PREFIXES,
    SILENCED_LOGGER_MESSAGES, RESTRICTED_PROPAGATION_SERIES,
)
from rate_limiter.utils import get_ec2_instance_id, get_ec2_instance_name

logger = logging.getLogger(__name__)
ignore_logger("elasticapm.transport")


class SentryHandler:
    def __init__(
            self,
            redis_connection,
            pii_regex_patterns=PII_REGEX_PATTERNS,
            exclude_exception_classes=EXCLUDE_EXCEPTION_CLASSES,
            exclude_exception_msg_prefixes=EXCLUDE_EXCEPTION_MSG_PREFIXES,
            silence_logger_messages=SILENCED_LOGGER_MESSAGES,
            propagation_series=RESTRICTED_PROPAGATION_SERIES
    ):
        self.redis_connection = redis_connection
        if pii_regex_patterns:
            self.pii_regex_patterns = pii_regex_patterns
        if exclude_exception_classes:
            self.exclude_exception_classes = exclude_exception_classes
        if exclude_exception_msg_prefixes:
            self.exclude_exception_msg_prefixes = exclude_exception_msg_prefixes
        if silence_logger_messages:
            self.silence_logger_messages = silence_logger_messages
        if propagation_series:
            self.propagation_series = propagation_series

    def before_send_sentry_handler(self, event, hint):
        """
        Warning: Don't change this. Use `filter_events` instead
        """
        # use this for debugging when required

        try:
            return self.filter_events(event, hint)
        except Exception as exc:

            try:
                logger.warning(
                    "sentryfilter error : {!r} \n{}".format(exc, "\n".join(traceback.format_tb(exc.__traceback__)))
                )
            except AttributeError:
                logger.warning(f"sentryfilter error  : {exc!r}")

            return self.filter_pii(event)

    def should_propagate(self, count):
        series = self.propagation_series
        highest = max(series)
        return (count % highest) in series

    @staticmethod
    def get_hash(bytestr):
        return hashlib.md5(ensure_bytes(bytestr)).hexdigest()

    @staticmethod
    def get_hash_hint_for_exc(event):
        try:
            exc_type = event["exception"]["values"][0]["type"].encode("utf-8")
            traceback_hints = []
            for frame in event["exception"]["values"][0]["stacktrace"]["frames"]:
                traceback_hints.append(frame["abs_path"])
                traceback_hints.append(str(frame["lineno"]))
        except Exception:
            return str(uuid.uuid4())
        else:
            return exc_type + ":".join(traceback_hints).encode("utf-8")

    @staticmethod
    def get_hash_hint_for_logger(event):
        try:
            hash_hint = event["logger"].encode("utf-8")
            try:
                hash_hint += event["logentry"]["message"].encode("utf-8")
            except UnicodeError:
                hash_hint += event["logentry"]["message"]
        except Exception:
            return str(uuid.uuid4())
        else:
            return hash_hint


    def dedupe_exc(self, event):
        hash_hint = self.get_hash_hint_for_exc(event)
        exchash = self.filter_pii(self.get_hash(hash_hint))
        key = f"sentry:exception:{exchash}:{int(time.time() // 1000)!s}"
        incr_cnt = self.redis_connection.incr(key)
        event["extra"]["event_count"] = incr_cnt
        event["extra"]["sr_exchash"] = exchash
        if self.should_propagate(incr_cnt):
            return event


    def dedupe_logger(self, event):
        hash_hint = self.get_hash_hint_for_logger(event)
        loghash = self.filter_pii(self.get_hash(hash_hint))
        key = f"sentry:logger:{loghash}:{int(time.time() // 1000)}"
        incr_cnt = self.redis_connection.incr(key)
        event["extra"]["event_count"] = incr_cnt
        event["extra"]["sr_loghash"] = loghash

        if self.should_propagate(incr_cnt):
            return event


    def handle_log_error(self, event):
        ev_logger = event["logger"]
        ev_msg = event["logentry"]["message"]
        silenced_messages = SILENCED_LOGGER_MESSAGES.get(ev_logger)
        if silenced_messages:
            for msg in silenced_messages:
                if ev_msg.startswith(msg):
                    logger.info(f"filtered via logger: {ev_msg!r}")
                    return None

        return self.dedupe_logger(event)


    def handle_exception_raise(self, event, hint):
        exc_type, exc_value, tb = hint["exc_info"]
        if exc_type.__name__ in EXCLUDE_EXCEPTION_CLASSES:
            logger.info(f"filtered via exception classes: {self.filter_pii(exc_value)!r}")
            return None

        try:
            msg = self.filter_pii(str(exc_value))
            if any(msg.startswith(x) for x in EXCLUDE_EXCEPTION_MSG_PREFIXES):
                logger.info(f"filtered via exception prefix: {exc_value!r}")
                return None
        except AttributeError:
            pass
        return self.dedupe_exc(event)


    def get_extra_attributes(self):
        return {
            "instance_name": get_ec2_instance_name(),
            "instance_id": get_ec2_instance_id(),
        }

    def filter_events(self, event, hint):
        event["modules"] = {}  # reduced payload by around 30-35%
        event["extra"].update(self.get_extra_attributes())

        if GIT_COMMIT_HASH:
            if "tags" not in event:
                event["tags"] = {}
            event["tags"]["commit_hash"] = GIT_COMMIT_HASH[:10]

        try:
            event = self.filter_pii(event)
            logger.info("event is filtered")
        except Exception:
            logger.warning("event is not filtered")

        if "logentry" in event:
            logger.info("sentry_log_error")
            return self.handle_log_error(event)
        elif "exc_info" in hint:
            logger.info("sentry_exception_raise")
            return self.handle_exception_raise(event, hint)
        else:

            logger.warning(f"nothandled:{event}:{hint}")

        if randint(0, 30) == 5:  # log some samples
            logger.warning(json.dumps(event))

        logger.info("event filtered successfully")

        return event

    @staticmethod
    def apply_mask(value):
        val = value[: int(len(value) / 2)] + "*" * int(len(value) / 2)
        return value.replace(value, val)

    def filter_pii(self, event):

        pattern_freq = {}
        for pattern in PII_REGEX_PATTERNS:
            pattern_freq[str(pattern)] = len(re.findall(PII_REGEX_PATTERNS[pattern], str(event)))

        for pattern in pattern_freq:
            for _ in range(pattern_freq[pattern]):

                regex = re.search(PII_REGEX_PATTERNS[pattern], str(event))

                if regex:
                    event = str(event).replace(regex.group().rstrip(), self.apply_mask(regex.group().rstrip()))
        try:
            event = eval(json.loads(json.dumps(event, indent=4, sort_keys=True)))
        except Exception:
            pass

        return event
