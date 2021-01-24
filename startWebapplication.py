from backend.service import service

"""URL der Datenbank"""
databaseURL = "192.168.178.54"

"""URL des Backendservice, nur ändern wenn er auf einem anderen System gestartet wurde."""
serviceURL = "localhost"

"""Startet das Backend"""
service = service(databaseURL)
