"""
Main Window - TeX's Mother-Chord UI
TeXmExDeX Type Tunes
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox,
    QFrame, QSplitter, QFileDialog, QMessageBox, QScrollArea,
    QLineEdit, QSlider, QCheckBox, QGroupBox, QApplication,
    QDockWidget, QSizePolicy, QToolBar, QStatusBar, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QGuiApplication, QAction


class ToastNotification(QLabel):
    """Floating toast notification that fades away."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            background-color: #2a4a2a;
            color: #90d090;
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()
        
        # Opacity effect for fade
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
        # Fade animation
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.fade_anim.finished.connect(self.hide)
        
        # Timer to start fade
        self.fade_timer = QTimer(self)
        self.fade_timer.setSingleShot(True)
        self.fade_timer.timeout.connect(self.start_fade)
    
    def show_message(self, text: str, duration: int = 2000):
        """Show toast with message, auto-hide after duration."""
        self.setText(text)
        self.opacity_effect.setOpacity(1.0)
        self.adjustSize()
        
        # Center in parent
        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            y = 100  # Near top
            self.move(x, y)
        
        self.show()
        self.raise_()
        self.fade_timer.start(duration)
    
    def start_fade(self):
        self.fade_anim.start()

sys.path.append('..')
import config
from models import Song
from parser import parse_ai_response
from prompts import generate_song_prompt, get_preset_prompt, PRESET_PROMPTS
from generators import song_to_midi
from ui.track_mixer import TrackMixer

try:
    from audio.sf2_engine import SF2Engine, FLUIDSYNTH_AVAILABLE
except ImportError:
    SF2Engine = None
    FLUIDSYNTH_AVAILABLE = False


STYLESHEET = """
QMainWindow {
    background-color: #181818;
}

QWidget {
    background-color: transparent;
    color: #b0b0b0;
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    font-size: 14px;
}

QLabel {
    color: #707070;
    font-size: 12px;
    background: transparent;
}

QLabel#title {
    color: #888888;
    font-size: 18px;
    font-weight: 300;
    letter-spacing: 3px;
}

QLabel#section {
    color: #505050;
    font-size: 11px;
    letter-spacing: 2px;
}

QPushButton {
    background-color: #252525;
    border: 1px solid #333333;
    color: #909090;
    padding: 10px 20px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #2a2a2a;
    color: #b0b0b0;
}

QPushButton:pressed {
    background-color: #202020;
}

QPushButton:disabled {
    color: #404040;
    border-color: #282828;
}

QPushButton#action {
    background-color: #2a2a2a;
    border-color: #3a3a3a;
    color: #a0a0a0;
}

QPushButton#action:hover {
    background-color: #333333;
}

QTextEdit, QPlainTextEdit {
    background-color: #141414;
    border: 1px solid #252525;
    color: #a0a0a0;
    padding: 10px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 13px;
    selection-background-color: #333333;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #353535;
}

QLineEdit {
    background-color: #141414;
    border: 1px solid #252525;
    color: #a0a0a0;
    padding: 10px 12px;
    font-size: 14px;
}

QLineEdit:focus {
    border-color: #353535;
}

QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #2a2a2a;
    color: #909090;
    padding: 8px 12px;
    font-size: 13px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #505050;
}

QComboBox QAbstractItemView {
    background-color: #1a1a1a;
    border: 1px solid #303030;
    color: #a0a0a0;
    selection-background-color: #282828;
}

QSlider::groove:horizontal {
    height: 3px;
    background: #252525;
}

QSlider::handle:horizontal {
    background: #606060;
    width: 12px;
    height: 12px;
    margin: -5px 0;
}

QSlider::handle:horizontal:hover {
    background: #707070;
}

QSlider::sub-page:horizontal {
    background: #404040;
}

QScrollArea {
    border: none;
}

QScrollBar:vertical {
    background: #181818;
    width: 8px;
}

QScrollBar::handle:vertical {
    background: #303030;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #404040;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QFrame#separator {
    background-color: #252525;
    max-height: 1px;
}

QStatusBar {
    background-color: #141414;
    color: #505050;
    font-size: 11px;
}

QDockWidget {
    color: #606060;
    font-size: 11px;
}

QDockWidget::title {
    background-color: #1a1a1a;
    padding: 6px 10px;
    border-bottom: 1px solid #252525;
}
"""


class MotherChordWindow(QMainWindow):
    """Main application window - Track-focused layout."""

    def __init__(self):
        super().__init__()
        self.song = None

        self.sf2_engine = None
        if SF2Engine and FLUIDSYNTH_AVAILABLE:
            try:
                self.sf2_engine = SF2Engine()
            except Exception as e:
                print(f"[UI] SF2 Engine init failed: {e}")

        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview_position)

        self.setup_ui()
        
        # Toast notification (must be after setup_ui)
        self.toast = ToastNotification(self)

    def setup_ui(self):
        self.setWindowTitle("TeX's Mother-Chord")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === TOP: Input Bar ===
        input_bar = self._create_input_bar()
        main_layout.addWidget(input_bar)

        # === MIDDLE: Track Area (main focus) ===
        track_area = self._create_track_area()
        main_layout.addWidget(track_area, stretch=1)

        # === BOTTOM: Transport Bar ===
        transport_bar = self._create_transport_bar()
        main_layout.addWidget(transport_bar)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        self.setStatusBar(self.status_bar)

    def _create_input_bar(self) -> QWidget:
        """Compact input area at top with expandable parameters."""
        self.input_bar = QFrame()
        self.input_bar.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #252525;")
        self.params_expanded = False

        layout = QVBoxLayout(self.input_bar)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(8)

        # Row 1: Title + File buttons
        top_row = QHBoxLayout()

        title = QLabel("TeX's Mother-Chord")
        title.setObjectName("title")
        top_row.addWidget(title)

        top_row.addStretch()

        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_project)
        top_row.addWidget(new_btn)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_project)
        top_row.addWidget(open_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_project)
        top_row.addWidget(save_btn)

        layout.addLayout(top_row)

        # Row 2: Song description + expand button
        desc_row = QHBoxLayout()
        desc_row.setSpacing(10)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Describe your song... (e.g., 'epic orchestral piece with building tension')")
        desc_row.addWidget(self.description_input, stretch=1)

        # Expand/collapse parameters button
        self.expand_btn = QPushButton("▼ Parameters")
        self.expand_btn.setFixedWidth(110)
        self.expand_btn.clicked.connect(self.toggle_parameters)
        desc_row.addWidget(self.expand_btn)

        layout.addLayout(desc_row)

        # Row 3: Expandable parameters (hidden by default)
        self.params_widget = QWidget()
        self.params_widget.setVisible(False)
        params_main = QVBoxLayout(self.params_widget)
        params_main.setContentsMargins(0, 12, 0, 12)
        params_main.setSpacing(16)

        # === Parameters Row 1: Core Music Settings (fills width) ===
        row1 = QHBoxLayout()
        row1.setSpacing(0)

        # Helper to create param input with stretch
        def add_param(label_text, widget, stretch=1):
            container = QVBoxLayout()
            container.setSpacing(4)
            lbl = QLabel(label_text)
            container.addWidget(lbl)
            container.addWidget(widget)
            row1.addLayout(container, stretch)
            row1.addSpacing(16)

        # Tempo
        self.tempo_input = QLineEdit()
        self.tempo_input.setPlaceholderText("60-200")
        add_param("Tempo (BPM)", self.tempo_input, 1)

        # Key
        self.key_combo = QComboBox()
        self.key_combo.addItems([
            "", "C Major", "G Major", "D Major", "A Major", "E Major", "B Major", "F Major", "Bb Major",
            "A Minor", "E Minor", "B Minor", "F# Minor", "C# Minor", "D Minor", "G Minor", "C Minor"
        ])
        add_param("Key", self.key_combo, 1)

        # Time Signature (with custom option)
        time_container = QWidget()
        time_inner = QHBoxLayout(time_container)
        time_inner.setContentsMargins(0, 0, 0, 0)
        time_inner.setSpacing(6)
        self.time_combo = QComboBox()
        self.time_combo.addItems(["4/4", "3/4", "6/8", "2/4", "5/4", "7/8", "12/8", "Custom..."])
        self.time_combo.currentTextChanged.connect(self._on_time_sig_change)
        time_inner.addWidget(self.time_combo)
        self.custom_time_input = QLineEdit()
        self.custom_time_input.setPlaceholderText("e.g. 11/8")
        self.custom_time_input.setVisible(False)
        time_inner.addWidget(self.custom_time_input)
        add_param("Time Signature", time_container, 1)

        # Genre/Style
        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("rock, jazz, ambient...")
        add_param("Genre / Style", self.genre_input, 2)

        # Mood
        self.mood_input = QLineEdit()
        self.mood_input.setPlaceholderText("melancholic, uplifting...")
        add_param("Mood / Feel", self.mood_input, 2)

        # Length
        self.length_input = QLineEdit()
        self.length_input.setPlaceholderText("32")
        add_param("Length (bars)", self.length_input, 1)

        # Chord Progression (wider)
        self.chords_input = QLineEdit()
        self.chords_input.setPlaceholderText("I-V-vi-IV, ii-V-I...")
        add_param("Chord Progression", self.chords_input, 3)

        params_main.addLayout(row1)

        # === Music Theory Helper Panel ===
        theory_frame = QFrame()
        theory_frame.setStyleSheet("""
            QFrame { background-color: #141414; border: 1px solid #252525; }
            QLabel { color: #606060; font-size: 11px; }
        """)
        theory_layout = QVBoxLayout(theory_frame)
        theory_layout.setContentsMargins(12, 10, 12, 10)
        theory_layout.setSpacing(8)

        theory_header = QLabel("MUSIC THEORY QUICK REFERENCE")
        theory_header.setStyleSheet("color: #505050; font-size: 10px; letter-spacing: 2px;")
        theory_layout.addWidget(theory_header)

        # Theory content in columns (evenly distributed)
        theory_cols = QHBoxLayout()
        theory_cols.setSpacing(0)

        def add_theory_col(title, items):
            col = QVBoxLayout()
            col.setSpacing(4)
            header = QLabel(title)
            header.setStyleSheet("color: #707070; font-size: 11px; font-weight: bold;")
            col.addWidget(header)
            for item in items:
                col.addWidget(QLabel(item))
            col.addStretch()
            theory_cols.addLayout(col, 1)

        add_theory_col("SONG STRUCTURES", [
            "• Verse-Chorus: ABABCB",
            "• AABA (32-bar): Jazz",
            "• Through-composed",
            "• Rondo: ABACADA",
            "• Build-Drop: EDM"
        ])

        add_theory_col("CHORD PROGRESSIONS", [
            "• I-V-vi-IV: Pop anthem",
            "• ii-V-I: Jazz resolution",
            "• i-VI-III-VII: Cinematic",
            "• I-IV-V: Blues/rock",
            "• vi-IV-I-V: Emotional"
        ])

        add_theory_col("TEMPO GUIDE", [
            "• 60-70: Ballad, ambient",
            "• 80-100: Hip-hop, R&B",
            "• 100-120: Pop, rock",
            "• 120-140: Dance, punk",
            "• 140+: DnB, metal"
        ])

        add_theory_col("KEY MOODS", [
            "• Major: Happy, bright",
            "• Minor: Sad, dark",
            "• Dorian: Jazzy minor",
            "• Mixolydian: Bluesy",
            "• Phrygian: Spanish"
        ])

        add_theory_col("STAND OUT IDEAS", [
            "• Odd time: 5/4, 7/8",
            "• Key changes mid-song",
            "• Polyrhythms: 3 over 4",
            "• Unexpected instruments",
            "• Dynamic contrast"
        ])

        theory_layout.addLayout(theory_cols)

        params_main.addWidget(theory_frame)
        layout.addWidget(self.params_widget)

        # Row 4: Generate + Paste response
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        # Preset combo
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Custom")
        for name in PRESET_PROMPTS.keys():
            self.preset_combo.addItem(name.replace('_', ' ').title(), name)
        self.preset_combo.setFixedWidth(140)
        action_row.addWidget(self.preset_combo)

        # Generate button
        gen_btn = QPushButton("Generate Prompt")
        gen_btn.setObjectName("action")
        gen_btn.clicked.connect(self.generate_prompt)
        action_row.addWidget(gen_btn)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #303030;")
        action_row.addWidget(sep)

        # Paste response
        self.response_input = QLineEdit()
        self.response_input.setPlaceholderText("Paste AI response here...")
        action_row.addWidget(self.response_input, stretch=1)

        # Parse button
        parse_btn = QPushButton("Parse & Load")
        parse_btn.setObjectName("action")
        parse_btn.clicked.connect(self.parse_response)
        action_row.addWidget(parse_btn)

        layout.addLayout(action_row)

        return self.input_bar

    def toggle_parameters(self):
        """Toggle the parameters panel visibility."""
        self.params_expanded = not self.params_expanded
        self.params_widget.setVisible(self.params_expanded)
        self.expand_btn.setText("▲ Parameters" if self.params_expanded else "▼ Parameters")

    def _on_time_sig_change(self, text):
        """Show custom time signature input when 'Custom...' is selected."""
        self.custom_time_input.setVisible(text == "Custom...")
        self.params_widget.setVisible(self.params_expanded)
        self.expand_btn.setText("▲ Parameters" if self.params_expanded else "▼ Parameters")

    def _create_track_area(self) -> QWidget:
        """Main track/mixer area."""
        area = QFrame()
        area.setStyleSheet("background-color: #181818;")

        layout = QHBoxLayout(area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left: Song info panel
        info_panel = self._create_info_panel()
        layout.addWidget(info_panel)

        # Center: Track mixer (main focus)
        self.track_mixer = TrackMixer()
        if self.sf2_engine:
            self.track_mixer.set_engine(self.sf2_engine)
        self.track_mixer.setStyleSheet("background-color: #1c1c1c; border-left: 1px solid #252525;")
        layout.addWidget(self.track_mixer, stretch=1)

        return area

    def _create_info_panel(self) -> QWidget:
        """Song info and preview panel."""
        panel = QFrame()
        panel.setFixedWidth(320)
        panel.setStyleSheet("background-color: #1a1a1a;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Song info header
        header = QLabel("SONG INFO")
        header.setObjectName("section")
        layout.addWidget(header)

        # Song details
        self.song_title_label = QLabel("No song loaded")
        self.song_title_label.setStyleSheet("color: #909090; font-size: 16px;")
        self.song_title_label.setWordWrap(True)
        layout.addWidget(self.song_title_label)

        self.song_details_label = QLabel("")
        self.song_details_label.setStyleSheet("color: #606060; font-size: 13px;")
        self.song_details_label.setWordWrap(True)
        layout.addWidget(self.song_details_label)

        layout.addSpacing(10)

        # Sections list
        sections_header = QLabel("SECTIONS")
        sections_header.setObjectName("section")
        layout.addWidget(sections_header)

        self.sections_list = QPlainTextEdit()
        self.sections_list.setReadOnly(True)
        self.sections_list.setStyleSheet("""
            background-color: #141414;
            border: 1px solid #222222;
            color: #808080;
            font-size: 12px;
        """)
        self.sections_list.setMaximumHeight(200)
        layout.addWidget(self.sections_list)

        layout.addStretch()

        # Export section
        export_header = QLabel("EXPORT")
        export_header.setObjectName("section")
        layout.addWidget(export_header)

        export_row = QHBoxLayout()
        export_row.setSpacing(8)

        midi_btn = QPushButton("MIDI")
        midi_btn.clicked.connect(self.export_midi)
        export_row.addWidget(midi_btn)

        json_btn = QPushButton("JSON")
        json_btn.clicked.connect(self.export_json)
        export_row.addWidget(json_btn)

        layout.addLayout(export_row)

        return panel

    def _create_transport_bar(self) -> QWidget:
        """Bottom transport controls."""
        bar = QFrame()
        bar.setStyleSheet("background-color: #141414; border-top: 1px solid #252525;")
        bar.setFixedHeight(60)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(15)

        # Play/Pause
        self.play_btn = QPushButton("▶  Play")
        self.play_btn.setFixedWidth(100)
        self.play_btn.clicked.connect(self.toggle_preview)
        self.play_btn.setEnabled(False)
        layout.addWidget(self.play_btn)

        # Stop
        self.stop_btn = QPushButton("◼  Stop")
        self.stop_btn.setFixedWidth(100)
        self.stop_btn.clicked.connect(self.stop_preview)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setEnabled(False)
        layout.addWidget(self.progress_slider, stretch=1)

        # Time display
        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setStyleSheet("color: #606060; font-family: monospace; font-size: 13px;")
        self.time_label.setFixedWidth(100)
        layout.addWidget(self.time_label)

        layout.addStretch()

        # Tagline
        tagline = QLabel("TeXmExDeX Type Tunes")
        tagline.setStyleSheet("color: #404040; font-size: 11px;")
        layout.addWidget(tagline)

        return bar

    # === Actions ===

    def generate_prompt(self):
        """Generate prompt and copy to clipboard."""
        description = self.description_input.text().strip()
        if not description:
            self.status_bar.showMessage("Enter a song description first")
            return

        preset_key = self.preset_combo.currentData()
        if preset_key:
            prompt = get_preset_prompt(preset_key, description)
        else:
            # Gather all parameters
            tempo = self.tempo_input.text().strip()
            key = self.key_combo.currentText()
            
            # Handle custom time signature
            time_sig = self.time_combo.currentText()
            if time_sig == "Custom...":
                time_sig = self.custom_time_input.text().strip()
            
            genre = self.genre_input.text().strip()
            mood = self.mood_input.text().strip()
            length = self.length_input.text().strip()
            chords = self.chords_input.text().strip()

            prompt = generate_song_prompt(
                description=description,
                style=genre,
                mood=mood,
                tempo_hint=tempo,
                key_hint=key,
                time_sig=time_sig if time_sig and time_sig != "4/4" else "",
                length_bars=length,
                chord_progression=chords
            )

        QGuiApplication.clipboard().setText(prompt)
        self.status_bar.showMessage("Prompt copied to clipboard")
        self.toast.show_message("✓ Copied to Clipboard!", 2500)

    def parse_response(self):
        """Parse AI response and load song."""
        response = self.response_input.text().strip()
        if not response:
            self.status_bar.showMessage("Paste the AI response first")
            return

        song, errors, warnings = parse_ai_response(response, debug=True)

        if errors:
            self.status_bar.showMessage(f"Parse error: {errors[0]}")
            return

        if song:
            self.song = song
            self._load_song(song)
            self.status_bar.showMessage(f"Loaded: {song.title}")

    def _load_song(self, song: Song):
        """Load song into UI."""
        # Update info panel
        self.song_title_label.setText(song.title)
        self.song_details_label.setText(
            f"{song.tempo} BPM  •  {song.key}  •  {int(song.duration_seconds)}s"
        )

        # Detailed sections breakdown
        sections_text = ""
        for s in song.sections:
            sections_text += f"━━ {s.name} ({s.bars} bars) ━━\n"
            
            # Track details
            for track in s.tracks:
                notes = len(track.notes)
                chords = len(track.chords)
                parts = []
                if notes > 0:
                    parts.append(f"{notes} notes")
                if chords > 0:
                    parts.append(f"{chords} chords")
                detail = ", ".join(parts) if parts else "empty"
                sections_text += f"  {track.name}: {detail}\n"
            
            # Drums
            if s.drums and s.drums.hits:
                sections_text += f"  Drums: {len(s.drums.hits)} hits\n"
            elif s.drums:
                sections_text += f"  Drums: empty\n"
            
            sections_text += "\n"
        
        self.sections_list.setPlainText(sections_text.strip())

        # Load into mixer
        self.track_mixer.load_tracks_from_song(song)

        # Load into audio engine
        if self.sf2_engine and self.sf2_engine.is_available():
            self.sf2_engine.load_song(song)
            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.progress_slider.setEnabled(True)
            self.progress_slider.setMaximum(int(song.duration_seconds))

    def toggle_preview(self):
        if not self.sf2_engine or not self.song:
            return

        if self.sf2_engine.is_playing:
            self.sf2_engine.pause()
            self.play_btn.setText("▶  Play")
            self.preview_timer.stop()
        else:
            if self.sf2_engine.play():
                self.play_btn.setText("⏸  Pause")
                self.preview_timer.start(100)

    def stop_preview(self):
        if self.sf2_engine:
            self.sf2_engine.stop()
            self.play_btn.setText("▶  Play")
            self.preview_timer.stop()
            self.progress_slider.setValue(0)
            self.time_label.setText("0:00 / 0:00")

    def update_preview_position(self):
        if not self.sf2_engine or not self.sf2_engine.is_playing:
            self.preview_timer.stop()
            self.play_btn.setText("▶  Play")
            return

        pos = self.sf2_engine.get_position()
        dur = self.sf2_engine.get_duration()

        self.progress_slider.setValue(int(pos))

        pm, ps = int(pos // 60), int(pos % 60)
        dm, ds = int(dur // 60), int(dur % 60)
        self.time_label.setText(f"{pm}:{ps:02d} / {dm}:{ds:02d}")

        if pos >= dur:
            self.stop_preview()

    def export_midi(self):
        if not self.song:
            self.status_bar.showMessage("No song to export")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export MIDI", f"{self.song.title}.mid", "MIDI Files (*.mid)"
        )
        if filepath:
            if song_to_midi(self.song, filepath):
                self.status_bar.showMessage(f"Exported: {filepath}")
            else:
                self.status_bar.showMessage("Export failed")

    def export_json(self):
        if not self.song:
            self.status_bar.showMessage("No song to export")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", f"{self.song.title}.json", "JSON Files (*.json)"
        )
        if filepath:
            with open(filepath, 'w') as f:
                f.write(self.song.to_json())
            self.status_bar.showMessage(f"Exported: {filepath}")

    def new_project(self):
        self.song = None
        self.description_input.clear()
        self.response_input.clear()
        self.song_title_label.setText("No song loaded")
        self.song_details_label.setText("")
        self.sections_list.clear()
        self.track_mixer.clear_tracks()
        self.status_bar.showMessage("New project")

    def open_project(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "JSON Files (*.json)"
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    self.song = Song.from_json(f.read())
                self._load_song(self.song)
                self.status_bar.showMessage(f"Opened: {self.song.title}")
            except Exception as e:
                self.status_bar.showMessage(f"Failed to open: {e}")

    def save_project(self):
        if self.song:
            self.export_json()
        else:
            self.status_bar.showMessage("No song to save")

    def closeEvent(self, event):
        if self.sf2_engine:
            self.sf2_engine.cleanup()
        event.accept()


def run_app():
    print(f"[{config.APP_NAME}] Launching...")
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    window = MotherChordWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
