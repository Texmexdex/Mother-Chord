"""
DSL Parser - Parses AI-generated song descriptions into Song objects.
"""

import re
from typing import Optional
import sys
sys.path.append('..')

from models.song import Song, Section, InstrumentTrack, DrumTrack, Note, Chord, DrumHit
import config


class DSLParser:
    def __init__(self, debug=False):
        self.errors = []
        self.warnings = []
        self.debug = debug
    
    def log(self, msg):
        if self.debug:
            print(f"[PARSER] {msg}")
    
    def parse(self, text):
        self.errors = []
        self.warnings = []
        
        text = self.fix_one_line(text)
        self.log(f"Newlines after fix: {text.count(chr(10))}")
        
        cleaned = self.clean_input(text)
        self.log(f"Cleaned:\n{cleaned[:500]}...")
        
        if not cleaned.strip():
            self.errors.append("No DSL content found")
            return None
        
        song = Song()
        
        title_match = re.search(r'SONG:\s*(.+?)(?:\n|$)', cleaned, re.I)
        if title_match:
            song.title = title_match.group(1).strip()
        
        tempo_match = re.search(r'TEMPO:\s*(\d+)', cleaned, re.I)
        if tempo_match:
            song.tempo = int(tempo_match.group(1))
        
        key_match = re.search(r'KEY:\s*([A-Ga-g][#b]?m?)', cleaned, re.I)
        if key_match:
            song.key = key_match.group(1)
        
        sections = re.split(r'(?=SECTION:)', cleaned, flags=re.I)
        
        bar = 0
        for sec_text in sections:
            if 'SECTION:' in sec_text.upper():
                section = self.parse_section(sec_text, song.tempo, song.key)
                if section:
                    section.start_bar = bar
                    bar += section.bars
                    song.sections.append(section)
                    self.log(f"Section: {section.name}, {len(section.tracks)} tracks")
        
        return song
    
    def fix_one_line(self, text):
        if text.count('\n') < 5 and 'SECTION:' in text.upper():
            self.log("Fixing one-line format")
            for kw in ['SONG:', 'TEMPO:', 'KEY:', 'SECTION:']:
                text = re.sub(rf'(\s)({kw})', r'\n\2', text, flags=re.I)
            for inst in ['GUITAR', 'PIANO', 'BASS', 'DRUMS', 'STRINGS', 'PAD', 'LEAD', 'SYNTH', 'ORGAN', 'BRASS', 'CHOIR', 'FLUTE', 'VIOLIN', 'CELLO']:
                text = re.sub(rf'(\s)({inst}):', rf'\n  \2:', text, flags=re.I)
        return text
    
    def clean_input(self, text):
        lines = []
        for line in text.split('\n'):
            s = line.strip()
            if not s or s.startswith('```'):
                continue
            if s.startswith(('#', '//', '*')) and 'SECTION' not in s.upper():
                continue
            if '//' in s:
                s = s.split('//')[0].strip()
            if s:
                lines.append(s)
        return '\n'.join(lines)
    
    def parse_section(self, text, tempo, key):
        lines = text.strip().split('\n')
        if not lines:
            return None
        
        header = lines[0]
        name_m = re.search(r'SECTION:\s*(.+?)(?:\s*[\[\(]|$)', header, re.I)
        bars_m = re.search(r'(\d+)\s*bars?', header, re.I)
        
        name = name_m.group(1).strip() if name_m else "Section"
        bars = int(bars_m.group(1)) if bars_m else 8
        
        section = Section(name=name, bars=bars, key=key, tempo=tempo)
        
        for line in lines[1:]:
            s = line.strip()
            if not s:
                continue
            
            m = re.match(r'(\w+)\s*:\s*(.+)', s)
            if m:
                inst = m.group(1).upper()
                pattern = m.group(2)
                
                if inst == 'DRUMS':
                    section.drums = self.parse_drums(pattern, bars)
                else:
                    track = self.parse_track(inst, pattern, bars)
                    if track:
                        section.tracks.append(track)
        
        return section
    
    def parse_track(self, inst_name, pattern, bars):
        inst_lower = inst_name.lower()
        gm = config.GM_INSTRUMENTS.get(inst_lower, 'piano')
        if gm == 'drums':
            return None
        
        track = InstrumentTrack(name=inst_name.title(), instrument=inst_lower)
        
        bar_pats = pattern.split('|')
        beat = 0.0
        
        for bar_pat in bar_pats:
            bar_pat = bar_pat.strip()
            if not bar_pat or bar_pat == '_':
                beat += 4.0
                continue
            
            items = re.findall(r'([A-Ga-g][#b]?\w*)\s*\(([^)]+)\)', bar_pat)
            bar_start = beat
            bar_beat = 0.0
            
            for chord_note, params in items:
                dur, vel = self.parse_params(params)
                
                # Check if it's a note with octave (e.g., C4, G#3)
                note_m = re.match(r'^([A-Ga-g][#b]?)(\d)$', chord_note)
                if note_m:
                    n = note_m.group(1).upper()
                    o = int(note_m.group(2))
                    pitch = config.NOTE_TO_MIDI.get(n, 0) + (o + 1) * 12
                    track.notes.append(Note(pitch=pitch, start=bar_start+bar_beat, duration=dur, velocity=vel))
                else:
                    # It's a chord
                    root, qual, oct = self.parse_chord(chord_note)
                    track.chords.append(Chord(root=root, quality=qual, octave=oct, start=bar_start+bar_beat, duration=dur, velocity=vel))
                
                bar_beat += dur
            
            beat += 4.0
        
        return track
    
    def parse_drums(self, pattern, bars):
        drums = DrumTrack()
        bar_pats = pattern.split('|')
        
        for bar_idx, bar_pat in enumerate(bar_pats):
            bar_pat = bar_pat.strip()
            if not bar_pat or bar_pat == '_':
                continue
            
            bar_start = bar_idx * 4.0
            items = re.findall(r'(\w+)\s*\(([^)]+)\)', bar_pat)
            
            for drum, beats_str in items:
                drum = drum.lower()
                if beats_str in ('8ths', 'eighths'):
                    for i in range(8):
                        drums.hits.append(DrumHit(drum=drum, start=bar_start + i*0.5, velocity=0.7))
                elif beats_str in ('16ths', 'sixteenths'):
                    for i in range(16):
                        drums.hits.append(DrumHit(drum=drum, start=bar_start + i*0.25, velocity=0.6))
                else:
                    try:
                        for b in beats_str.split(','):
                            b = b.strip()
                            if b:
                                drums.hits.append(DrumHit(drum=drum, start=bar_start + float(b)-1, velocity=0.8))
                    except ValueError:
                        pass
        
        return drums
    
    def parse_params(self, params):
        dur, vel = 1.0, 0.7
        for p in params.split(','):
            p = p.strip().lower()
            if p in config.DURATION_MAP:
                dur = config.DURATION_MAP[p]
            elif p in config.DYNAMICS_MAP:
                vel = config.DYNAMICS_MAP[p]
        return dur, vel
    
    def parse_chord(self, chord):
        m = re.match(r'^([A-Ga-g][#b]?)(\w*)(\d)?$', chord)
        if m:
            root = m.group(1).upper()
            qual = m.group(2) or ''
            oct = int(m.group(3)) if m.group(3) else 4
            return root, qual, oct
        return 'C', '', 4


def parse_ai_response(text, debug=False):
    parser = DSLParser(debug=debug)
    song = parser.parse(text)
    return song, parser.errors, parser.warnings
