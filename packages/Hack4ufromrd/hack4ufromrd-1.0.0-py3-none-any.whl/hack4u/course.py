#!/usr/bin/env python3

class Course:

    def __init__(self, name, duration, link):
        self.name = name
        self.duration = duration
        self.link = link


    def __repr__(self):
        return f"\nCurso: {self.name} | Duracion: {self.duration} horas | Link: {self.link}"



courses = [
        Course("Introduccion a Linux", 15, "https://hack4u.io/cursos/introduccion-a-linux/"),
        Course("Personalizacion de Linux", 3, "https://hack4u.io/cursos/personalizacion-de-entorno-en-linux/"),
        Course("Introduccion al Hacking", 53, "https://hack4u.io/cursos/introduccion-al-hacking/"),
        Course("Python Ofensivo", 35, "https://hack4u.io/cursos/python-ofensivo/")
]


def list_course():
    for course in courses:
        print(course)

def search_course_by_name(name):
    for course in courses:
        if course.name == name:
            return course

    return None


