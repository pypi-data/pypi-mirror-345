#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

# Avoid having code to make anamnesis optional in multiple places
try:
    from anamnesis import AbstractAnam, register_class
except ImportError:
    AbstractAnam = object

    def register_class(x):
        return None

__all__ = ['AbstractAnam', 'register_class']
