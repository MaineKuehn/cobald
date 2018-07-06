import threading
import pytest
import time
import asyncio

import trio

from cobald.utility.concurrent.meta_runner import MetaRunner


class TerminateRunner(Exception):
    pass


class TestMetaRunner(object):
    def test_abort_subroutine(self):
        """Test that failing subroutines abort runners"""
        def abort():
            raise TerminateRunner

        for flavour in (threading,):
            runner = MetaRunner()
            runner.register_payload(abort, flavour=flavour)
            with pytest.raises(TerminateRunner):
                runner.run()

            def noop():
                return

            def loop():
                while True:
                    time.sleep(0)

            runner = MetaRunner()
            runner.register_payload(noop, loop, flavour=flavour)
            runner.register_payload(abort, flavour=flavour)
            with pytest.raises(TerminateRunner):
                runner.run()

    def test_abort_coroutine(self):
        """Test that failing coroutines abort runners"""
        async def abort():
            raise TerminateRunner

        for flavour in (asyncio, trio):
            runner = MetaRunner()
            runner.register_payload(abort, flavour=flavour)
            with pytest.raises(TerminateRunner):
                runner.run()

            async def noop():
                return

            async def loop():
                while True:
                    await flavour.sleep(0)
            runner = MetaRunner()

            runner.register_payload(noop, loop, flavour=flavour)
            runner.register_payload(abort, flavour=flavour)
            with pytest.raises(TerminateRunner):
                runner.run()
