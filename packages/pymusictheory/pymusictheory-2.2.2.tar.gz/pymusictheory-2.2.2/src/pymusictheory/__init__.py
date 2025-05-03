"""
Calculations on notes, both in the context of octaves and without.

Vocabulary:
"semitone offset": The number of semitones away from C in the octave.
"absolute semitone offset": The number of semitones away from C0.
"semitone distance": A number of semitones.
"""

from enum import Enum
from functools import total_ordering
from typing import Self
from collections.abc import Iterator


# Enum for musical note letters
class NoteLetter(Enum):
    """
    Enum representing musical note letters.
    """

    C = 0
    D = 1
    E = 2
    F = 3
    G = 4
    A = 5
    B = 6

    def __str__(self) -> str:
        return self.name

    def __add__(self, other: int) -> "NoteLetter":
        """
        When adding letters, treat them as integers and wrap around if necessary.
        """
        new_value = (self.value + other) % len(NoteLetter)
        return NoteLetter(new_value)

    def __sub__(self, other: int) -> "NoteLetter":
        """
        When subtracting letters, treat them as integers and wrap around if necessary.
        """
        new_value = (self.value - other) % len(NoteLetter)
        return NoteLetter(new_value)

    @property
    def semitone_offset(self) -> int:
        """
        Returns how many semitones this letter is away from C.
        """
        match self:
            case NoteLetter.C:
                return 0
            case NoteLetter.D:
                return 2
            case NoteLetter.E:
                return 4
            case NoteLetter.F:
                return 5
            case NoteLetter.G:
                return 7
            case NoteLetter.A:
                return 9
            case NoteLetter.B:
                return 11

    @property
    def __int__(self) -> int:
        return self.value

    @classmethod
    def from_str(cls, s: str) -> "NoteLetter":
        """
        Converts a string to a NoteLetter by matching the string with the name of each enum variant.
        """
        for note in cls:
            if note.name == s:
                return note
        raise ValueError(f"Invalid note letter string: {s}")


class NoteAlteration(Enum):
    """
    Enum representing musical note alterations.
    """

    SHARP = 1
    FLAT = -1
    NATURAL = 0
    DOUBLE_SHARP = 2
    DOUBLE_FLAT = -2

    @property
    def semitone_difference(self) -> int:
        """
        Returns how many semitones this alteration modifies the note by.
        """
        return self.value

    def __int__(self) -> int:
        return self.semitone_difference

    def __str__(self) -> str:
        match self:
            case NoteAlteration.SHARP:
                return "♯"
            case NoteAlteration.FLAT:
                return "♭"
            case NoteAlteration.NATURAL:
                return "♮"
            case NoteAlteration.DOUBLE_SHARP:
                return "𝄪"
            case NoteAlteration.DOUBLE_FLAT:
                return "𝄫"

    @classmethod
    def from_str(cls, s: str) -> "NoteAlteration":
        match s:
            case "♯":
                return cls.SHARP
            case "#":
                return cls.SHARP
            case "♭":
                return cls.FLAT
            case "b":
                return cls.FLAT
            case "♮":
                return cls.NATURAL
            case "n":
                return cls.NATURAL
            case "𝄪":
                return cls.DOUBLE_SHARP
            case "##":
                return cls.DOUBLE_SHARP
            case "𝄫":
                return cls.DOUBLE_FLAT
            case "bb":
                return cls.DOUBLE_FLAT
            case _:
                raise ValueError(f"Invalid alteration string: {s}")


class Note:
    """
    An abstract musical note, without a specific octave.
    """

    def __init__(self, letter: NoteLetter, alteration: NoteAlteration):
        self.letter = letter
        self.alteration = alteration

    @classmethod
    def from_str(cls, s: str) -> Self:
        """
        Allows creating a Note from a string representation like "C", "C#" or "Db".
        """
        if len(s) == 1:
            return cls(NoteLetter.from_str(s), NoteAlteration.NATURAL)

        letter = NoteLetter.from_str(s[0])
        alteration = NoteAlteration.from_str(s[1:])
        return cls(letter, alteration)

    @property
    def semitone_offset(self) -> int:
        """
        Returns how many semitones away from C this note is. The semitone offset is the sum of the letter's semitone offset and the alteration's semitone difference.

        Examples:
        - C = 0
        - C# = 1
        - C## = 2
        - Cb = -1
        - Cbb = -2
        - B# = 12
        - B## = 13
        """

        return self.letter.semitone_offset + self.alteration.semitone_difference

    @classmethod
    def from_semitone_offset(cls, semitone_offset: int) -> set[Self]:
        """
        Returns all possible notes that are a specific number of semitones away from C.

        Examples:
        - 0 -> C and Dbb
        - -1 -> Cb
        - -2 -> Cbb
        - 1 -> C# and Db
        - 7 -> G, F## and Abb
        - 8 -> G# and Ab
        - 11 -> B and A##
        - 12 -> B#
        - 13 -> B##
        """

        # Loop through all possible enumerations of NoteLetter and NoteAlteration
        notes = set(
            cls(note_letter, note_alteration)
            for note_letter in NoteLetter
            for note_alteration in NoteAlteration
            if note_letter.semitone_offset + note_alteration.semitone_difference
            == semitone_offset
        )

        return notes

    def __eq__(self, other: object) -> bool:
        """
        Two non-octaved notes are only equal if they have the same letter and alteration.
        """
        if not isinstance(other, Note):
            return NotImplemented
        return self.letter == other.letter and self.alteration == other.alteration

    # lt is not implemented because it doesn't make sense to compare notes without an octave

    def __str__(self) -> str:
        return (
            f"{self.letter}{self.alteration}"
            if self.alteration != NoteAlteration.NATURAL
            else str(self.letter)
        )

    def __repr__(self) -> str:
        return f"Note({self.letter}, {self.alteration})"

    def __hash__(self) -> int:
        return hash((self.letter, self.alteration))


class Interval(Enum):
    """
    Enum representing musical intervals with their semitone and letter distances.
    """

    PERFECT_UNISON = (0, 0)
    MINOR_SECOND = (1, 1)
    MAJOR_SECOND = (2, 1)
    MINOR_THIRD = (3, 2)  # 3 semitones, 2 letter steps
    MAJOR_THIRD = (4, 2)  # etc.
    PERFECT_FOURTH = (5, 3)
    PERFECT_FIFTH = (7, 4)
    MINOR_SIXTH = (8, 5)
    MAJOR_SIXTH = (9, 5)
    MINOR_SEVENTH = (10, 6)
    MAJOR_SEVENTH = (11, 6)
    PERFECT_OCTAVE = (12, 7)

    @property
    def semitone_distance(self) -> int:
        """
        Get the semitone distance of the interval.
        """
        return self.value[0]

    @property
    def letter_distance(self) -> int:
        """
        Get the letter distance of the interval.
        """
        return self.value[1]


@total_ordering
class NoteInOctave:
    """
    A concrete musical note in a specific octave
    """

    def __init__(self, note: Note, octave: int):
        self.note = note
        assert octave >= 0, "Octaves cannot be negative"
        self.octave = octave

    @classmethod
    def from_absolute_semitone_offset(cls, absolute_semitone_offset: int) -> set[Self]:
        """
        Returns all possible notes that are a specific number of semitones away from C0.
        """

        # Find the candidate offset within the octave, and the candidate octave.
        #
        # Edge cases close to octave changes need to be handled carefully. Let X denote an octave.
        #
        # Case 1: "CX" can be interpreted as being in octave X-1 (B#)
        # Case 2: "C#X" can be interpreted as being in octave X-1 (B##)
        # Case 3: "BY" can be interpreted as being in octave Y+1 (Cb)
        # Case 4: "BbY" can be interpreted as being in octave Y+1 (Cbb)

        if absolute_semitone_offset % 12 == 0:
            semitone_offset_candidates = {0, 12}
            candidate_octaves = {
                absolute_semitone_offset // 12,
                absolute_semitone_offset // 12 - 1,
            }
        elif absolute_semitone_offset % 12 == 1:
            semitone_offset_candidates = {1, 13}
            candidate_octaves = {
                absolute_semitone_offset // 12,
                absolute_semitone_offset // 12 - 1,
            }
        elif absolute_semitone_offset % 12 == 11:
            semitone_offset_candidates = {11, -1}
            candidate_octaves = {
                absolute_semitone_offset // 12,
                absolute_semitone_offset // 12 + 1,
            }
        elif absolute_semitone_offset % 12 == 10:
            semitone_offset_candidates = {10, -2}
            candidate_octaves = {
                absolute_semitone_offset // 12,
                absolute_semitone_offset // 12 + 1,
            }
        else:
            semitone_offset_candidates = {absolute_semitone_offset % 12}
            candidate_octaves = {absolute_semitone_offset // 12}

        # Find all possible non-octaved notes
        notes = set.union(
            *(
                Note.from_semitone_offset(semitone_offset)
                for semitone_offset in semitone_offset_candidates
            )
        )

        # Keep only notes and octaves such that their semitone offset adds up to the absolute semitone offset
        return set(
            cls(note, octave)
            for note in notes
            for octave in candidate_octaves
            if note.semitone_offset + octave * 12 == absolute_semitone_offset
        )

    def from_semitone_distance(self, semitone_offset: int) -> set["NoteInOctave"]:
        """
        Returns all possible notes that are a specific number of semitones away from this note
        """

        return NoteInOctave.from_absolute_semitone_offset(
            self.absolute_semitone_offset + semitone_offset
        )

    def __add__(self, interval: Interval) -> "NoteInOctave":
        """
        Adds an interval to the note, potentially changing its octave.
        """

        # This is only implemented for notes without double accidentals. Otherwise we would have to handle
        # complex cases like B## + M3 = D###4
        if self.note.alteration in (
            NoteAlteration.DOUBLE_SHARP,
            NoteAlteration.DOUBLE_FLAT,
        ):
            raise ValueError("Cannot add intervals to notes with double accidentals.")

        # Find all possible notes that are a specific number of semitones away from this note
        feasible_notes = self.from_semitone_distance(interval.semitone_distance)

        # Only one of these notes will have the correct letter
        new_notes = [
            note
            for note in feasible_notes
            if note.letter - interval.letter_distance == self.letter
        ]
        assert len(new_notes) == 1, (
            "There should only be one correct note after adding an interval"
        )
        new_note = new_notes[0]

        return new_note

    def __str__(self) -> str:
        return f"{self.note}{self.octave}"

    @property
    def absolute_semitone_offset(self) -> int:
        """
        The absolute semitone offset of the note is the semitone offset from C0.
        """
        # absolute_semitone_offset = 12*self.octave + self.note.letter.semitone_offset + self.note.alteration.semitone_difference
        absolute_semitone_offset = 12 * self.octave + self.note.semitone_offset

        return absolute_semitone_offset

    def __int__(self) -> int:
        """
        The integer representation of the note is absolute semitone offset.
        """
        return self.absolute_semitone_offset

    def __repr__(self) -> str:
        return f"NoteInOctave({self.note}, {self.octave})"

    def __eq__(self, other: object) -> bool:
        """
        Comparison is forwarded to the absolute semitone offset.
        """
        assert isinstance(other, NoteInOctave), (
            "Cannot compare NoteInOctave with non-NoteInOctave object"
        )
        return self.absolute_semitone_offset == other.absolute_semitone_offset

    def __lt__(self, other: object) -> bool:
        """
        Comparison is forwarded to the absolute semitone offset.
        """
        assert isinstance(other, NoteInOctave), (
            "Cannot compare NoteInOctave with non-NoteInOctave object"
        )
        return self.absolute_semitone_offset < other.absolute_semitone_offset

    def __hash__(self) -> int:
        return hash((self.note, self.octave))

    @classmethod
    def from_str(cls, s: str) -> Self:
        """
        Converts a string to an octaved note by splitting the string into note and octave parts.

        Examples: NoteInOctave.from_str("C4"), NoteInOctave.from_str("D♯5"), NoteInOctave.from_str("B♭3")
        """
        note_str = s[:-1]
        octave_str = s[-1]
        note = Note.from_str(note_str)
        octave = int(octave_str)
        return cls(note, octave)

    # Forward some properties to the underlying note to avoid breaking law of demeter
    @property
    def letter(self) -> NoteLetter:
        return self.note.letter

    @property
    def alteration(self) -> NoteAlteration:
        return self.note.alteration


class Chord:
    """
    A Chord is a set of octaved notes.
    """

    def __init__(self, notes: set[NoteInOctave]):
        self.notes = notes

    def __iter__(self) -> Iterator[NoteInOctave]:
        return iter(self.notes)

    def __repr__(self) -> str:
        return f"Chord({{{','.join(str(note) for note in sorted(self.notes))}}})"

    def __str__(self) -> str:
        return f"{{{','.join(str(note) for note in sorted(self.notes))}}}"
