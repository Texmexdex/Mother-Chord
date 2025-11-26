"""
Song data models - Pure Python dataclasses for song structure.
"""

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class Note:
    """A single note."""
    pitch: int          # MIDI pitch (0-127)
    start: float        # Start time in beats
    duration: float     # Duration in beats
    velocity: float = 0.7  # 0.0-1.0


@dataclass
class DrumHit:
    """A single drum hit."""
    drum: str           # Drum name (kick, snare, hat, etc.)
    start: float        # Start time in beats
    velocity: float = 0.8


@dataclass
class Chord:
    """A chord with timing."""
    root: str           # Root note (C, D#, Bb, etc.)
    quality: str        # Chord quality (m, 7, maj7, etc.)
    octave: int         # Base octave
    start: float        # Start time in beats
    duration: float     # Duration in beats
    velocity: float = 0.7


@dataclass 
class InstrumentTrack:
    """A track for a single instrument."""
    name: str                           # Instrument name
    instrument: str                     # GM instrument name
    notes: list[Note] = field(default_factory=list)
    chords: list[Chord] = field(default_factory=list)
    volume: float = 0.8
    pan: float = 0.5                    # 0=left, 0.5=center, 1=right


@dataclass
class DrumTrack:
    """A drum track."""
    name: str = "Drums"
    hits: list[DrumHit] = field(default_factory=list)
    volume: float = 0.8


@dataclass
class Section:
    """A song section (intro, verse, chorus, etc.)."""
    name: str                           # Section name
    bars: int                           # Number of bars
    start_bar: int = 0                  # Starting bar in the song
    key: Optional[str] = None           # Key (if different from song)
    tempo: Optional[int] = None         # Tempo (if different from song)
    tracks: list[InstrumentTrack] = field(default_factory=list)
    drums: Optional[DrumTrack] = None
    
    @property
    def duration_beats(self) -> float:
        """Duration in beats (assumes 4/4)."""
        return self.bars * 4


@dataclass
class Song:
    """Complete song structure."""
    title: str = "Untitled"
    tempo: int = 120
    key: str = "C"
    time_signature: str = "4/4"
    sections: list[Section] = field(default_factory=list)
    
    @property
    def total_bars(self) -> int:
        return sum(s.bars for s in self.sections)
    
    @property
    def total_beats(self) -> float:
        return self.total_bars * 4  # Assumes 4/4
    
    @property
    def duration_seconds(self) -> float:
        return (self.total_beats / self.tempo) * 60
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'title': self.title,
            'tempo': self.tempo,
            'key': self.key,
            'time_signature': self.time_signature,
            'sections': [
                {
                    'name': s.name,
                    'bars': s.bars,
                    'start_bar': s.start_bar,
                    'key': s.key,
                    'tempo': s.tempo,
                    'tracks': [
                        {
                            'name': t.name,
                            'instrument': t.instrument,
                            'notes': [
                                {'pitch': n.pitch, 'start': n.start, 
                                 'duration': n.duration, 'velocity': n.velocity}
                                for n in t.notes
                            ],
                            'chords': [
                                {'root': c.root, 'quality': c.quality, 'octave': c.octave,
                                 'start': c.start, 'duration': c.duration, 'velocity': c.velocity}
                                for c in t.chords
                            ],
                            'volume': t.volume,
                            'pan': t.pan
                        }
                        for t in s.tracks
                    ],
                    'drums': {
                        'name': s.drums.name,
                        'hits': [
                            {'drum': h.drum, 'start': h.start, 'velocity': h.velocity}
                            for h in s.drums.hits
                        ],
                        'volume': s.drums.volume
                    } if s.drums else None
                }
                for s in self.sections
            ]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Song':
        """Create Song from dictionary."""
        song = cls(
            title=data.get('title', 'Untitled'),
            tempo=data.get('tempo', 120),
            key=data.get('key', 'C'),
            time_signature=data.get('time_signature', '4/4')
        )
        
        for s_data in data.get('sections', []):
            section = Section(
                name=s_data['name'],
                bars=s_data['bars'],
                start_bar=s_data.get('start_bar', 0),
                key=s_data.get('key'),
                tempo=s_data.get('tempo')
            )
            
            for t_data in s_data.get('tracks', []):
                track = InstrumentTrack(
                    name=t_data['name'],
                    instrument=t_data['instrument'],
                    volume=t_data.get('volume', 0.8),
                    pan=t_data.get('pan', 0.5)
                )
                for n_data in t_data.get('notes', []):
                    track.notes.append(Note(
                        pitch=n_data['pitch'],
                        start=n_data['start'],
                        duration=n_data['duration'],
                        velocity=n_data.get('velocity', 0.7)
                    ))
                for c_data in t_data.get('chords', []):
                    track.chords.append(Chord(
                        root=c_data['root'],
                        quality=c_data['quality'],
                        octave=c_data['octave'],
                        start=c_data['start'],
                        duration=c_data['duration'],
                        velocity=c_data.get('velocity', 0.7)
                    ))
                section.tracks.append(track)
            
            if s_data.get('drums'):
                d_data = s_data['drums']
                drums = DrumTrack(
                    name=d_data.get('name', 'Drums'),
                    volume=d_data.get('volume', 0.8)
                )
                for h_data in d_data.get('hits', []):
                    drums.hits.append(DrumHit(
                        drum=h_data['drum'],
                        start=h_data['start'],
                        velocity=h_data.get('velocity', 0.8)
                    ))
                section.drums = drums
            
            song.sections.append(section)
        
        return song
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Song':
        """Create Song from JSON string."""
        return cls.from_dict(json.loads(json_str))
