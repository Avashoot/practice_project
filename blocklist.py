"""
blocklist.py

This files just contains the blocklist of jwt Tokens
It will bw improved by app and the logout resource so that the Token can be added 
to the blocklist when the users log's out
"""


BLOCKLIST = set() #type:ignore