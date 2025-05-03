from pymusictheory import Chord, Interval, Note, NoteInOctave, NoteLetter


class TestNoteLetter:
    def test_addition(self) -> None:
        actual = [
            NoteLetter.C + 4,
            NoteLetter.E + 7,
            NoteLetter.A + 2,
        ]

        expected = [
            NoteLetter.G,
            NoteLetter.E,
            NoteLetter.C,
        ]

        assert actual == expected, f"Expected {expected}, but got {actual}"

    def test_subtraction(self) -> None:
        actual = [
            NoteLetter.C - 4,
            NoteLetter.E - 7,
            NoteLetter.A - 2,
        ]

        expected = [
            NoteLetter.F,
            NoteLetter.E,
            NoteLetter.F,
        ]

        assert actual == expected, f"Expected {expected}, but got {actual}"


class TestNote:
    def test_semitone_offset(self) -> None:
        assert Note.from_str("C").semitone_offset == 0
        assert Note.from_str("C#").semitone_offset == 1
        assert Note.from_str("C##").semitone_offset == 2
        assert Note.from_str("Cb").semitone_offset == -1
        assert Note.from_str("Cbb").semitone_offset == -2
        assert Note.from_str("Eb").semitone_offset == 3
        assert Note.from_str("F#").semitone_offset == 6
        assert Note.from_str("B#").semitone_offset == 12
        assert Note.from_str("B##").semitone_offset == 13

    def test_from_semitone_offset(self) -> None:
        assert Note.from_semitone_offset(0) == {
            Note.from_str("C"),
            Note.from_str("Dbb"),
        }
        assert Note.from_semitone_offset(-1) == {Note.from_str("Cb")}
        assert Note.from_semitone_offset(-2) == {Note.from_str("Cbb")}
        assert Note.from_semitone_offset(1) == {
            Note.from_str("C#"),
            Note.from_str("Db"),
        }
        assert Note.from_semitone_offset(7) == {
            Note.from_str("G"),
            Note.from_str("F##"),
            Note.from_str("Abb"),
        }
        assert Note.from_semitone_offset(8) == {
            Note.from_str("G#"),
            Note.from_str("Ab"),
        }
        assert Note.from_semitone_offset(11) == {
            Note.from_str("B"),
            Note.from_str("A##"),
        }
        assert Note.from_semitone_offset(12) == {Note.from_str("B#")}
        assert Note.from_semitone_offset(13) == {Note.from_str("B##")}

    def test_eq(self) -> None:
        # Should be equal
        assert Note.from_str("C") == Note.from_str("C")
        assert Note.from_str("Cb") == Note.from_str("Cb")
        assert Note.from_str("G#") == Note.from_str("G#")
        # Should not be equal
        assert Note.from_str("C") != Note.from_str("D")
        assert Note.from_str("Cb") != Note.from_str("B#")
        assert Note.from_str("G#") != Note.from_str("Ab")
        assert Note.from_str("A##") != Note.from_str("B")
        assert Note.from_str("Bbb") != Note.from_str("A")


class TestNoteInOctave:
    def test_eq(self) -> None:
        # Should be equal
        assert NoteInOctave.from_str("C4") == NoteInOctave.from_str("C4")
        assert NoteInOctave.from_str("Cb4") == NoteInOctave.from_str("B3")
        assert NoteInOctave.from_str("C4") == NoteInOctave.from_str("B#3")
        assert NoteInOctave.from_str("E#4") == NoteInOctave.from_str("F4")
        assert NoteInOctave.from_str("G#4") == NoteInOctave.from_str("Ab4")
        # Should not be equal
        assert NoteInOctave.from_str("C4") != NoteInOctave.from_str("D4")
        assert NoteInOctave.from_str("C4") != NoteInOctave.from_str("Cb5")

    def test_absolute_semitone_offset(self) -> None:
        assert NoteInOctave.from_str("C1").absolute_semitone_offset == 12
        assert NoteInOctave.from_str("C2").absolute_semitone_offset == 24
        assert NoteInOctave.from_str("Cb2").absolute_semitone_offset == 23
        assert NoteInOctave.from_str("B#1").absolute_semitone_offset == 24
        assert NoteInOctave.from_str("G#2").absolute_semitone_offset == 32

    def test_from_absolute_semitone_offset(self) -> None:
        assert NoteInOctave.from_absolute_semitone_offset(28) == set(
            [
                NoteInOctave.from_str("E2"),
                NoteInOctave.from_str("Fb2"),
                NoteInOctave.from_str("D##2"),
            ]
        )
        assert NoteInOctave.from_absolute_semitone_offset(31) == set(
            [
                NoteInOctave.from_str("G2"),
                NoteInOctave.from_str("F##2"),
                NoteInOctave.from_str("Abb2"),
            ]
        )
        assert NoteInOctave.from_absolute_semitone_offset(32) == set(
            [
                NoteInOctave.from_str("G#2"),
                NoteInOctave.from_str("Ab2"),
            ]
        )
        # Four edge cases
        assert NoteInOctave.from_absolute_semitone_offset(12) == set(
            [
                NoteInOctave.from_str("C1"),
                NoteInOctave.from_str("B#0"),
                NoteInOctave.from_str("Dbb1"),
            ]
        )
        assert NoteInOctave.from_absolute_semitone_offset(13) == set(
            [
                NoteInOctave.from_str("C#1"),
                NoteInOctave.from_str("B##0"),
                NoteInOctave.from_str("Db1"),
            ]
        )
        assert NoteInOctave.from_absolute_semitone_offset(11) == set(
            [
                NoteInOctave.from_str("Cb1"),
                NoteInOctave.from_str("B0"),
                NoteInOctave.from_str("A##0"),
            ]
        )
        assert NoteInOctave.from_absolute_semitone_offset(10) == set(
            [
                NoteInOctave.from_str("Cbb1"),
                NoteInOctave.from_str("Bb0"),
                NoteInOctave.from_str("A#0"),
            ]
        )

    def test_from_semitone_distance(self) -> None:
        actual = NoteInOctave.from_str("C4").from_semitone_distance(0)
        expected = {
            NoteInOctave.from_str("C4"),
            NoteInOctave.from_str("B#3"),
            NoteInOctave.from_str("Dbb4"),
        }
        assert actual == expected

        actual = NoteInOctave.from_str("Cb4").from_semitone_distance(0)
        expected = {
            NoteInOctave.from_str("Cb4"),
            NoteInOctave.from_str("B3"),
            NoteInOctave.from_str("A##3"),
        }
        assert actual == expected

        actual = NoteInOctave.from_str("B#4").from_semitone_distance(0)
        expected = {
            NoteInOctave.from_str("B#4"),
            NoteInOctave.from_str("C5"),
            NoteInOctave.from_str("Dbb5"),
        }
        assert actual == expected

        actual = NoteInOctave.from_str("G4").from_semitone_distance(5)
        expected = {
            NoteInOctave.from_str("C5"),
            NoteInOctave.from_str("B#4"),
            NoteInOctave.from_str("Dbb5"),
        }
        assert actual == expected

        actual = NoteInOctave.from_str("A3").from_semitone_distance(5)
        expected = {
            NoteInOctave.from_str("D4"),
            NoteInOctave.from_str("C##4"),
            NoteInOctave.from_str("Ebb4"),
        }
        assert actual == expected

        actual = NoteInOctave.from_str("A3").from_semitone_distance(6)
        expected = {
            NoteInOctave.from_str("D#4"),
            NoteInOctave.from_str("Eb4"),
            NoteInOctave.from_str("Fbb4"),
        }
        assert actual == expected

    def test_add_interval(self) -> None:
        """
        Test that adding intervals works as expected.

        Tested so far (in octave 4):
        - PERFECT_UNISON
        - MINOR_THIRD
        - MAJOR_THIRD
        - PERFECT_FIFTH
        - PERFECT_OCTAVE

        Not yet tested:
        - MINOR_SECOND
        - MAJOR_SECOND
        - PERFECT_FOURTH
        - MINOR_SIXTH
        - MAJOR_SIXTH
        - MINOR_SEVENTH
        - MAJOR_SEVENTH

        Also tested a perfect fifth with a different octave.
        """

        # Random perfect unisons
        assert NoteInOctave.from_str(
            "C4"
        ) + Interval.PERFECT_UNISON == NoteInOctave.from_str("C4")
        assert NoteInOctave.from_str(
            "C#4"
        ) + Interval.PERFECT_UNISON == NoteInOctave.from_str("C#4")
        assert NoteInOctave.from_str(
            "D4"
        ) + Interval.PERFECT_UNISON == NoteInOctave.from_str("D4")

        # Random minor thirds
        assert NoteInOctave.from_str(
            "C4"
        ) + Interval.MINOR_THIRD == NoteInOctave.from_str("Eb4")
        assert NoteInOctave.from_str(
            "C#4"
        ) + Interval.MINOR_THIRD == NoteInOctave.from_str("E4")
        assert NoteInOctave.from_str(
            "D4"
        ) + Interval.MINOR_THIRD == NoteInOctave.from_str("F4")

        # There are no minor thirds resulting in double sharps, if we only consider starting notes with single accidentals

        # Minor thirds resulting in double flats
        assert NoteInOctave.from_str(
            "Fb4"
        ) + Interval.MINOR_THIRD == NoteInOctave.from_str("Abb4")
        assert NoteInOctave.from_str(
            "Cb4"
        ) + Interval.MINOR_THIRD == NoteInOctave.from_str("Ebb4")

        # Random major thirds
        assert NoteInOctave.from_str(
            "C4"
        ) + Interval.MAJOR_THIRD == NoteInOctave.from_str("E4")
        assert NoteInOctave.from_str(
            "C#4"
        ) + Interval.MAJOR_THIRD == NoteInOctave.from_str("E#4")
        assert NoteInOctave.from_str(
            "D4"
        ) + Interval.MAJOR_THIRD == NoteInOctave.from_str("F#4")

        # Major thirds resulting in double sharps
        assert NoteInOctave.from_str(
            "B#4"
        ) + Interval.MAJOR_THIRD == NoteInOctave.from_str("D##5")
        assert NoteInOctave.from_str(
            "D#4"
        ) + Interval.MAJOR_THIRD == NoteInOctave.from_str("F##4")
        assert NoteInOctave.from_str(
            "E#4"
        ) + Interval.MAJOR_THIRD == NoteInOctave.from_str("G##4")
        assert NoteInOctave.from_str(
            "A#4"
        ) + Interval.MAJOR_THIRD == NoteInOctave.from_str("C##5")

        # There are no major thirds resulting in double flats, if we only consider starting notes with single accidentals

        # Random perfect fifths
        assert NoteInOctave.from_str(
            "C4"
        ) + Interval.PERFECT_FIFTH == NoteInOctave.from_str("G4")
        assert NoteInOctave.from_str(
            "C#4"
        ) + Interval.PERFECT_FIFTH == NoteInOctave.from_str("G#4")
        assert NoteInOctave.from_str(
            "D4"
        ) + Interval.PERFECT_FIFTH == NoteInOctave.from_str("A4")

        # Random perfect unisons
        assert NoteInOctave.from_str(
            "C4"
        ) + Interval.PERFECT_OCTAVE == NoteInOctave.from_str("C5")
        assert NoteInOctave.from_str(
            "C#4"
        ) + Interval.PERFECT_OCTAVE == NoteInOctave.from_str("C#5")
        assert NoteInOctave.from_str(
            "D4"
        ) + Interval.PERFECT_OCTAVE == NoteInOctave.from_str("D5")

        # Perfect fifths in different octaves
        assert NoteInOctave.from_str(
            "G4"
        ) + Interval.PERFECT_FIFTH == NoteInOctave.from_str("D5")
        assert NoteInOctave.from_str(
            "G#4"
        ) + Interval.PERFECT_FIFTH == NoteInOctave.from_str("D#5")
        assert NoteInOctave.from_str(
            "Ab4"
        ) + Interval.PERFECT_FIFTH == NoteInOctave.from_str("Eb5")

        # Perfect fifths with double sharps
        assert NoteInOctave.from_str(
            "B#4"
        ) + Interval.PERFECT_FIFTH == NoteInOctave.from_str("F##5")
        assert NoteInOctave.from_str(
            "E#4"
        ) + Interval.PERFECT_FIFTH == NoteInOctave.from_str("B#4")

        # There are no perfect fifths resulting in double flats, if we only consider starting notes with single accidentals

        # We expect an error if we try to add an interval to a note that already has a double accidental
        # This would necessitate handling of complex cases like B## + M3 = D### which are
        # never used in practice

        # Assert that code should raise an error
        try:
            NoteInOctave.from_str("B##4") + Interval.MAJOR_THIRD
        except ValueError as e:
            assert str(e) == "Cannot add intervals to notes with double accidentals."
        else:
            assert False, "Expected ValueError, but no error was raised"


class TestChord:
    def test_repr(self) -> None:
        # Test the representation of a chord. It should be sorted
        chord = Chord(
            {
                NoteInOctave.from_str("C4"),
                NoteInOctave.from_str("G4"),
                NoteInOctave.from_str("E4"),
            }
        )
        assert repr(chord) == r"Chord({C4,E4,G4})"

    def test_str(self) -> None:
        # Test the string representation of a chord. It should be sorted
        chord = Chord(
            {
                NoteInOctave.from_str("C4"),
                NoteInOctave.from_str("G4"),
                NoteInOctave.from_str("E4"),
            }
        )
        assert str(chord) == r"{C4,E4,G4}"
