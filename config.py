"""
TeX's Mother-Chord - Configuration
TeXmExDeX Type Tunes
"""

# --- Application ---
APP_NAME = "TeX's Mother-Chord"
APP_VERSION = "1.0.0"
APP_TAGLINE = "TeXmExDeX Type Tunes"

# --- Default SoundFont ---
# Set this to your preferred SF2 filename
# Looks in: NEW BUILD/audio/, Backend/soundfonts/, and common locations
DEFAULT_SOUNDFONT = "Timbres Of Heaven GM_GS_XG_SFX V 3.4 Final.sf2"

# --- Audio Engines ---
SUPPORTED_ENGINES = ["SuperCollider", "Csound", "FluidSynth"]
DEFAULT_ENGINE = "SuperCollider"

# --- Audio Settings ---
DEFAULT_TEMPO = 120
DEFAULT_KEY = "C"
DEFAULT_TIME_SIG = "4/4"
SAMPLE_RATE = 44100
BIT_DEPTH = 16

# --- DSL Note Durations ---
# w=whole, h=half, q=quarter, e=eighth, s=sixteenth
DURATION_MAP = {
    'w': 4.0,    # whole note (4 beats)
    'h': 2.0,    # half note
    'dh': 3.0,   # dotted half
    'q': 1.0,    # quarter note
    'dq': 1.5,   # dotted quarter
    'e': 0.5,    # eighth note
    'de': 0.75,  # dotted eighth
    's': 0.25,   # sixteenth
    't': 0.333,  # triplet eighth
}

# --- DSL Dynamics ---
DYNAMICS_MAP = {
    'ppp': 0.15,
    'pp': 0.25,
    'p': 0.4,
    'mp': 0.55,
    'mf': 0.7,
    'f': 0.85,
    'ff': 0.95,
    'fff': 1.0,
}

# --- MIDI Note Mapping ---
NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

# --- Chord Definitions ---
CHORD_INTERVALS = {
    '': [0, 4, 7],           # Major
    'm': [0, 3, 7],          # Minor
    '7': [0, 4, 7, 10],      # Dominant 7
    'maj7': [0, 4, 7, 11],   # Major 7
    'm7': [0, 3, 7, 10],     # Minor 7
    'dim': [0, 3, 6],        # Diminished
    'dim7': [0, 3, 6, 9],    # Diminished 7
    'aug': [0, 4, 8],        # Augmented
    'sus2': [0, 2, 7],       # Suspended 2
    'sus4': [0, 5, 7],       # Suspended 4
    'add9': [0, 4, 7, 14],   # Add 9
    '9': [0, 4, 7, 10, 14],  # Dominant 9
}

# --- Instrument Presets (GM MIDI) ---
GM_INSTRUMENTS = {
    # Piano
    'piano': 0,
    'bright_piano': 1,
    'electric_piano': 4,
    'honkytonk': 3,
    
    # Chromatic Percussion
    'celesta': 8,
    'glockenspiel': 9,
    'music_box': 10,
    'vibraphone': 11,
    'marimba': 12,
    'xylophone': 13,
    
    # Organ
    'organ': 19,
    'church_organ': 19,
    'rock_organ': 18,
    
    # Guitar
    'acoustic_guitar': 24,
    'electric_guitar': 27,
    'clean_guitar': 27,
    'distortion_guitar': 30,
    
    # Bass
    'bass': 33,
    'acoustic_bass': 32,
    'electric_bass': 33,
    'slap_bass': 36,
    'synth_bass': 38,
    
    # Strings
    'strings': 48,
    'violin': 40,
    'viola': 41,
    'cello': 42,
    'contrabass': 43,
    'tremolo_strings': 44,
    'pizzicato': 45,
    'harp': 46,
    
    # Ensemble
    'string_ensemble': 48,
    'synth_strings': 50,
    'choir': 52,
    'voice': 54,
    
    # Brass
    'trumpet': 56,
    'trombone': 57,
    'tuba': 58,
    'french_horn': 60,
    'brass': 61,
    'synth_brass': 62,
    
    # Reed
    'saxophone': 65,
    'alto_sax': 65,
    'tenor_sax': 66,
    'oboe': 68,
    'clarinet': 71,
    
    # Pipe
    'flute': 73,
    'recorder': 74,
    'pan_flute': 75,
    
    # Synth Lead
    'lead': 80,
    'square_lead': 80,
    'saw_lead': 81,
    'synth_lead': 81,
    'synth': 81,
    
    # Synth Pad
    'pad': 88,
    'pads': 88,
    'new_age_pad': 88,
    'warm_pad': 89,
    'polysynth': 90,
    'space_pad': 91,
    'atmosphere': 99,
    'ambient': 88,
    
    # Sound Effects / Other
    'fx': 96,
    'rain': 96,
    'soundtrack': 97,
    'crystal': 98,
    
    # Common track name variations
    'guitar': 25,  # Acoustic guitar (steel)
    'gtr': 25,
    'keys': 0,  # Piano
    'keyboard': 0,
    'synths': 81,
    'vox': 54,  # Voice Oohs
    'vocals': 54,
    'horns': 61,  # Brass Section
    'woodwinds': 73,  # Flute
    'perc': 'drums',
    
    # Drums (Channel 10)
    'drums': 'drums',
    'percussion': 'drums',
    'drum': 'drums',
    'kit': 'drums',
}

# --- Drum Map (GM Standard) ---
DRUM_MAP = {
    'kick': 36,
    'bass': 36,
    'bd': 36,
    'snare': 38,
    'sd': 38,
    'rimshot': 37,
    'clap': 39,
    'hat': 42,
    'hh': 42,
    'closed_hat': 42,
    'open_hat': 46,
    'oh': 46,
    'tom_low': 45,
    'tom_mid': 47,
    'tom_high': 50,
    'crash': 49,
    'ride': 51,
    'china': 52,
    'bell': 53,
    'tambourine': 54,
    'cowbell': 56,
}

# --- UI Colors ---
UI_COLORS = {
    'bg_dark': '#1a1a1a',
    'bg_mid': '#252525',
    'bg_light': '#333333',
    'border': '#444444',
    'text': '#e0e0e0',
    'text_dim': '#888888',
    'accent': '#00aaff',
    'accent_hover': '#33bbff',
    'success': '#44cc44',
    'warning': '#ffaa00',
    'error': '#ff4444',
}

# --- Comment Markers (for AI response parsing) ---
# These are stripped/ignored when parsing AI responses
COMMENT_MARKERS = [
    '//',   # C-style
    '#',    # Python/Shell style
    '--',   # SQL/Lua style
    '/*',   # C block comment start
    '*/',   # C block comment end
    '*',    # Often used in block comments
    '"""',  # Python docstring
    "'''",  # Python docstring
]

# Lines starting with these are explanatory text, not code
EXPLANATION_PREFIXES = [
    'note:', 'note -', 'explanation:', 'here', 'this', 'the above',
    'i ', "i'", 'you ', 'we ', 'let me', 'as you can see',
    'in this', 'for example', 'notice', 'remember', 'important:',
]
