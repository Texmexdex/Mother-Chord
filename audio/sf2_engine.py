"""
SF2 Audio Engine - SoundFont-based playback with per-track SF2 loading.
Uses FluidSynth for high-quality audio synthesis.
"""

import threading
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field

try:
    import fluidsynth
    FLUIDSYNTH_AVAILABLE = True
except ImportError:
    FLUIDSYNTH_AVAILABLE = False
    print("[SF2 ENGINE] pyfluidsynth not installed. Run: pip install pyfluidsynth")

import sys
sys.path.append('..')

from models.song import Song
import config


@dataclass
class TrackConfig:
    """Configuration for a single track."""
    name: str
    channel: int
    soundfont_path: Optional[str] = None
    soundfont_id: Optional[int] = None
    bank: int = 0
    preset: int = 0
    volume: float = 1.0
    pan: float = 0.5  # 0=left, 0.5=center, 1=right


class SF2Engine:
    """SoundFont-based audio engine with per-track SF2 support."""
    
    def __init__(self):
        self.fs = None
        self.is_initialized = False
        self.is_playing = False
        self.is_paused = False
        
        self.tracks: Dict[str, TrackConfig] = {}
        self.loaded_soundfonts: Dict[str, int] = {}  # path -> sfid
        
        self.current_song: Optional[Song] = None
        self.play_thread: Optional[threading.Thread] = None
        self.start_time: float = 0
        self.pause_time: float = 0
        
        self._init_fluidsynth()
    
    def _init_fluidsynth(self):
        """Initialize FluidSynth."""
        if not FLUIDSYNTH_AVAILABLE:
            print("[SF2 ENGINE] FluidSynth not available")
            return
        
        try:
            self.fs = fluidsynth.Synth(gain=0.6)  # Moderate gain to prevent clipping
            self.fs.start(driver="dsound")  # Windows DirectSound
            
            self.is_initialized = True
            self.default_sfid = None
            
            # Try to load a default SoundFont
            self._load_default_soundfont()
            
            print("[SF2 ENGINE] FluidSynth initialized")
        except Exception as e:
            print(f"[SF2 ENGINE] Failed to initialize: {e}")
            self.fs = None
    
    def _load_default_soundfont(self):
        """Try to load a default GM SoundFont."""
        import os
        
        # Common locations for SoundFonts
        sf2_paths = [
            # Check in audio folder (where this file is)
            os.path.dirname(__file__),
            # Check in Backend/soundfonts folder (relative to workspace)
            os.path.join(os.path.dirname(__file__), '..', '..', 'Backend', 'soundfonts'),
            # Check in NEW BUILD root
            os.path.join(os.path.dirname(__file__), '..'),
            # Check in soundfonts subfolder
            os.path.join(os.path.dirname(__file__), 'soundfonts'),
            # Windows common locations
            'C:/soundfonts',
            os.path.expanduser('~/soundfonts'),
        ]
        
        # First try the configured default from config.py
        configured_default = getattr(config, 'DEFAULT_SOUNDFONT', '')
        
        # Fallback preferred SoundFonts (good quality GM)
        preferred = [configured_default] if configured_default else []
        preferred.extend([
            'GeneralUser GS v1.471.sf2',
            'FluidR3_GM2-2.SF2', 
            'TimGM6mb.sf2',
            'SGM-V2.01.sf2',
            'Arachno_SoundFont_Version_1.0.sf2',
        ])
        
        for sf_dir in sf2_paths:
            if not os.path.isdir(sf_dir):
                continue
            
            # First try preferred fonts
            for pref in preferred:
                if not pref:
                    continue
                path = os.path.join(sf_dir, pref)
                if os.path.exists(path):
                    try:
                        self.default_sfid = self.fs.sfload(path)
                        self.default_sf_path = path
                        print(f"[SF2 ENGINE] Loaded default SF2: {pref}")
                        return
                    except Exception as e:
                        print(f"[SF2 ENGINE] Failed to load {pref}: {e}")
            
            # Otherwise load any .sf2 file
            for f in os.listdir(sf_dir):
                if f.lower().endswith('.sf2'):
                    path = os.path.join(sf_dir, f)
                    try:
                        self.default_sfid = self.fs.sfload(path)
                        self.default_sf_path = path
                        print(f"[SF2 ENGINE] Loaded default SF2: {f}")
                        return
                    except:
                        pass
        
        print("[SF2 ENGINE] WARNING: No default SoundFont found - audio may not work")
        print("[SF2 ENGINE] Set DEFAULT_SOUNDFONT in config.py or place SF2 files in Backend/soundfonts/")
    
    def is_available(self) -> bool:
        """Check if engine is available."""
        return self.is_initialized and self.fs is not None
    
    def load_soundfont(self, path: str) -> Optional[int]:
        """Load a SoundFont file. Returns soundfont ID or None."""
        if not self.is_available():
            return None
        
        if path in self.loaded_soundfonts:
            return self.loaded_soundfonts[path]
        
        try:
            sfid = self.fs.sfload(path)
            self.loaded_soundfonts[path] = sfid
            print(f"[SF2 ENGINE] Loaded: {path} (ID: {sfid})")
            return sfid
        except Exception as e:
            print(f"[SF2 ENGINE] Failed to load {path}: {e}")
            return None
    
    def setup_track(self, name: str, channel: int, soundfont_path: Optional[str] = None,
                    bank: int = 0, preset: int = 0, volume: float = 1.0):
        """Configure a track with optional SoundFont."""
        track = TrackConfig(
            name=name,
            channel=channel,
            soundfont_path=soundfont_path,
            bank=bank,
            preset=preset,
            volume=volume
        )
        
        if soundfont_path and self.is_available():
            sfid = self.load_soundfont(soundfont_path)
            if sfid is not None:
                track.soundfont_id = sfid
                self.fs.program_select(channel, sfid, bank, preset)
        
        self.tracks[name] = track
        
        # Set volume (CC 7)
        if self.is_available():
            self.fs.cc(channel, 7, int(volume * 127))
    
    def set_track_preset(self, track_name: str, bank: int, preset: int):
        """Change the preset for a track."""
        if track_name not in self.tracks:
            return
        
        track = self.tracks[track_name]
        track.bank = bank
        track.preset = preset
        
        if self.is_available() and track.soundfont_id is not None:
            self.fs.program_select(track.channel, track.soundfont_id, bank, preset)
    
    def set_track_volume(self, track_name: str, volume: float):
        """Set volume for a track (0.0 - 1.0)."""
        if track_name not in self.tracks:
            return
        
        track = self.tracks[track_name]
        track.volume = volume
        
        if self.is_available():
            self.fs.cc(track.channel, 7, int(volume * 127))
    
    def note_on(self, channel: int, note: int, velocity: int):
        """Play a note."""
        if self.is_available():
            self.fs.noteon(channel, note, velocity)
    
    def note_off(self, channel: int, note: int):
        """Stop a note."""
        if self.is_available():
            self.fs.noteoff(channel, note)
    
    def all_notes_off(self):
        """Stop all notes on all channels."""
        if self.is_available():
            for ch in range(16):
                self.fs.cc(ch, 123, 0)  # All notes off
    
    def load_song(self, song: Song):
        """Load a song and auto-configure tracks."""
        self.stop()
        self.current_song = song
        self.tracks.clear()
        
        if not self.is_available():
            return
        
        # Collect unique tracks
        channel = 0
        for section in song.sections:
            for track in section.tracks:
                if track.name not in self.tracks:
                    # Assign channel (skip 9 for drums)
                    if channel == 9:
                        channel = 10
                    
                    self.setup_track(
                        name=track.name,
                        channel=channel,
                        volume=1.0  # Full volume
                    )
                    
                    # Set GM instrument using default soundfont
                    program = config.GM_INSTRUMENTS.get(track.instrument.lower(), 0)
                    if isinstance(program, int):
                        if self.default_sfid is not None:
                            self.fs.program_select(channel, self.default_sfid, 0, program)
                        else:
                            self.fs.program_change(channel, program)
                    
                    # Set channel volume (not maxed to prevent clipping)
                    self.fs.cc(channel, 7, 100)  # CC7 = volume
                    self.fs.cc(channel, 11, 100)  # CC11 = expression
                    
                    channel += 1
        
        # Setup drums on channel 9 (channel 10 in MIDI terms)
        for section in song.sections:
            if section.drums and "Drums" not in self.tracks:
                self.setup_track(name="Drums", channel=9, volume=0.8)
                
                # Drums use bank 128 (percussion) in GM, program 0 = Standard Kit
                if self.default_sfid is not None:
                    # Try bank 128 first (standard GM percussion)
                    try:
                        self.fs.program_select(9, self.default_sfid, 128, 0)
                    except:
                        # Some soundfonts use bank 0 for drums on channel 10
                        try:
                            self.fs.program_select(9, self.default_sfid, 0, 0)
                        except:
                            pass
                
                self.fs.cc(9, 7, 100)  # Drum volume
                self.fs.cc(9, 11, 100)  # Drum expression
                break
    
    def play(self):
        """Start or resume playback."""
        if not self.is_available() or not self.current_song:
            return False
        
        if self.is_paused:
            pause_duration = time.time() - self.pause_time
            self.start_time += pause_duration
            self.is_paused = False
            self.is_playing = True
            return True
        
        if self.is_playing:
            return True
        
        self.is_playing = True
        self.is_paused = False
        self.start_time = time.time()
        
        self.play_thread = threading.Thread(target=self._play_song, daemon=True)
        self.play_thread.start()
        return True
    
    def pause(self):
        """Pause playback."""
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            self.pause_time = time.time()
            self.all_notes_off()
    
    def stop(self):
        """Stop playback."""
        self.is_playing = False
        self.is_paused = False
        self.all_notes_off()
        
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)
    
    def _play_song(self):
        """Play the loaded song (runs in separate thread)."""
        if not self.current_song or not self.is_available():
            return
        
        events = self._song_to_events()
        events.sort(key=lambda x: x['time'])
        
        start_time = time.time()
        event_index = 0
        
        while self.is_playing and event_index < len(events):
            if self.is_paused:
                time.sleep(0.05)
                continue
            
            current_time = time.time() - start_time
            
            while event_index < len(events) and events[event_index]['time'] <= current_time:
                event = events[event_index]
                
                if event['type'] == 'note_on':
                    self.note_on(event['channel'], event['note'], event['velocity'])
                elif event['type'] == 'note_off':
                    self.note_off(event['channel'], event['note'])
                
                event_index += 1
            
            time.sleep(0.005)  # 5ms resolution
        
        self.is_playing = False
        self.all_notes_off()
    
    def _song_to_events(self) -> List[dict]:
        """Convert song to timed events."""
        events = []
        song = self.current_song
        bps = song.tempo / 60.0  # beats per second
        
        for section in song.sections:
            section_start = (section.start_bar * 4) / bps
            
            # Process instrument tracks
            for track in section.tracks:
                if track.name not in self.tracks:
                    continue
                
                channel = self.tracks[track.name].channel
                
                # Notes
                for note in track.notes:
                    start = section_start + (note.start / bps)
                    end = start + (note.duration / bps)
                    vel = int(note.velocity * 127)
                    
                    events.append({'time': start, 'type': 'note_on', 
                                   'channel': channel, 'note': note.pitch, 'velocity': vel})
                    events.append({'time': end, 'type': 'note_off',
                                   'channel': channel, 'note': note.pitch})
                
                # Chords
                for chord in track.chords:
                    start = section_start + (chord.start / bps)
                    end = start + (chord.duration / bps)
                    vel = int(chord.velocity * 127)
                    
                    # Get chord notes
                    quality = chord.quality.lower() if chord.quality else ''
                    intervals = config.CHORD_INTERVALS.get(quality, [0, 4, 7])
                    root = config.NOTE_TO_MIDI.get(chord.root.upper(), 0) + (chord.octave + 1) * 12
                    
                    for interval in intervals:
                        pitch = root + interval
                        events.append({'time': start, 'type': 'note_on',
                                       'channel': channel, 'note': pitch, 'velocity': vel})
                        events.append({'time': end, 'type': 'note_off',
                                       'channel': channel, 'note': pitch})
            
            # Drums
            if section.drums:
                for hit in section.drums.hits:
                    start = section_start + (hit.start / bps)
                    vel = int(hit.velocity * 127)
                    midi_note = config.DRUM_MAP.get(hit.drum.lower(), 36)
                    
                    events.append({'time': start, 'type': 'note_on',
                                   'channel': 9, 'note': midi_note, 'velocity': vel})
                    events.append({'time': start + 0.1, 'type': 'note_off',
                                   'channel': 9, 'note': midi_note})
        
        return events
    
    def get_position(self) -> float:
        """Get current playback position in seconds."""
        if not self.is_playing and not self.is_paused:
            return 0.0
        if self.is_paused:
            return self.pause_time - self.start_time
        return time.time() - self.start_time
    
    def get_duration(self) -> float:
        """Get song duration in seconds."""
        if not self.current_song:
            return 0.0
        return self.current_song.duration_seconds
    
    def cleanup(self):
        """Clean up resources."""
        self.stop()
        if self.fs:
            self.fs.delete()
            self.fs = None
