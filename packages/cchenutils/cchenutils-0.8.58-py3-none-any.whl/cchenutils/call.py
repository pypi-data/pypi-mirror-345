import subprocess


def call(cmd):
    return subprocess.call(cmd, shell=True)
