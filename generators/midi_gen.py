"""
MIDI Generator - Converts Song objects to MIDI files.
"""

from midiutil import MIDIFile
import sys
sys.path.append('..')

from models.song import Song, Section, InstrumentTrack, DrumTrack, Note, Chord
import config


class MIDIGenerator:
    """Generates MIDI files from Song objects."""
    
    def __init__(self):
        self.midi = None
        self.track_count = 0
    
    def generate(self, song: Song) -> MIDIFile:
        """Generate a MIDI file from a Song object."""
        
        # Safety check
        if not song or not song.sections:
            raise ValueError("Song has no sections to generate")
        
        # Count unique tracks across all sections
        all_track_names = set()
        has_drums = False
        for section in song.sections:
            for track in section.tracks:
                all_track_names.add(track.name)
            if section.drums and section.drums.hits:
                has_drums = True
        
        # Calculate total tracks needed
        track_count = max(1, len(all_track_names) + (1 if has_drums else 0))
        
        self.midi = MIDIFile(track_count + 1)  # +1 for tempo track
        self.track_count = track_count
        
        # Set tempo on track 0
        self.midi.addTempo(0, 0, song.tempo)
        
        # Track assignments
        track_assignments = {}  # instrument_name -> track_number
        current_track = 1
        
        # Pre-assign all tracks and set track names
        track_instruments = {}  # track_num -> instrument name for naming
        for name in sorted(all_track_names):
            track_assignments[name] = current_track
            current_track += 1
        
        # Drum track is always last
        drum_track_num = current_track if has_drums else None
        
        # Set track names (need to find instrument for each track)
        for section in song.sections:
            for inst_track in section.tracks:
                if inst_track.name in track_assignments:
                    track_num = track_assignments[inst_track.name]
                    if track_num not in track_instruments:
                        # Create descriptive track name
                        track_instruments[track_num] = inst_track.name
        
        # Add track names to MIDI
        for track_num, track_name in track_instruments.items():
            self.midi.addTrackName(track_num, 0, track_name)
        
        # Add drum track name
        if drum_track_num:
            self.midi.addTrackName(drum_track_num, 0, "Drums")
        
        # Process each section
        for section in song.sections:
            section_start = section.start_bar * 4  # Convert bars to beats
            
            # Process instrument tracks
            for inst_track in section.tracks:
                if inst_track.name not in track_assignments:
                    continue  # Skip if somehow not assigned
                
                track_num = track_assignments[inst_track.name]
                channel = min(track_num - 1, 15)  # Clamp channel to 0-15
                if channel == 9:  # Skip drum channel for melodic instruments
                    channel = 10
                
                # Set instrument
                program = config.GM_INSTRUMENTS.get(inst_track.instrument.lower(), 0)
                if isinstance(program, int):
                    self.midi.addProgramChange(track_num, channel, 0, program)
                
                # Add notes
                for note in inst_track.notes:
                    self._add_note(
                        track_num,
                        channel,
                        note.pitch,
                        section_start + note.start,
                        note.duration,
                        int(note.velocity * 127)
                    )
                
                # Add chords
                for chord in inst_track.chords:
                    self._add_chord(
                        track_num,
                        channel,
                        chord,
                        section_start + chord.start
                    )
            
            # Process drums
            if section.drums and section.drums.hits and drum_track_num:
                for hit in section.drums.hits:
                    midi_note = config.DRUM_MAP.get(hit.drum.lower(), 36)
                    self._add_note(
                        drum_track_num,
                        9,  # Channel 10 (0-indexed = 9) for drums
                        midi_note,
                        section_start + hit.start,
                        0.25,  # Short duration for drums
                        int(hit.velocity * 127)
                    )
        
        return self.midi
    
    def _add_note(self, track: int, channel: int, pitch: int, start: float, 
                  duration: float, velocity: int):
        """Add a single note to the MIDI file."""
        # Clamp values
        pitch = max(0, min(127, pitch))
        velocity = max(1, min(127, velocity))
        duration = max(0.1, duration)
        
        self.midi.addNote(track, channel, pitch, start, duration, velocity)
    
    def _add_chord(self, track: int, channel: int, chord: Chord, start: float):
        """Add a chord to the MIDI file."""
        # Normalize quality for lookup
        quality = chord.quality.lower() if chord.quality else ''
        
        # Try direct lookup first
        intervals = config.CHORD_INTERVALS.get(quality)
        
        # If not found, try to match patterns
        if intervals is None:
            if 'maj7' in quality or quality.startswith('maj7'):
                intervals = [0, 4, 7, 11]
            elif 'maj' in quality:
                intervals = [0, 4, 7]
            elif 'm7' in quality or 'min7' in quality:
                intervals = [0, 3, 7, 10]
            elif quality.startswith('m') or 'min' in quality:
                intervals = [0, 3, 7]
            elif 'sus4' in quality:
                intervals = [0, 5, 7]
            elif 'sus2' in quality:
                intervals = [0, 2, 7]
            elif 'dim7' in quality:
                intervals = [0, 3, 6, 9]
            elif 'dim' in quality:
                intervals = [0, 3, 6]
            elif 'aug' in quality:
                intervals = [0, 4, 8]
            elif '7' in quality:
                intervals = [0, 4, 7, 10]
            else:
                intervals = [0, 4, 7]  # Default to major
        
        # Calculate root MIDI note
        root_note = config.NOTE_TO_MIDI.get(chord.root.upper(), 0)
        root_midi = root_note + (chord.octave + 1) * 12
        
        # Add each note in the chord
        velocity = int(chord.velocity * 127)
        for interval in intervals:
            pitch = root_midi + interval
            self._add_note(track, channel, pitch, start, chord.duration, velocity)
    
    def save(self, filepath: str):
        """Save the MIDI file to disk."""
        if self.midi is None:
            raise ValueError("No MIDI data generated. Call generate() first.")
        
        with open(filepath, 'wb') as f:
            self.midi.writeFile(f)


def song_to_midi(song: Song, filepath: str) -> bool:
    """
    Convenience function to convert a Song to MIDI file.
    Returns True on success.
    """
    try:
        generator = MIDIGenerator()
        generator.generate(song)
        generator.save(filepath)
        return True
    except Exception as e:
        import traceback
        print(f"Error generating MIDI: {e}")
        traceback.print_exc()
        return False
