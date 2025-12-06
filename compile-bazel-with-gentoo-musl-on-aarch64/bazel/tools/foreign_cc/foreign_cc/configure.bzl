# Stub configure.bzl for local foreign_cc override

def configure(*args, **kwargs):
    print("Stub configure called with", kwargs.get("name", "<unknown>"))

def configure_make(*args, **kwargs):
    print("Stub configure_make called with", kwargs.get("name", "<unknown>"))

__all__ = ["configure", "configure_make"]

