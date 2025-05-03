# pymusictheory

`pymusictheory` is a Python library for performing calculations with musical notes. It provides tools to work with notes, intervals, and chords, both in the context of octaves and without. This library is useful for music theory analysis, algorithmic composition, and other musical applications.

Key features:
- Correctly returning double accidentals when adding intervals to notes. Example: B# + M3 = D##

Not implemented:
- Adding intervals to notes with double accidentals. For example, B## + M3 = D###

## Overview of Classes

### 1. `NoteLetter`
Represents the basic musical note letters (C, D, E, F, G, A, B). It supports operations like addition and subtraction to navigate the musical scale.

- **Example Usage:**
  ```python
  from pymusictheory import NoteLetter

  note = NoteLetter.C + 4  # G
  print(note)  # Output: G
  ```

### 2. `NoteAlteration`
Represents alterations to a note (sharp, flat, natural). It defines how many semitones the alteration modifies the note by.

- **Example Usage:**
  ```python
  from pymusictheory import NoteAlteration

  alteration = NoteAlteration.SHARP
  print(alteration.semitone_difference)  # Output: 1
  ```

### 3. `Note`
Represents a musical note without a specific octave. It combines a `NoteLetter` and a `NoteAlteration` to define a note like C#, Db, or F.

- **Key Features:**
  - Convert from string representation (e.g., "C#").
  - Calculate semitone offsets from C.
  - Generate all possible notes for a given semitone offset.

- **Example Usage:**
  ```python
  from pymusictheory import Note

  note = Note.from_str("C#")
  print(note.semitone_offset)  # Output: 1
  ```

### 4. `NoteInOctave`
Represents a musical note in a specific octave. It extends `Note` by adding an octave number and supports operations like calculating absolute semitone offsets and adding intervals.

- **Key Features:**
  - Convert from string representation (e.g., "C4").
  - Calculate absolute semitone offsets from C0.
  - Add intervals to notes.

- **Example Usage:**
  ```python
  from pymusictheory import NoteInOctave

  note = NoteInOctave.from_str("C4")
  print(note.absolute_semitone_offset)  # Output: 48
  ```

### 5. `Interval`
Represents musical intervals (e.g., major third, perfect fifth). It defines the semitone and letter distances for each interval.

- **Example Usage:**
  ```python
  from pymusictheory import Interval

  interval = Interval.MAJOR_THIRD
  print(interval.semitone_distance)  # Output: 4
  ```

### 6. `Chord`
Represents a set of `NoteInOctave` objects, forming a chord. It allows iteration over the notes in the chord.

- **Example Usage:**
  ```python
  from pymusictheory import NoteInOctave, Chord

  chord = Chord({NoteInOctave.from_str("C4"), NoteInOctave.from_str("E4"), NoteInOctave.from_str("G4")})
  for note in chord:
      print(note)
  ```

## Relationships Between Classes
- `NoteLetter` and `NoteAlteration` combine to form a `Note`.
- `Note` and an octave number combine to form a `NoteInOctave`.
- `Interval` can be added to a `NoteInOctave` to calculate a new note.
- A `Chord` is a collection of `NoteInOctave` objects.

## Common Use Cases

### 1. Calculate Semitone Offsets
```python
from pymusictheory import Note

note = Note.from_str("F#")
print(note.semitone_offset)  # Output: 6
```

### 2. Add Intervals to Notes
```python
from pymusictheory import NoteInOctave, Interval

note = NoteInOctave.from_str("C4")
new_note = note + Interval.PERFECT_FIFTH
print(new_note)  # Output: G4

note = NoteInOctave.from_str("B#3")
new_note = note + Interval.MAJOR_THIRD
print(new_note)  # Output: D##4
```

### 3. Generate Chords
```python
from pymusictheory import NoteInOctave, Chord

chord = Chord({NoteInOctave.from_str("C4"), NoteInOctave.from_str("E4"), NoteInOctave.from_str("G4")})
print(chord)  # Output: {C4, E4, G4}
```

## Installation
Ensure you have Python 3.13 or higher installed. Install the library using:
```bash
pip install pymusictheory
```

## Contributing
Contributions are welcome! Please submit issues or pull requests on the GitHub repository.

## License
This project is licensed under the MIT License.
