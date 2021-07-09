#!/usr/bin/env bash

set -e

diff <(sed -n '/# QUALITY-ASSURANCE-START/,/# QUALITY-ASSURANCE-END/p' .github/workflows/master.yml) <(sed -n '/# QUALITY-ASSURANCE-START/,/# QUALITY-ASSURANCE-END/p' .github/workflows/pr.yml) || (echo 'QUALITY-ASSURANCE section in .github/workflows/master.yml and .github/workflows/pr.yml is different' && false)
