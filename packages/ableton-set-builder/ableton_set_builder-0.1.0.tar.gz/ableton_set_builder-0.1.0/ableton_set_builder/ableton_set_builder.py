import xmltodict
import os
import gzip
from enum import Enum
from typing import List, Dict, Any
import io
from importlib import resources
from typing import Literal

_MonitoringTypes = Literal["off", "auto", "in"]

class ColorsDir(Enum):
    salmon = 0
    frank_orange = 1
    dirty_gold = 2
    lemonade = 3
    lime = 4
    highlighter_green = 5
    bianchi = 6
    turquiose = 7
    sky_blue = 8
    sapphire = 9
    periwinkle = 10
    orchid = 11
    magenta = 12
    white = 13
    fire_hydrant_red = 14
    tangerine = 15
    sand = 16
    sunshine_yellow = 17
    terminal_green = 18
    forest = 19
    tiffany_blue = 20
    cyan = 21
    cerulean = 22
    united_nations_blue = 23
    amethyst = 24
    iris = 25
    flamingo = 26
    aluminium = 27
    terracotta = 28
    light_salmon = 29
    whiskey = 30
    canary = 31
    primrose = 32
    wild_willow = 33
    dark_sea_green = 34
    honeydew = 35
    pale_turquiose = 36
    light_periwinkle = 37
    fog = 38
    dull_lavender = 39
    whisper = 40
    silver_chalice = 41
    dusty_pink = 42
    barley_corn = 43
    pale_oyster = 44
    dark_khaki = 45
    pistachio = 46
    dollar_bill = 47
    neptune = 48
    nepal = 49
    polo_blue = 50
    vista_blue = 51
    amethyst_smoke = 52
    lilac = 53
    turkish_rose = 54
    steel = 55
    medium_carmine = 56
    red_orche = 57
    coffee = 58
    durian_yellow = 59
    pomelo_green = 60
    apple = 61
    aquamarine = 62
    sea_blue = 63
    cosmic_cobalt = 64
    dark_sapphire = 65
    plump_purple = 66
    purpureus = 67
    fuchsia_rose = 68
    eclipse = 69

class AbletonSetBuilder:
    def __init__(self, template_path: str = None):
        if template_path is None:
            return
        self.doc = self.load_set(template_path)
        self.tracks = self.doc["Ableton"]["LiveSet"]["Tracks"]
        self.audio_tracks: List[Dict[str, Any]] = []
        self.midi_tracks: List[Dict[str, Any]] = []
        self.audio_tracks_first_clips: List[Dict[str, Any]] = []
        self.midi_tracks_first_clips: List[Dict[str, Any]] = []
        if "MasterTrack" in self.doc["Ableton"]["LiveSet"]:
            self.master_track = self.doc["Ableton"]["LiveSet"]["MasterTrack"]

        self.initialize_tracks()

    def load_set(self, path: str):
        if os.path.splitext(path)[1] == '.als':
            with gzip.open(path, 'rb') as f:
                return xmltodict.parse(f.read())
        elif os.path.splitext(path)[1] == '.xml':
            with open(path) as fd:
                return xmltodict.parse(fd.read())
        else:
            raise ValueError("Invalid file format. Please provide an .als or .xml file.")

    @staticmethod
    def import_template(template: str):
        with resources.files('ableton_set_builder.templates').joinpath(template).open('r') as fd:
            return xmltodict.parse(fd.read())

    def initialize_tracks(self):
        if not self.tracks:
            self.audio_tracks = []
            self.midi_tracks = []
            return
        # Handle audio tracks
        if "AudioTrack" in self.tracks:
            if isinstance(self.tracks["AudioTrack"], list):
                self.audio_tracks = self.tracks["AudioTrack"]
            else:
                self.audio_tracks = [self.tracks["AudioTrack"]]

        # Handle MIDI tracks
        if "MidiTrack" in self.tracks:
            if isinstance(self.tracks["MidiTrack"], list):
                self.midi_tracks = self.tracks["MidiTrack"]
            else:
                self.midi_tracks = [self.tracks["MidiTrack"]]

        # Get first clips for audio and MIDI tracks
        for audio_track in self.audio_tracks:
            audio_track_first_clip = audio_track["DeviceChain"]["MainSequencer"]["ClipSlotList"]["ClipSlot"]
            self.audio_tracks_first_clips.append(audio_track_first_clip)

        for midi_track in self.midi_tracks:
            midi_track_first_clip = midi_track["DeviceChain"]["MainSequencer"]["ClipSlotList"]["ClipSlot"]
            self.midi_tracks_first_clips.append(midi_track_first_clip)

    def create_audio_track(self, name: str, color: str, input: str = "1", output: str = "1", monitoring: _MonitoringTypes = "off", track_height: int = 68):
        monitoringEnum = {
            "off": 2,
            "auto": 1,
            "in": 0
        }
        def parse_io(io):
            if '/' in input:
                base = io.split('/')[0]
                base_num = int(base)
                io = f"S{int((base_num - 1) / 2)}"
            else:
                base_num = int(io)
                io = f"M{base_num - 1}"
            return io

        color = ColorsDir[color].value
        track = self.import_template('audio_track.xml')['AudioTrack']
        track["@Id"] = len(self.audio_tracks)
        track["Name"]["EffectiveName"]['@Value'] = name
        track["Name"]["UserName"]["@Value"] = name
        track["Color"]["@Value"] = color
        track["DeviceChain"]["AutomationLanes"]["AutomationLanes"]["AutomationLane"]["LaneHeight"]["@Value"] = track_height
        track["DeviceChain"]["MainSequencer"]["MonitoringEnum"]["@Value"] = monitoringEnum[monitoring]
        track["DeviceChain"]["AudioInputRouting"]["Target"]["@Value"] = f"AudioIn/External/{parse_io(input)}"
        track["DeviceChain"]["AudioInputRouting"]["UpperDisplayString"]["@Value"] = "Ext. In"
        track["DeviceChain"]["AudioInputRouting"]["LowerDisplayString"]["@Value"] = input
        track["DeviceChain"]["AudioOutputRouting"]["Target"]["@Value"] = f"AudioOut/External/{parse_io(output)}"
        track["DeviceChain"]["AudioOutputRouting"]["UpperDisplayString"]["@Value"] = "Ext. Out"
        track["DeviceChain"]["AudioOutputRouting"]["LowerDisplayString"]["@Value"] = output
        self.audio_tracks.append(track)

    def create_clip_slot(self, id: int, lom_id: int, has_stop: str, need_refreeze: str) -> Dict[str, Any]:
        return {
            "@Id": str(id),
            "LomId": {
                "@Value": str(lom_id)
            },
            "ClipSlot": {
                "Value": None
            },
            "HasStop": {
                "@Value": has_stop
            },
            "NeedRefreeze": {
                "@Value": need_refreeze
            }
        }

    def create_scene(self, id: int, name: str, annotation: str, color: int, tempo: int, time_signature_id: int) -> Dict[str, Any]:
        scene = {
            "@Id": str(id),
            "FollowAction": {
                "FollowTime": {"@Value": "4"},
                "IsLinked": {"@Value": "true"},
                "LoopIterations": {"@Value": "1"},
                "FollowActionA": {"@Value": "4"},
                "FollowActionB": {"@Value": "0"},
                "FollowChanceA": {"@Value": "100"},
                "FollowChanceB": {"@Value": "0"},
                "JumpIndexA": {"@Value": "1"},
                "JumpIndexB": {"@Value": "1"},
                "FollowActionEnabled": {"@Value": "false"}
            },
            "Name": {"@Value": name},
            "Annotation": {"@Value": annotation},
            "Color": {"@Value": str(color)},
            "Tempo": {"@Value": str(tempo)},
            "IsTempoEnabled": {"@Value": "true"},
            "TimeSignatureId": {"@Value": str(time_signature_id)},
            "IsTimeSignatureEnabled": {"@Value": "true"},
            "LomId": {"@Value": "0"},
            "ClipSlotsListWrapper": {"@LomId": "0"}
        }
        return scene

    def clear_track(self, track: Dict[str, Any]):
        track["DeviceChain"]["MainSequencer"]["ClipSlotList"]["ClipSlot"] = []
        track["DeviceChain"]["FreezeSequencer"]["ClipSlotList"]["ClipSlot"] = []

    def add_clip_to_track(self, track: Dict[str, Any], clip: Dict[str, Any]):
        # check if clip is not a list:
        if not isinstance(track["DeviceChain"]["MainSequencer"]["ClipSlotList"]["ClipSlot"], list):
            track["DeviceChain"]["MainSequencer"]["ClipSlotList"]["ClipSlot"] = [track["DeviceChain"]["MainSequencer"]["ClipSlotList"]["ClipSlot"]]

        if not isinstance(track["DeviceChain"]["FreezeSequencer"]["ClipSlotList"]["ClipSlot"], list):
            track["DeviceChain"]["FreezeSequencer"]["ClipSlotList"]["ClipSlot"] = [track["DeviceChain"]["FreezeSequencer"]["ClipSlotList"]["ClipSlot"]]
        track["DeviceChain"]["MainSequencer"]["ClipSlotList"]["ClipSlot"].append(clip)
        track["DeviceChain"]["FreezeSequencer"]["ClipSlotList"]["ClipSlot"].append(clip)

    def add_scene(self, id: int, name: str, annotation: str = "", color: int = -1, tempo: int = 120, time_signature_id: int = 201):
        new_scene = self.create_scene(id, name, annotation, color, tempo, time_signature_id)
        self.doc["Ableton"]["LiveSet"]["Scenes"]["Scene"].append(new_scene)

        # Add clip slots to tracks for this scene
        for track in self.audio_tracks + self.midi_tracks:
            self.add_clip_to_track(track, self.create_clip_slot(id, 0, "true", "true"))

    def add_template_scene(self, scene_id: int, scene_name: str, color: int = -1, tempo: int = 120):
        # Create a new scene
        new_scene = self.create_scene(scene_id, scene_name, "", color, tempo, 201)

        # Add the scene to the scenes list
        if "Scene" not in self.doc["Ableton"]["LiveSet"]["Scenes"]:
            self.doc["Ableton"]["LiveSet"]["Scenes"]["Scene"] = []
        # check if scene is not a list:
        if not isinstance(self.doc["Ableton"]["LiveSet"]["Scenes"]["Scene"], list):
            self.doc["Ableton"]["LiveSet"]["Scenes"]["Scene"] = [self.doc["Ableton"]["LiveSet"]["Scenes"]["Scene"]]

        self.doc["Ableton"]["LiveSet"]["Scenes"]["Scene"].append(new_scene)

        # Add the first clips of the audio and midi tracks to the scene
        for i, audio_track_first_clip in enumerate(self.audio_tracks_first_clips):
            new_clip = audio_track_first_clip.copy()
            new_clip["@Id"] = str(scene_id)
            self.add_clip_to_track(self.audio_tracks[i], new_clip)

        for i, midi_track_first_clip in enumerate(self.midi_tracks_first_clips):
            new_clip = midi_track_first_clip.copy()
            new_clip["@Id"] = str(scene_id)
            self.add_clip_to_track(self.midi_tracks[i], new_clip)

    def clearScenes(self):
        self.doc["Ableton"]["LiveSet"]["Scenes"]["Scene"] = []
        # self.clear_track(self.master_track)

        for audio_track in self.audio_tracks:
            self.clear_track(audio_track)
        for midi_track in self.midi_tracks:
            self.clear_track(midi_track)

    def import_set(self, import_path: str):
        doc_import = self.load_set(import_path)
        return

    def assemble(self):
        self.doc["Ableton"]["LiveSet"]["Tracks"] = {}
        self.doc["Ableton"]["LiveSet"]["Tracks"]["AudioTrack"] = self.audio_tracks
        return self.doc

    def to_xml(self):
        assemble = self.assemble()
        return xmltodict.unparse(assemble, pretty=True)

    def build_uncompressed_als(self, output_path: str):
        path = os.path.splitext(output_path)[0] + '.als'
        with open(path, "w") as f:
            f.write(self.to_xml())    

    def build_als(self, output_path: str):
        path = os.path.splitext(output_path)[0] + ".als"
        with gzip.open(path, "wb") as gz:
            gz.write(self.to_xml().encode('utf-8'))
