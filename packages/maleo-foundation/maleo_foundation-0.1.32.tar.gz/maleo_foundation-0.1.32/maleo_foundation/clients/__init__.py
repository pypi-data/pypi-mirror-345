from __future__ import annotations
from .general import BaseGeneralClients
from .google import GoogleClients

class BaseClients:
    General = BaseGeneralClients
    Google = GoogleClients