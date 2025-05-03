from datetime import datetime
from typing import Dict


class Interpret:
    def __init__(self, data: dict):
        self._name = data.get('name', '')
        self._nachname = data.get('nachname', '')

    def full_name(self):
        if self._name == self._nachname:
            return self._name
        else:
            return '{} {}'.format(self._name, self._nachname)

    @property
    def name(self):
        return self._name

    @property
    def nachname(self):
        return self._nachname

    def __repr__(self):
        return f"Interpret(name='{self.name}', nachname='{self.nachname}')"


class Besetzung:
    def __init__(self, data: dict):
        self._anzahl_instrumente = data.get('anzahlInstrumente', 0)
        self._anzahl_spieler = data.get('anzahlSpieler', 0)
        self._anzahl_stimmen = data.get('anzahlStimmen', 0)
        self._bezeichnung = data.get('bezeichnung', '')

    @property
    def anzahl_instrumente(self):
        return self._anzahl_instrumente

    @property
    def anzahl_spieler(self):
        return self._anzahl_spieler

    @property
    def anzahl_stimmen(self):
        return self._anzahl_stimmen

    @property
    def bezeichnung(self):
        return self._bezeichnung

    def __repr__(self):
        return (f"Besetzung(anzahl_instrumente={self.anzahl_instrumente}, "
                f"anzahl_spieler={self.anzahl_spieler}, "
                f"anzahl_stimmen={self.anzahl_stimmen}, "
                f"bezeichnung='{self.bezeichnung}')")


class Verlag:
    def __init__(self, data: dict):
        self._type = data.get('type', '')
        self._ip_name_number = data.get('ipNameNumber', None)
        self._name = data.get('name', '')
        self._is_bevollmaechtigt = data.get('isBevollmaechtigt', False)
        self._is_eigenes_konto = data.get('isEigenesKonto', False)
        self._identifier = data.get('identifier', '')

    @property
    def type(self):
        return self._type

    @property
    def ip_name_number(self):
        return self._ip_name_number

    @property
    def name(self):
        return self._name

    @property
    def is_bevollmaechtigt(self):
        return self._is_bevollmaechtigt

    @property
    def is_eigenes_konto(self):
        return self._is_eigenes_konto

    @property
    def identifier(self):
        return self._identifier

    def __repr__(self):
        return (f"Verlag(type='{self.type}', ip_name_number={self.ip_name_number}, "
                f"name='{self.name}', is_bevollmaechtigt={self.is_bevollmaechtigt}, "
                f"is_eigenes_konto={self.is_eigenes_konto}, identifier='{self.identifier}')")


class Urheber:
    def __init__(self, data: dict):
        self._type = data.get('type', 'URHEBER')
        self._ip_name_number = data.get('ipNameNumber', None)
        self._name = data.get('name', '')
        self._vorname = data.get('vorname', '')
        self._nachname = data.get('nachname', '')
        self._identifier = data.get('identifier', '')
        self._rolle = data.get('rolle', '')
        self._is_bevollmaechtigt = data.get('isBevollmaechtigt', False)
        self._is_eigenes_konto = data.get('isEigenesKonto', False)

    @property
    def type(self):
        return self._type

    @property
    def ip_name_number(self):
        return self._ip_name_number

    @property
    def name(self):
        return self._name

    @property
    def vorname(self):
        return self._vorname

    @property
    def nachname(self):
        return self._nachname

    @property
    def identifier(self):
        return self._identifier

    @property
    def rolle(self):
        return self._rolle

    @property
    def is_bevollmaechtigt(self):
        return self._is_bevollmaechtigt

    @property
    def is_eigenes_konto(self):
        return self._is_eigenes_konto

    def __repr__(self):
        return (f"Urheber(vorname='{self.vorname}', nachname='{self.nachname}', rolle='{self.rolle}', "
                f"identifier='{self.identifier}', bevollmaechtigt={self.is_bevollmaechtigt})")


class Werk:
    def __init__(self, data: Dict):
        # Read-only fields (initialized once)
        self._is_eigenes_werk = data.get('isEigenesWerk', False)
        self._verlagswerknummern = data.get('verlagswerknummern', [])
        self._isrc = data.get('isrc', [])
        self._erstellung_datum = datetime.strptime(data.get('erstellungDatum', '1970-01-01'), '%Y-%m-%d')
        self._titel = data.get('titel', 'Unknown Title')
        self._werknummer = data.get('werknummer', '')
        self._werkfassungsnummer = data.get('werkfassungsnummer', '')
        self._sonstige_titel = data.get('sonstigeTitel', [])
        self._interpreten = []
        for interpret in data.get('interpreten', []):
            self._interpreten.append(Interpret(interpret))
        self._sprache = data.get('sprache', '')
        self._gattung = data.get('gattung', '')
        self._besetzung = []
        for besetzung in data.get('besetzung', []):
            self._besetzung.append(Besetzung(besetzung))
        self._iwk = data.get('iwk', '')
        self._frei_v = data.get('freiV', False)
        self._verbundene_schutzfrist = data.get('verbundeneSchutzfrist', False)
        self._verteilung_ar = data.get('verteilungAr', 'VAR')  # Either LOSE or VAR
        self._verteilung_vr = data.get('verteilungVr', 'VAR')  # Either LOSE or VAR
        self._originalverlage = []
        for verlag in data.get('originalverlage', []):
            self._originalverlage.append(Verlag(verlag))
        self._subverlage = []
        for verlag in data.get('subverlage', []):
            self._subverlage.append(Verlag(verlag))

        self._aenderung_datum = datetime.strptime(data.get('aenderungDatum', '1970-01-01'), '%Y-%m-%d')
        self._spieldauer = data.get('spieldauer', 0)  # in seconds
        self._status = data.get('status', 0)

        # Urheber (authors/composers)
        self._urheber = []
        for urheber in data.get('urheber', []):
            self._urheber.append(Urheber(urheber))

    # Read-only properties
    @property
    def is_eigenes_werk(self):
        return self._is_eigenes_werk

    @property
    def verlagswerknummern(self):
        return self._verlagswerknummern

    @property
    def isrc(self):
        return self._isrc

    @property
    def erstellung_datum(self):
        return self._erstellung_datum

    @property
    def titel(self):
        return self._titel

    @property
    def werknummer(self):
        return self._werknummer

    @property
    def werkfassungsnummer(self):
        return self._werkfassungsnummer

    @property
    def sonstige_titel(self):
        return self._sonstige_titel

    @property
    def interpreten(self):
        return self._interpreten

    @property
    def sprache(self):
        return self._sprache

    @property
    def gattung(self):
        return self._gattung

    @property
    def besetzung(self):
        return self._besetzung

    @property
    def iwk(self):
        return self._iwk

    @property
    def frei_v(self):
        return self._frei_v

    @property
    def verbundene_schutzfrist(self):
        return self._verbundene_schutzfrist

    @property
    def verteilung_ar(self):
        return self._verteilung_ar

    @property
    def verteilung_vr(self):
        return self._verteilung_vr

    @property
    def originalverlage(self):
        return self._originalverlage

    @property
    def subverlage(self):
        return self._subverlage

    @property
    def aenderung_datum(self):
        return self._aenderung_datum

    @property
    def spieldauer(self):
        return self._spieldauer

    @property
    def status(self):
        return self._status

    @property
    def urheber(self):
        return self._urheber

    def __repr__(self):
        return f"Werk(titel='{self.titel}', werknummer='{self.werknummer}', spieldauer={self.spieldauer}s)"
