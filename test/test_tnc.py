#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test connect frame commands over a high quality simulated audio channel.

Near end-to-end test for sending / receiving connection control frames through the
TNC and modem and back through on the other station. Data injection initiates from the
queue used by the daemon process into and out of the TNC.

Can be invoked from CMake, pytest, coverage or directly.

Uses util_tnc_I[RS]S.py in separate process to perform the data transfer.

@author: DJ2LS, N2KIQ
"""

import multiprocessing
import os
import sys
import time

import log_handler
import pytest
import structlog

try:
    import test.util_tnc_IRS as irs
    import test.util_tnc_ISS as iss
except ImportError:
    import util_tnc_IRS as irs
    import util_tnc_ISS as iss


# This test is currently a little inconsistent.
@pytest.mark.parametrize("command", ["CONNECT"])
@pytest.mark.flaky(reruns=2)
def test_tnc(command, tmp_path):
    log_handler.setup_logging(filename=tmp_path / "test_tnc", level="INFO")
    log = structlog.get_logger("test_tnc")

    iss_proc = multiprocessing.Process(target=iss.t_arq_iss, args=[command, tmp_path])
    irs_proc = multiprocessing.Process(target=irs.t_arq_irs, args=[command, tmp_path])
    log.debug("Starting threads.")
    iss_proc.start()
    irs_proc.start()

    time.sleep(12)

    log.debug("Terminating threads.")
    irs_proc.terminate()
    iss_proc.terminate()
    irs_proc.join()
    iss_proc.join()

    for idx in range(2):
        try:
            os.unlink(tmp_path / f"hfchannel{idx+1}")
        except FileNotFoundError as fnfe:
            log.debug(f"Unlinking pipe: {fnfe}")

    assert iss_proc.exitcode in [0, -15], f"Transmit side failed test. {iss_proc}"
    assert irs_proc.exitcode in [0, -15], f"Receive side failed test. {irs_proc}"


if __name__ == "__main__":
    # Run pytest with the current script as the filename.
    ecode = pytest.main(["-s", "-v", sys.argv[0]])
    if ecode == 0:
        print("errors: 0")
    else:
        print(ecode)
