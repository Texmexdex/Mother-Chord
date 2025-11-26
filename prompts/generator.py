"""
Prompt Generator - Creates perfectly structured prompts for AI song generation.
"""

SONG_DSL_SPEC = '''
## SONG DSL FORMAT SPECIFICATION

You must output a song in this EXACT format. No explanations, just the DSL code.

### Structure:
```
SONG: [Title]
TEMPO: [BPM as integer, e.g., 120]
KEY: [Key signature, e.g., Am, C, F#m, Bb]

SECTION: [Name] [X bars]
  [INSTRUMENT]: [pattern]
  [INSTRUMENT]: [pattern]
  DRUMS: [drum pattern]

SECTION: [Name] [X bars]
  ...
```

### Instrument Pattern Format:
Each bar separated by `|`. Chords/notes with duration in parentheses.

Durations: w=whole, h=half, q=quarter, e=eighth, s=sixteenth
Dynamics: ppp, pp, p, mp, mf, f, ff, fff

Examples:
- `Am(w)` = A minor chord, whole note
- `C(h) G(h)` = C chord half note, G chord half note (fills one bar)
- `F(q) Am(q) | Dm(h)` = Two bars
- `_` = Rest/silent bar

### Drum Pattern Format:
`[drum](beats)` where beats are 1-4 (quarter notes) or special patterns.

Drums: kick, snare, hat, open_hat, crash, ride, tom_low, tom_mid, tom_high
Special: 8ths (every eighth note), 16ths (every sixteenth)

Examples:
- `kick(1,3) snare(2,4)` = Standard rock beat
- `hat(8ths)` = Hi-hat on every eighth note
- `kick(1) snare(2,4) hat(8ths)` = Combined pattern

### Available Instruments:
piano, strings, bass, drums, guitar, synth, lead, pad, organ, brass, 
flute, violin, cello, choir, voice, sax, trumpet

### Example Complete Song:
```
SONG: Midnight Dreams
TEMPO: 85
KEY: Am

SECTION: Intro [4 bars]
  PIANO: Am(w) | F(w) | C(w) | G(w)
  STRINGS: _ | _ | Am(w,pp) | F(w,pp)

SECTION: Verse [8 bars]
  PIANO: Am(h) Em(h) | F(w) | Dm(h) Am(h) | E(w) | Am(h) Em(h) | F(w) | G(w) | Am(w)
  BASS: A2(w) | F2(w) | D2(w) | E2(w) | A2(w) | F2(w) | G2(w) | A2(w)
  DRUMS: kick(1,3) snare(2,4) hat(8ths)

SECTION: Chorus [8 bars]
  PIANO: F(w) | G(w) | Am(w) | Em(w) | F(w) | G(w) | C(h) G(h) | Am(w)
  STRINGS: F(w,mf) | G(w,mf) | Am(w,mf) | Em(w,mf) | F(w,f) | G(w,f) | C(w,f) | Am(w,f)
  BASS: F2(w) | G2(w) | A2(w) | E2(w) | F2(w) | G2(w) | C2(h) G2(h) | A2(w)
  DRUMS: kick(1,3) snare(2,4) hat(8ths) crash(1)

SECTION: Outro [4 bars]
  PIANO: Am(w,mp) | F(w,p) | C(w,pp) | Am(w,ppp)
  STRINGS: Am(w,mp) | F(w,p) | C(w,pp) | Am(w,ppp)
```
'''


def generate_song_prompt(
    description: str,
    style: str = "",
    mood: str = "",
    tempo_hint: str = "",
    key_hint: str = "",
    instruments: list[str] = None,
    structure_hint: str = "",
    duration_hint: str = "",
    time_sig: str = "",
    length_bars: str = "",
    chord_progression: str = ""
) -> str:
    """
    Generate a complete prompt for AI song generation.
    
    Args:
        description: Main description of the song
        style: Musical style (rock, jazz, classical, electronic, etc.)
        mood: Emotional mood (happy, sad, energetic, calm, etc.)
        tempo_hint: Tempo suggestion (slow, medium, fast, or specific BPM)
        key_hint: Key suggestion (major, minor, or specific key)
        instruments: List of instruments to use
        structure_hint: Song structure hint (simple, complex, verse-chorus, etc.)
        duration_hint: Approximate duration (short, medium, long)
        time_sig: Time signature (4/4, 3/4, 6/8, etc.)
        length_bars: Approximate length in bars
        chord_progression: Suggested chord progression
    
    Returns:
        Complete prompt string ready to paste into AI chat.
    """
    
    prompt_parts = []
    
    # Header
    prompt_parts.append("# SONG GENERATION REQUEST")
    prompt_parts.append("")
    prompt_parts.append("Generate a complete song in the DSL format specified below.")
    prompt_parts.append("Output ONLY the DSL code - no explanations before or after.")
    prompt_parts.append("")
    
    # User's description
    prompt_parts.append("## SONG DESCRIPTION:")
    prompt_parts.append(description)
    prompt_parts.append("")
    
    # Additional parameters
    has_params = any([style, mood, tempo_hint, key_hint, instruments, structure_hint, 
                      duration_hint, time_sig, length_bars, chord_progression])
    if has_params:
        prompt_parts.append("## PARAMETERS:")
        
        if style:
            prompt_parts.append(f"- Style/Genre: {style}")
        if mood:
            prompt_parts.append(f"- Mood: {mood}")
        if tempo_hint:
            prompt_parts.append(f"- Tempo: {tempo_hint} BPM")
        if key_hint:
            prompt_parts.append(f"- Key: {key_hint}")
        if time_sig:
            prompt_parts.append(f"- Time Signature: {time_sig}")
        if length_bars:
            prompt_parts.append(f"- Approximate Length: {length_bars} bars")
        if chord_progression:
            prompt_parts.append(f"- Chord Progression: {chord_progression}")
        if instruments:
            prompt_parts.append(f"- Instruments: {', '.join(instruments)}")
        if structure_hint:
            prompt_parts.append(f"- Structure: {structure_hint}")
        if duration_hint:
            prompt_parts.append(f"- Duration: {duration_hint}")
        
        prompt_parts.append("")
    
    # DSL specification
    prompt_parts.append(SONG_DSL_SPEC)
    
    # Final instruction
    prompt_parts.append("")
    prompt_parts.append("## YOUR OUTPUT:")
    prompt_parts.append("Generate the complete song now. Start with `SONG:` and include all sections.")
    prompt_parts.append("Remember: Output ONLY the DSL code, no explanations.")
    
    return '\n'.join(prompt_parts)


def generate_section_prompt(
    section_type: str,
    bars: int,
    key: str,
    tempo: int,
    instruments: list[str],
    mood: str = "",
    reference: str = ""
) -> str:
    """
    Generate a prompt for a single section (for editing/regenerating).
    """
    
    prompt = f"""# GENERATE SONG SECTION

Generate a {section_type} section with these parameters:
- Bars: {bars}
- Key: {key}
- Tempo: {tempo}
- Instruments: {', '.join(instruments)}
"""
    
    if mood:
        prompt += f"- Mood: {mood}\n"
    
    if reference:
        prompt += f"\nReference/Context: {reference}\n"
    
    prompt += f"""
Output ONLY the section in this format:
```
SECTION: {section_type} [{bars} bars]
  [instrument patterns...]
  DRUMS: [drum pattern]
```

Use the DSL format with chords like `Am(w)`, `F(h)`, etc.
Durations: w=whole, h=half, q=quarter, e=eighth
Dynamics: pp, p, mp, mf, f, ff
"""
    
    return prompt


# Preset prompts for common song types
PRESET_PROMPTS = {
    'pop_ballad': {
        'style': 'pop ballad',
        'mood': 'emotional, heartfelt',
        'tempo_hint': '70-85 BPM',
        'instruments': ['piano', 'strings', 'bass', 'drums'],
        'structure_hint': 'intro, verse, chorus, verse, chorus, bridge, chorus, outro'
    },
    'rock_anthem': {
        'style': 'rock anthem',
        'mood': 'powerful, energetic',
        'tempo_hint': '120-140 BPM',
        'instruments': ['guitar', 'bass', 'drums', 'synth'],
        'structure_hint': 'intro, verse, pre-chorus, chorus, verse, chorus, solo, chorus, outro'
    },
    'chill_lofi': {
        'style': 'lo-fi hip hop',
        'mood': 'relaxed, nostalgic',
        'tempo_hint': '75-90 BPM',
        'instruments': ['piano', 'bass', 'drums', 'pad'],
        'structure_hint': 'intro, main loop A, main loop B, main loop A, outro'
    },
    'epic_cinematic': {
        'style': 'cinematic orchestral',
        'mood': 'epic, dramatic',
        'tempo_hint': '90-110 BPM',
        'instruments': ['strings', 'brass', 'piano', 'drums', 'choir'],
        'structure_hint': 'intro, build, climax, resolution'
    },
    'jazz_standard': {
        'style': 'jazz',
        'mood': 'sophisticated, smooth',
        'tempo_hint': '120-160 BPM',
        'instruments': ['piano', 'bass', 'drums', 'sax'],
        'structure_hint': 'head, solo section, head out'
    },
    'electronic_dance': {
        'style': 'electronic dance',
        'mood': 'energetic, driving',
        'tempo_hint': '125-130 BPM',
        'instruments': ['synth', 'bass', 'drums', 'lead', 'pad'],
        'structure_hint': 'intro, buildup, drop, breakdown, buildup, drop, outro'
    },
    'ambient': {
        'style': 'ambient',
        'mood': 'atmospheric, peaceful',
        'tempo_hint': '60-80 BPM',
        'instruments': ['pad', 'strings', 'piano'],
        'structure_hint': 'evolving texture, minimal structure'
    },
    'classical_piece': {
        'style': 'classical',
        'mood': 'elegant, refined',
        'tempo_hint': 'varies by movement',
        'instruments': ['piano', 'strings', 'flute'],
        'structure_hint': 'exposition, development, recapitulation'
    }
}


def get_preset_prompt(preset_name: str, description: str) -> str:
    """Generate a prompt using a preset configuration."""
    if preset_name not in PRESET_PROMPTS:
        return generate_song_prompt(description)
    
    preset = PRESET_PROMPTS[preset_name]
    return generate_song_prompt(
        description=description,
        **preset
    )
