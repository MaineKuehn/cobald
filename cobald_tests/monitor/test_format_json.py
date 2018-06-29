import json
import io
import logging
import threading
import time


from cobald.monitor.format_json import JsonFormatter


class CapturingHandler(logging.StreamHandler):
    @property
    def content(self):
        return self.stream.getvalue()

    def __init__(self):
        super().__init__(stream=io.StringIO())


_test_index = 0
_index_lock = threading.Lock()


def make_test_logger(base_name: str = 'test_logger'):
    with _index_lock:
        global _test_index
        log_name = base_name + '.test%d' % _test_index
        _test_index += 1
    logger = logging.getLogger(log_name)
    handler = CapturingHandler()
    logger.handlers = [handler]
    return logger, handler


class TestFormatJson(object):
    def test_payload(self):
        for payload in (
                {'a': 'a'},
                {str(i): i for i in range(20)},
        ):
            logger, handler = make_test_logger(__name__)
            handler.formatter = JsonFormatter()
            logger.critical('message', payload)
            data = json.loads(handler.content)
            assert len(data) == len(payload) + 2
            assert data.pop('message') == 'message'
            assert data.pop('time')
            assert data == payload

    def test_default_timestamp(self):
        now = time.time()
        payload = {'a': 'a', '1': 1, '2.2': 2.2}
        logger, handler = make_test_logger(__name__)
        handler.formatter = JsonFormatter()
        logger.critical('message', payload, extra={'create': now})
        data = json.loads(handler.content)
        assert len(data) == len(payload) + 2
        # from Formatter and LogRecord
        ct = time.localtime(now)
        msecs = (now - int(now)) * 1000
        default_time_string = logging.Formatter.default_msec_format % (
            time.strftime(logging.Formatter.default_time_format, ct),
            msecs
        )
        assert data.pop('time') == default_time_string

    def test_explicit_timestamp(self):
        now = time.time()
        payload = {'a': 'a', '1': 1, '2.2': 2.2}
        logger, handler = make_test_logger(__name__)
        handler.formatter = JsonFormatter(datefmt='%Y')
        logger.critical('message', payload, extra={'create': now})
        data = json.loads(handler.content)
        assert len(data) == len(payload) + 2
        # from Formatter and LogRecord
        ct = time.localtime(now)
        default_time_string = time.strftime('%Y', ct)
        assert data.pop('time') == default_time_string

    def test_disabled_timestamp(self):
        now = time.time()
        payload = {'a': 'a', '1': 1, '2.2': 2.2}
        logger, handler = make_test_logger(__name__)
        handler.formatter = JsonFormatter(datefmt='')
        logger.critical('message', payload, extra={'create': now})
        data = json.loads(handler.content)
        assert len(data) == len(payload) + 1
        assert 'time' not in data

