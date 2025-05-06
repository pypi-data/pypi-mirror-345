# memememe

A simple Python module to fetch random GIFs from Tenor using a search term.

## Usage
```python
from memememe import get_random_gif

key = '' # Tenor V2 api key
gif = get_random_gif("cat", key)
print(gif)
```