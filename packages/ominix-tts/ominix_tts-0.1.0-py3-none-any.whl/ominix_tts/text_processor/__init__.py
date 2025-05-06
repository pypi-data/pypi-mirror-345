import os

from .symbols import symbols as symbols_v1
from .symbols2 import symbols as symbols_v2

_symbol_to_id_v1 = {s: i for i, s in enumerate(symbols_v1)}
_symbol_to_id_v2 = {s: i for i, s in enumerate(symbols_v2)}

def cleaned_text_to_sequence(cleaned_text, version=None):
  '''Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
    Args:
      text: string to convert to a sequence
    Returns:
      List of integers corresponding to the symbols in the text
  '''
  if version is None:version=os.environ.get('version', 'v2')
  if version == "v1":
    phones = [_symbol_to_id_v1[symbol] for symbol in cleaned_text]
  else:
    phones = [_symbol_to_id_v2[symbol] for symbol in cleaned_text]

  return phones

