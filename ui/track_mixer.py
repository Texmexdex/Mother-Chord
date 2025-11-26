"""
Track Mixer Widget - Per-track volume, SF2 selection, and preset controls.
Card-based layout for multiple tracks.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QScrollArea, QFrame, QFileDialog,
    QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
import os
import glob
import sys

sys.path.append('..')
import config

try:
    from sf2utils.sf2parse import Sf2File
    SF2UTILS_AVAILABLE = True
except ImportError:
    SF2UTILS_AVAILABLE = False


class TrackCard(QFrame):
    """Compact track card with volume and SF2 controls."""

    volumeChanged = pyqtSignal(str, float)
    soundfontChanged = pyqtSignal(str, str)
    presetChanged = pyqtSignal(str, int, int)

    def __init__(self, track_name: str, instrument: str = "", parent=None):
        super().__init__(parent)
        self.track_name = track_name
        self.instrument = instrument
        self.sf2_path = None

        self.setFixedWidth(220)
        self.setMinimumHeight(180)
        self.setStyleSheet("""
            TrackCard {
                background: #1e1e1e;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
            }
            TrackCard:hover {
                border-color: #3a3a3a;
            }
            QLabel {
                color: #808080;
                font-size: 11px;
            }
            QComboBox {
                background: #141414;
                border: 1px solid #2a2a2a;
                color: #909090;
                padding: 4px 8px;
                font-size: 11px;
            }
            QSlider::groove:horizontal {
                height: 3px;
                background: #2a2a2a;
            }
            QSlider::handle:horizontal {
                background: #606060;
                width: 10px;
                margin: -4px 0;
            }
            QSlider::sub-page:horizontal {
                background: #505050;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Track name (header)
        name_label = QLabel(self.track_name)
        name_label.setStyleSheet("color: #b0b0b0; font-size: 13px; font-weight: bold;")
        layout.addWidget(name_label)

        # Instrument type
        if self.instrument:
            inst_label = QLabel(self.instrument)
            inst_label.setStyleSheet("color: #505050; font-size: 10px;")
            layout.addWidget(inst_label)

        layout.addSpacing(4)

        # Volume
        vol_row = QHBoxLayout()
        vol_row.setSpacing(6)
        vol_row.addWidget(QLabel("Vol"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self._on_volume_change)
        vol_row.addWidget(self.volume_slider)
        self.vol_label = QLabel("80")
        self.vol_label.setFixedWidth(24)
        self.vol_label.setStyleSheet("color: #606060;")
        vol_row.addWidget(self.vol_label)
        layout.addLayout(vol_row)

        # SF2 selector
        layout.addWidget(QLabel("SoundFont"))
        sf2_row = QHBoxLayout()
        sf2_row.setSpacing(4)
        self.sf2_combo = QComboBox()
        self.sf2_combo.addItem("Default GM")
        self.sf2_combo.currentIndexChanged.connect(self._on_sf2_change)
        self.sf2_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sf2_row.addWidget(self.sf2_combo)
        browse_btn = QPushButton("...")
        browse_btn.setFixedSize(24, 24)
        browse_btn.setStyleSheet("padding: 0;")
        browse_btn.clicked.connect(self._browse_sf2)
        sf2_row.addWidget(browse_btn)
        layout.addLayout(sf2_row)

        # Preset selector
        layout.addWidget(QLabel("Preset"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("0:0 - Default")
        self.preset_combo.setEnabled(False)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_change)
        layout.addWidget(self.preset_combo)

        layout.addStretch()

    def _on_volume_change(self, value):
        self.vol_label.setText(str(value))
        self.volumeChanged.emit(self.track_name, value / 100.0)

    def _on_sf2_change(self, index):
        if index == 0:
            self.sf2_path = None
            self.preset_combo.clear()
            self.preset_combo.addItem("0:0 - Default")
            self.preset_combo.setEnabled(False)
        else:
            self.sf2_path = self.sf2_combo.itemData(index)
            self._load_presets_from_sf2(self.sf2_path)
            self.preset_combo.setEnabled(True)
        self.soundfontChanged.emit(self.track_name, self.sf2_path or "")

    def _load_presets_from_sf2(self, sf2_path: str):
        self.preset_combo.clear()
        if not SF2UTILS_AVAILABLE or not sf2_path:
            self.preset_combo.addItem("0:0 - Default", (0, 0))
            return
        try:
            with open(sf2_path, 'rb') as f:
                sf2 = Sf2File(f)
                presets = []
                for preset in sf2.presets:
                    if preset.name and preset.name != "EOP":
                        presets.append((preset.bank, preset.preset, preset.name))
                presets.sort(key=lambda x: (x[0], x[1]))
                for bank, prog, name in presets:
                    display = f"{bank}:{prog} {name[:18]}"
                    self.preset_combo.addItem(display, (bank, prog))
                if not presets:
                    self.preset_combo.addItem("0:0 - Default", (0, 0))
                else:
                    # Auto-select preset based on instrument name
                    self._auto_select_preset()
        except Exception as e:
            self.preset_combo.addItem("0:0 - Default", (0, 0))
    
    def _auto_select_preset(self):
        """Auto-select the correct preset based on instrument name."""
        if not self.instrument:
            return
        
        inst_lower = self.instrument.lower()
        
        # Special handling for drums - look for drum kit presets (bank 128)
        if inst_lower in ('drums', 'drum', 'percussion', 'perc', 'kit'):
            # Try to find a drum kit (usually bank 128, or has "drum" in name)
            for i in range(self.preset_combo.count()):
                data = self.preset_combo.itemData(i)
                text = self.preset_combo.itemText(i).lower()
                if data:
                    # Bank 128 is percussion bank in GM
                    if data[0] == 128:
                        self.preset_combo.setCurrentIndex(i)
                        return
                    # Or look for "drum" or "kit" in preset name
                    if 'drum' in text or 'kit' in text or 'perc' in text:
                        self.preset_combo.setCurrentIndex(i)
                        return
            return
        
        # Get the GM program number for this instrument
        gm_program = config.GM_INSTRUMENTS.get(inst_lower)
        
        if gm_program == 'drums' or gm_program is None:
            return
        
        # Find a preset matching this program number (bank 0)
        for i in range(self.preset_combo.count()):
            data = self.preset_combo.itemData(i)
            if data and data[0] == 0 and data[1] == gm_program:
                self.preset_combo.setCurrentIndex(i)
                return
        
        # If exact match not found, just use the GM program number
        for i in range(self.preset_combo.count()):
            data = self.preset_combo.itemData(i)
            if data and data[1] == gm_program:
                self.preset_combo.setCurrentIndex(i)
                return

    def _on_preset_change(self, index):
        if index >= 0:
            data = self.preset_combo.itemData(index)
            if data:
                bank, preset = data
                self.presetChanged.emit(self.track_name, bank, preset)

    def _browse_sf2(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select SoundFont", "", "SoundFont Files (*.sf2 *.SF2)"
        )
        if path:
            self.add_soundfont(path)
            idx = self.sf2_combo.findData(path)
            if idx >= 0:
                self.sf2_combo.setCurrentIndex(idx)

    def add_soundfont(self, path: str):
        name = os.path.basename(path)
        for i in range(self.sf2_combo.count()):
            if self.sf2_combo.itemData(i) == path:
                return
        # Truncate long names
        display = name[:25] + "..." if len(name) > 28 else name
        self.sf2_combo.addItem(display, path)


class TrackMixer(QWidget):
    """Track mixer with card-based layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.track_cards: dict[str, TrackCard] = {}
        self.sf2_engine = None
        self.soundfont_dir = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #252525;")
        header.setFixedHeight(44)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("TRACKS")
        title.setStyleSheet("color: #606060; font-size: 11px; letter-spacing: 2px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.sf2_folder_btn = QPushButton("Load SF2 Folder")
        self.sf2_folder_btn.setStyleSheet("padding: 6px 12px; font-size: 11px;")
        self.sf2_folder_btn.clicked.connect(self._select_sf2_folder)
        header_layout.addWidget(self.sf2_folder_btn)

        layout.addWidget(header)

        # Scroll area for track cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("background-color: #181818; border: none;")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background-color: #181818;")
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(16, 16, 16, 16)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)

        # Status bar
        status_bar = QFrame()
        status_bar.setStyleSheet("background-color: #141414; border-top: 1px solid #252525;")
        status_bar.setFixedHeight(28)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(16, 0, 16, 0)

        self.status_label = QLabel("No tracks loaded")
        self.status_label.setStyleSheet("color: #505050; font-size: 11px;")
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_bar)

    def set_engine(self, engine):
        self.sf2_engine = engine

    def load_tracks_from_song(self, song):
        self.clear_tracks()
        tracks_seen = {}
        for section in song.sections:
            for track in section.tracks:
                if track.name not in tracks_seen:
                    tracks_seen[track.name] = track.instrument
            if section.drums and "Drums" not in tracks_seen:
                tracks_seen["Drums"] = "drums"

        for name, instrument in tracks_seen.items():
            self.add_track(name, instrument)

        self.status_label.setText(f"{len(tracks_seen)} tracks")

    def add_track(self, name: str, instrument: str = ""):
        if name in self.track_cards:
            return

        card = TrackCard(name, instrument)
        card.volumeChanged.connect(self._on_volume_change)
        card.soundfontChanged.connect(self._on_sf2_change)
        card.presetChanged.connect(self._on_preset_change)

        # Add default SF2 from engine if available
        if self.sf2_engine and hasattr(self.sf2_engine, 'default_sf_path'):
            default_path = getattr(self.sf2_engine, 'default_sf_path', None)
            if default_path:
                card.add_soundfont(default_path)
                # Auto-select the default SF2
                idx = card.sf2_combo.findData(default_path)
                if idx >= 0:
                    card.sf2_combo.setCurrentIndex(idx)

        if self.soundfont_dir:
            self._populate_sf2_combo(card)

        self.track_cards[name] = card
        self.cards_layout.addWidget(card)

    def clear_tracks(self):
        for card in self.track_cards.values():
            card.deleteLater()
        self.track_cards.clear()

    def _select_sf2_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select SoundFont Folder")
        if folder:
            self.soundfont_dir = folder
            self._refresh_sf2_lists()

    def _refresh_sf2_lists(self):
        if not self.soundfont_dir:
            return
        for card in self.track_cards.values():
            self._populate_sf2_combo(card)

    def _populate_sf2_combo(self, card: TrackCard):
        if not self.soundfont_dir:
            return
        sf2_files = glob.glob(os.path.join(self.soundfont_dir, "*.sf2"))
        sf2_files += glob.glob(os.path.join(self.soundfont_dir, "*.SF2"))
        for sf2_path in sorted(sf2_files):
            card.add_soundfont(sf2_path)

    def _on_volume_change(self, track_name: str, volume: float):
        if self.sf2_engine:
            self.sf2_engine.set_track_volume(track_name, volume)

    def _on_sf2_change(self, track_name: str, sf2_path: str):
        if self.sf2_engine and sf2_path:
            sfid = self.sf2_engine.load_soundfont(sf2_path)
            if sfid is not None and track_name in self.sf2_engine.tracks:
                track = self.sf2_engine.tracks[track_name]
                track.soundfont_id = sfid
                track.soundfont_path = sf2_path
                self.sf2_engine.fs.program_select(track.channel, sfid, 0, 0)

    def _on_preset_change(self, track_name: str, bank: int, preset: int):
        if self.sf2_engine and track_name in self.sf2_engine.tracks:
            track = self.sf2_engine.tracks[track_name]
            if track.soundfont_id is not None:
                try:
                    self.sf2_engine.fs.program_select(
                        track.channel, track.soundfont_id, bank, preset
                    )
                    track.bank = bank
                    track.preset = preset
                except Exception:
                    pass
