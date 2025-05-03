# PyGEMASearch

PyGEMASearch is a Python package for searching songs in the GEMA database using the public API.

## Installation

```sh
pip install git+https://github.com/DonMikone/PyGEMASearch.git
```

## Usage

```python
from gemasearch import GemaMusicSearch

gema_search = GemaMusicSearch()
result = gema_search.search("Bohemian Rhapsody")
print(result)
```

# GemaMusicSearch API Documentation

## Overview
`GemaMusicSearch` provides an interface to search for musical works in the GEMA database.

## Usage

### Initialize the Search
```python
from gemasearch import GemaMusicSearch

gema_search = GemaMusicSearch()
```

### Search for a Work by Title
```python
results = gema_search.search("Bohemian Rhapsody")
for werk in results:
    print(werk.titel)
```

#### `search` Function
```python
def search(self, search_string: str, page: int = 0, page_size: int = 50, fuzzy_search=True):
```
- **search_string** (*str*): The title or name of any or multiple composers/authors of the work to search for.
- **page** (*int*): The page number of the results (default is `0`).
- **page_size** (*int*): Number of results per page (default is `50`).
- **fuzzy_search** (*bool*): Whether to perform a fuzzy search (`True`) or an exact match (`False`).
- **Returns**: A list of `Werk` objects or `None` if an error occurs.

## Notes
- Use fuzzy search for better results when searching by title.

### Search for a Work by Werknummer
```python
results = gema_search.search_werknummer("17680241-007")
for werk in results:
    print(werk.titel)
```

#### `search_werknummer` Function
```python
def search_werknummer(self, number_string: str, page: int = 0, page_size: int = 50):
```
- **number_string** (*str*): The Werknummer to search for.
- **page** (*int*): The page number of the results (default is `0`).
- **page_size** (*int*): Number of results per page (default is `50`).
- **Returns**: A list of `Werk` objects or `None` if an error occurs.

### Search for a Work by ISRC
```python
results = gema_search.search_isrc("DEUM72301260")
for werk in results:
    print(werk.titel)
```

#### `search_isrc` Function
```python
def search_isrc(self, isrc: str, page: int = 0, page_size: int = 50):
```
- **isrc** (*str*): The ISRC code to search for.
- **page** (*int*): The page number of the results (default is `0`).
- **page_size** (*int*): Number of results per page (default is `50`).
- **Returns**: A list of `Werk` objects or `None` if an error occurs.

### Example: Fetching Authors and ISRC of a Track
```python
results = gema_search.search("Bohemian Rhapsody")
for werk in results:
    print(f"Title: {werk.titel}")
    print("Authors:")
    for urheber in werk.urheber:
        print(f"  - {urheber.vorname} {urheber.nachname} ({urheber.rolle})")
    print(f"ISRC: {werk.isrc}")
```

# Example Usage of the Wrapper Classes

This section provides an overview of how to use the wrapper classes to iterate over results, fetch the names of the authors/composers, and e.g. retrieve the ISRC code of a track.

## Example Data
Assuming we have a list of `Werk` objects, we can perform various operations on them.

### Iterating Over Results and Fetching Author/Composer Names
```python
werke = gema_search.search("Bohemian Rhapsody")  # Example data instances

# Iterate over works and print their titles and authors
for werk in werke:
    print(f"Title: {werk.titel}")
    print("Authors/Composers:")
    for urheber in werk.urheber:
        print(f"  - {urheber.vorname} {urheber.nachname} ({urheber.rolle})")
    print()
```

### Retrieving the ISRC Code of a Track
```python
# Fetch ISRC codes of a specific work
werk = werke[0]  # Example: selecting the first work
if werk.isrc:
    print(f"ISRC Codes for '{werk.titel}': {', '.join(werk.isrc)}")
else:
    print(f"No ISRC codes available for '{werk.titel}'.")
```

## List of Properties for Each Class

### **Werk**
- `is_eigenes_werk`
- `verlagswerknummern`
- `isrc`
- `erstellung_datum`
- `titel`
- `werknummer`
- `werkfassungsnummer`
- `sonstige_titel`
- `interpreten`
- `sprache`
- `gattung`
- `besetzung`
- `iwk`
- `frei_v`
- `verbundene_schutzfrist`
- `verteilung_ar`
- `verteilung_vr`
- `originalverlage`
- `subverlage`
- `aenderung_datum`
- `spieldauer`
- `status`
- `urheber`

### **Urheber** (Author/Composer)
- `type`
- `ip_name_number`
- `name`
- `vorname`
- `nachname`
- `identifier`
- `rolle`
- `is_bevollmaechtigt`
- `is_eigenes_konto`

### **Interpret** (Performer)
- `name`
- `nachname`

### **Besetzung** (Instrumentation)
- `anzahl_instrumente`
- `anzahl_spieler`
- `anzahl_stimmen`
- `bezeichnung`

### **Verlag** (Publisher)
- `type`
- `ip_name_number`
- `name`
- `is_bevollmaechtigt`
- `is_eigenes_konto`
- `identifier`

## License
GPLv3


