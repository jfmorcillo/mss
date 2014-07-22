#!/bin/bash
urpmi.update --no-ignore Core\ Updates\ Testing
urpmi.update --update Core\ Updates\ Testing

exit $?
