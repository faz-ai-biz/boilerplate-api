#!/usr/bin/env bash
# test.sh: Run the test suite with coverage reporting.

pytest --cov=src --cov-report=term-missing
