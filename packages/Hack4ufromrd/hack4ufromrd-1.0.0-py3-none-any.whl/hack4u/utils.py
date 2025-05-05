#!/usr/bin/env python3

from .course import courses


def total_duration():
    return sum(course.duration for course in courses)
