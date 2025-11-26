# TeX's Mother-Chord

**TeXmExDeX Type Tunes**

An AI-to-MIDI bridge tool that transforms natural language song descriptions into playable MIDI files. Describe your music, let AI generate the structure, and export production-ready MIDI for your DAW.

## What It Does

1. **Describe** your song in plain English (mood, tempo, style, instruments)
2. **Generate** a structured prompt with music theory parameters
3. **Paste** the AI's response (from ChatGPT, Claude, Gemini, etc.)
4. **Preview** with built-in SoundFont playback
5. **Export** to MIDI with proper instrument assignments and track names

## Features

- **Smart DSL Parser** - Handles AI responses even when formatting is messy
- **Music Theory Helper** - Quick reference for chord progressions, song structures, tempo guides
- **Per-Track SoundFont Selection** - Load different SF2 files for each instrument
- **Auto Instrument Mapping** - Automatically assigns GM programs based on track names
- **Live Preview** - FluidSynth-powered playback before export
- **Detailed Parse Stats** - See exactly what was parsed per section

## Installation

### Requirements
- Python 3.10+
- Windows (batch scripts included, but Python code is cross-platform)

### Setup

```bash
# Clone the repo
git clone https://github.com/Texmexdex/Mother-Chord.git
cd Mother-Chord

# Run setup (creates venv and installs dependencies)
setup.bat

# Launch the app
run.bat
```

### Dependencies
- PyQt6 - GUI framework
- midiutil - MIDI file generation
- pyfluidsynth - Audio preview (requires FluidSynth)
- sf2utils - SoundFont preset reading

### SoundFont Setup

For audio preview, place a GM-compatible SoundFont (.sf2) in the `audio/` folder.

Recommended free SoundFonts:
- [Timbres of Heaven](https://midkar.com/soundfonts/) - High quality GM/GS/XG
- [GeneralUser GS](https://schristiancollins.com/generaluser.php) - Lightweight and clean
- [FluidR3 GM](https://member.keymusician.com/Member/FluidR3_GM/) - Classic choice

Set your preferred default in `config.py`:
```python
DEFAULT_SOUNDFONT = "Your_Soundfont.sf2"
```

## Usage

### 1. Describe Your Song

Enter a description like:
> "Epic orchestral piece with building tension, starts quiet with strings, builds to a powerful brass climax"

### 2. Set Parameters (Optional)

Click **▼ Parameters** to expand:
- **Tempo** - BPM (60-200)
- **Key** - C Major, A Minor, etc.
- **Time Signature** - 4/4, 3/4, 7/8, or custom
- **Genre** - rock, jazz, ambient, cinematic...
- **Mood** - melancholic, uplifting, aggressive...
- **Length** - Approximate bars
- **Chord Progression** - I-V-vi-IV, ii-V-I, etc.

### 3. Generate & Copy

Click **Generate Prompt** - the full prompt is copied to your clipboard.

### 4. Get AI Response

Paste the prompt into your AI of choice (ChatGPT, Claude, Gemini). Copy the response.

### 5. Parse & Load

Paste the AI response and click **Parse & Load**. You'll see:
- Song info (title, tempo, key, duration)
- Section breakdown with note/chord counts per track
- Track cards for each instrument

### 6. Preview & Adjust

- Click **▶ Play** to hear the preview
- Adjust SoundFonts and presets per track
- Volume sliders for mixing

### 7. Export

- **MIDI** - Import into any DAW (Ableton, FL Studio, Logic, etc.)
- **JSON** - Save/load projects

## DSL Format

The AI generates songs in this format:

```
SONG: My Song Title
TEMPO: 120
KEY: Am

SECTION: Intro [8 bars]
  PIANO: Am(w) | F(w) | C(w) | G(w) | Am(w) | F(w) | C(w) | G(w)
  STRINGS: Am(w,pp) | F(w,pp) | C(w,p) | G(w,p) | Am(w,mp) | F(w,mp) | C(w,mf) | G(w,mf)
  DRUMS: kick(1,3) snare(2,4) hat(8ths)

SECTION: Verse [16 bars]
  ...
```

### Notation
- **Chords**: `Am(w)` = A minor, whole note
- **Durations**: w=whole, h=half, q=quarter, e=eighth, s=sixteenth
- **Dynamics**: ppp, pp, p, mp, mf, f, ff, fff
- **Drums**: `kick(1,3)` = kick on beats 1 and 3, `hat(8ths)` = hi-hat every eighth

## Project Structure

```
Mother-Chord/
├── main.py              # Entry point
├── config.py            # Settings and GM instrument mappings
├── audio/
│   └── sf2_engine.py    # FluidSynth playback engine
├── generators/
│   └── midi_gen.py      # MIDI file generation
├── models/
│   └── song.py          # Song data structures
├── parser/
│   └── dsl_parser.py    # AI response parser
├── prompts/
│   └── generator.py     # Prompt generation with presets
├── ui/
│   ├── main_window.py   # Main application window
│   └── track_mixer.py   # Track card mixer widget
├── requirements.txt
├── setup.bat
└── run.bat
```

## Troubleshooting

### No Sound
- Make sure a SoundFont (.sf2) is in the `audio/` folder
- Check console for `[SF2 ENGINE] Loaded default SF2: ...`
- FluidSynth must be installed for preview to work

### Drums Not Working
- Drums use MIDI channel 10 with bank 128
- The parser looks for drum kit presets automatically
- Check that your SF2 has percussion instruments

### Parse Errors
- AI responses sometimes have formatting issues
- The parser handles most cases, but very malformed output may fail
- Check the console for `[PARSER]` debug messages

## License

MIT License - do whatever you want with it.

## Credits

Created by TeX (TeXmExDeX)

Built with:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [FluidSynth](https://www.fluidsynth.org/)
- [midiutil](https://github.com/MarkCWirt/MIDIUtil)
