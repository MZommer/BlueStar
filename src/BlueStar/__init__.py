from .__utils__ import *
import random
import numpy as np

"""
    TODO: Mainsequence functions
"""


class Song:
    def __init__(self, MapName, beats, JDVersion=2022, OriginalJDVersion=2022, Difficulty="Normal", LocaleID=0xffffffff,
                 Artist="TBA", Title="TBA", Credits="CREDITS STRING TO BE FILLED", DefaultColors=None,
                 lyricsColor="FF0000", videoOffset=0, lyrics=[], pictos=[], AudioPreview={}, moves=[], kinectMoves=[],
                 autodances=[], AmbientSounds=[], HideUserInterface=[], isJDN=False, endBeat=None, goldEffects=None,
                 autoGoldEffects="Moves", hideUserInterface=None, **kwargs):
        self.MapName = MapName
        self.mapname = MapName.lower()
        self.isJDN = isJDN
        self.JDVersion = JDVersion
        self.OriginalJDVersion = OriginalJDVersion
        self.Difficulty = Difficulty
        self.LocaleID = LocaleID
        self.Credits = Credits
        self.Artist = Artist
        self.Title = Title
        self.DefaultColors = DefaultColors
        self.lyricsColor = lyricsColor
        self.videoOffset = videoOffset
        self.lyrics = lyrics
        self.pictos = pictos
        self.AudioPreview = AudioPreview
        self.endBeat = endBeat
        self.moves = moves
        self.kinectMoves = kinectMoves
        self.HideUserInterface = HideUserInterface
        self.autodances = autodances
        self.AmbientSounds = AmbientSounds
        self.beats = sorted(list(set(beats)))
        if self.beats[0] != 0:
            self.beats.insert(0, 0)
        self.units = [0]
        self.__makeUnitArray()
        self.__goldEffectsArr = []
        self.autoGoldEffects = autoGoldEffects
        self.goldEffects = goldEffects

        self.tml_dance = {
            "__class": "Tape",
            "Clips": [],
            "TapeClock": 0,
            "TapeBarCount": 1,
            "FreeResourcesAfterPlay": 0,
            "MapName": self.MapName
        }
        self.tml_karaoke = {
            "__class": "Tape",
            "Clips": [],
            "TapeClock": 0,
            "TapeBarCount": 1,
            "FreeResourcesAfterPlay": 0,
            "MapName": self.MapName
        }
        self.mainsequence = {
            "__class": "Tape",
            "Clips": [],
            "TapeClock": 0,
            "TapeBarCount": 1,
            "FreeResourcesAfterPlay": 0,
            "MapName": self.MapName
        }
        self.autodance = {
            "__class": "Actor_Template",
            "WIP": 0,
            "LOWUPDATE": 0,
            "UPDATE_LAYER": 0,
            "PROCEDURAL": 0,
            "STARTPAUSED": 0,
            "FORCEISENVIRONMENT": 0,
            "COMPONENTS": []
        }
        self.ambtpls = []
        self.__makeMusicTrack()
        self.__makeSongDesc()

    def makeUAF(self):
        self.__makeMotionClips()
        self.__makePictogramClips()
        self.__makeGoldEffectClips()
        self.tml_dance["Clips"] = sorted(self.tml_dance["Clips"], key=lambda d: d['StartTime'])
        self.__makeKaraokeClips()
        self.tml_karaoke["Clips"] = sorted(self.tml_karaoke["Clips"], key=lambda d: d['StartTime'])
        self.__makeMainSequence()

    def __makeUnitArray(self):
        units = [0]
        for index, beat in enumerate(self.beats):
            if beat == 0:
                continue
            delay = (beat - self.beats[index - 1])
            unit = delay / 24
            for _ in range(int(delay / unit)):
                units.append(units[-1] + unit)
        self.units = np.asarray(units, dtype=np.int32)

    def getMarker(self, time):
        marker = getClosestIndex(self.units, np.abs(time)).item()
        return marker * -1 if time < 0 else marker

    def makeTime(self, time, duration):
        startTime = self.getMarker(time)
        if self.isJDN:
            duration = self.getMarker(duration)
        else:
            endTime = self.getMarker(time + duration)
            duration = endTime - startTime
        return startTime, duration

    def fixLyrics(self):
        """
            As far as I know this problem was caused by the way that this times work so this is not necessary anymore
            Still I let the function here
        """
        for index, item in enumerate(self.lyrics):
            if index >= len(self.lyrics) - 1:
                continue
            next_item = self.lyrics[index + 1]
            if item['time'] + item['duration'] > next_item['time']:
                item['duration'] -= item['time'] + item['duration'] - next_item['time'] + 1

    def __makeMarkers(self):
        """
            Bad and lazy way to do the markers
            The proper way would be using the actual bpm and using the real difference per beat and not the rounded one,
            but when the bpm of a chunk of a song, is a float, I can't get it.
            If you are reading this and you have an idea to implement this hmu!
        """
        self.markers = [round(beat * 48) for beat in self.beats]

    def __colorsResolver(self):
        if self.DefaultColors is None or not self.DefaultColors.get("songcolor_2a"):
            # Checks if DefaultColors is none or if it doesn't have the menu colors
            return {  # Placeholder colors
                "songcolor_2a": [1, 0.666667, 0.666667, 0.666667],
                "lyrics": hex2perc(self.lyricsColor),
                "theme": [1, 1, 1, 1],
                "songcolor_1a": [1, 0.266667, 0.266667, 0.266667],
                "songcolor_2b": [1, 0.466667, 0.466667, 0.466667],
                "songcolor_1b": [1, 0.066667, 0.066667, 0.066667]
            }
        else:
            return {
                "songcolor_2a": hex2perc(self.DefaultColors["songcolor_2a"]),
                "lyrics": hex2perc(self.DefaultColors["lyrics"]),
                "theme": [1, 1, 1, 1],
                "songcolor_1a": hex2perc(self.DefaultColors["songcolor_1a"]),
                "songcolor_2b": hex2perc(self.DefaultColors["songcolor_2b"]),
                "songcolor_1b": hex2perc(self.DefaultColors["songcolor_1b"])
            }

    def __makeSongDesc(self):
        Difficulty_ENUM = {
            -1: "SongDifficulty_NA",
            0: "SongDifficulty_Easy",
            1: "SongDifficulty_Normal",
            2: "SongDifficulty_Hard",
            3: "SongDifficulty_Extreme",
            4: "SongDifficulty_Max"
        }
        DifficultyResolver = {
            None: -1,
            "Easy": 0,
            "Normal": 1,
            "Hard": 2,
            "Exteme": 3,
            "Max": 4
        }
        Difficulty = self.Difficulty if isinstance(self.Difficulty, int) else DifficultyResolver[self.Difficulty]
        self.songdesc = {
            "__class": "Actor_Template",
            "WIP": 0,
            "LOWUPDATE": 0,
            "UPDATE_LAYER": 0,
            "PROCEDURAL": 0,
            "STARTPAUSED": 0,
            "FORCEISENVIRONMENT": 0,
            "COMPONENTS": [{
                "__class": "JD_SongDescTemplate",
                "MapName": self.MapName,
                "JDVersion": self.JDVersion if self.JDVersion != 0 else self.OriginalJDVersion,
                "OriginalJDVersion": self.OriginalJDVersion,
                "Artist": self.Artist,
                "DancerName": "Unknown Dancer",
                "Title": self.Title,
                "Credits": self.Credits,
                "PhoneImages": {
                    f"coach{i + 1}": f"world/maps/{self.mapname}/menuart/textures/{self.mapname}_coach_{i + 1}_phone.png"
                    for i in range(len(self.moves))
                },
                "NumCoach": len(self.moves),
                "MainCoach": -1,
                "Difficulty": Difficulty,
                "SweatDifficulty": Difficulty,
                "backgroundType": 0,
                "LyricsType": 0,
                "Tags": ["main", f"jd{self.OriginalJDVersion}", f"main_{self.OriginalJDVersion}"],
                "Status": 3,
                "LocaleID": self.LocaleID,
                "MojoValue": 0,
                "CountInProgression": 1,
                "DefaultColors": self.__colorsResolver(),
                "VideoPreviewPath": ""
            }
            ]
        }
        self.songdesc["COMPONENTS"][0]["PhoneImages"]["cover"] \
            = f"world/maps/{self.mapname}/menuart/textures/{self.mapname}_cover_phone.jpg"
        if self.MapName.lower().endswith("alt"):
            self.songdesc["COMPONENTS"][0]["RelatedAlbums"] = [self.MapName[:-3]]

    def __makeMusicTrack(self):
        self.__makeMarkers()
        if self.endBeat is None:
            self.endBeat = len(self.markers)
        if self.AudioPreview.get("prelobby", False):  # JDN
            previewLoopStart = self.AudioPreview["prelobby"]["startbeat"]
            previewEntry = previewLoopStart - 1
            previewLoopEnd = self.AudioPreview["prelobby"].get("endbeat", self.endBeat)
        elif self.AudioPreview.get("loopStart", False):  # JDVS
            previewEntry = self.beats.index(getClosestValue(self.beats, self.AudioPreview["entry"] * 1000))
            previewLoopStart = previewEntry + self.beats.index(getClosestValue(self.beats, self.AudioPreview[
                "loopStart"] * 1000))
            previewLoopEnd = self.beats.index(getClosestValue(self.beats, self.AudioPreview["loopEnd"] * 1000))
        else:
            previewEntry = round(self.endBeat / 2)
            previewLoopStart = round(self.endBeat / 2)
            previewLoopEnd = self.endBeat
        self.musictrack = {
            "__class": "Actor_Template",
            "WIP": 0,
            "LOWUPDATE": 0,
            "UPDATE_LAYER": 0,
            "PROCEDURAL": 0,
            "STARTPAUSED": 0,
            "FORCEISENVIRONMENT": 0,
            "COMPONENTS": [{
                "__class": "MusicTrackComponent_Template",
                "trackData": {
                    "__class": "MusicTrackData",
                    "structure": {
                        "__class": "MusicTrackStructure",
                        "markers": self.markers,
                        "signatures": [{
                            "__class": "MusicSignature",
                            "marker": 0,
                            "beats": 4
                        }
                        ],
                        "sections": [
                            {
                                "__class": "MusicSection",
                                "marker": i * 16,
                                "sectionType": 0,
                                "comment": ""
                            } for i in range(len(self.markers) // 16)
                        ],
                        "startBeat": 0,
                        "endBeat": self.endBeat,
                        "fadeStartBeat": 0,
                        "useFadeStartBeat": False,
                        "fadeEndBeat": 0,
                        "useFadeEndBeat": False,
                        "videoStartTime": 0,
                        "previewEntry": previewEntry,
                        "previewLoopStart": previewLoopStart,
                        "previewLoopEnd": previewLoopEnd,
                        "volume": 0,
                        "fadeInDuration": 0,
                        "fadeInType": 0,
                        "fadeOutDuration": 0,
                        "fadeOutType": 0
                    },
                    "path": f"world/maps/{self.mapname}/audio/{self.mapname}.wav",
                    "url": f"jmcs://jd-contents/{self.MapName}/{self.MapName}.ogg"
                }
            }
            ]
        }

    def __makeMotionClips(self):
        clips = []
        pictoTimes = [picto["time"] for picto in self.pictos]
        for moveType, arr in enumerate((self.moves, self.kinectMoves)):
            for index, moves in enumerate(arr):
                for move in moves:
                    StartTime, Duration = self.makeTime(move["time"], move["duration"])
                    GoldMove = move.get("goldMove", 0)
                    clips.append({
                        "__class": "MotionClip",
                        "Id": random.randint(0, 0xffffffff),
                        "TrackId": random.randint(0, 0xffffffff),
                        "IsActive": 1,
                        "StartTime": StartTime,
                        "Duration": Duration,
                        "ClassifierPath": f"world/maps/{self.mapname}/timeline/moves/{move['name']}.{'msm' if moveType == 0 else 'gesture'}",
                        "GoldMove": GoldMove,
                        "CoachId": index,
                        "MoveType": moveType,
                        "Color": [1, 1, 0, 0],
                        "MotionPlatformSpecifics": {
                            "X360": {
                                "__class": "MotionPlatformSpecific",
                                "ScoreScale": 1,
                                "ScoreSmoothing": 0,
                                "ScoringMode": 0
                            },
                            "ORBIS": {
                                "__class": "MotionPlatformSpecific",
                                "ScoreScale": 1,
                                "ScoreSmoothing": 0,
                                "ScoringMode": 0
                            },
                            "DURANGO": {
                                "__class": "MotionPlatformSpecific",
                                "ScoreScale": 1,
                                "ScoreSmoothing": 0,
                                "ScoringMode": 0
                            }
                        }
                    })
                    if GoldMove == 1 and self.autoGoldEffects is not None:
                        if self.autoGoldEffects == "Moves":
                            if StartTime + Duration not in self.__goldEffectsArr:
                                self.__goldEffectsArr.append(move["time"] + move["duration"])
                        elif self.autoGoldEffects == "Pictos":
                            time = getClosestValue(pictoTimes, move["time"])
                            if time not in self.__goldEffectsArr:
                                self.__goldEffectsArr.append(time)

        self.tml_dance["Clips"].extend(clips)

    def __makeGoldEffectClips(self):
        clips = []
        if self.goldEffects is None:
            self.goldEffects = self.__goldEffectsArr
        for time in self.goldEffects:
            if not isinstance(time, int):
                time = time["time"]
            StartTime, Duration = self.makeTime(time, 0)
            clips.append({
                "__class": "GoldEffectClip",
                "Id": random.randint(0, 0xffffffff),
                "TrackId": random.randint(0, 0xffffffff),
                "IsActive": 1,
                "StartTime": StartTime,
                "Duration": 24,
                "EffectType": 1
            })
        self.tml_dance["Clips"].extend(clips)

    def __makePictogramClips(self):
        clips = []
        for picto in self.pictos:
            StartTime, Duration = self.makeTime(picto["time"], picto["duration"])
            clips.append({
                "__class": "PictogramClip",
                "Id": random.randint(0, 0xffffffff),
                "TrackId": random.randint(0, 0xffffffff),
                "IsActive": 1,
                "StartTime": StartTime,
                "Duration": Duration,
                "PictoPath": f"world/maps/{self.mapname}/timeline/pictos/{picto['name']}.png",
                "CoachCount": 4294967295
            })
        self.tml_dance["Clips"].extend(clips)

    def __makeKaraokeClips(self):
        clips = []
        for lyric in self.lyrics:
            StartTime, Duration = self.makeTime(lyric["time"], lyric["duration"])
            clips.append({
                "__class": "KaraokeClip",
                "Id": random.randint(0, 0xffffffff),
                "TrackId": random.randint(0, 0xffffffff),
                "IsActive": 1,
                "StartTime": StartTime,
                "Duration": Duration,
                "Pitch": 311.126984,
                "Lyrics": lyric["text"],
                "IsEndOfLine": lyric.get('isLineEnding', 0),
                "ContentType": 0,
                "StartTimeTolerance": 4,
                "EndTimeTolerance": 4,
                "SemitoneTolerance": 5
            })
        self.tml_karaoke["Clips"].extend(clips)

    def __makeMainSequence(self):
        clips = []
        for clip in self.HideUserInterface:
            StartTime, Duration = self.makeTime(clip["time"], clip["duration"])
            clips.append({
                "__class": "HideUserInterfaceClip",
                "Id": random.randint(0, 0xffffffff),
                "TrackId": random.randint(0, 0xffffffff),
                "IsActive": 1,
                "StartTime": StartTime,
                "Duration": Duration,
                "EventType": 18,
                "CustomParam": ""
            })
        for index, clip in enumerate(self.AmbientSounds):
            StartTime, Duration = self.makeTime(clip["time"], clip["duration"])
            clips.append({
                "__class": "SoundSetClip",
                "Id": random.randint(0, 0xffffffff),
                "TrackId": random.randint(0, 0xffffffff),
                "IsActive": 1,
                "StartTime": StartTime,
                "Duration": Duration,
                "SoundSetPath": f"world/maps/{self.mapname}/audio/amb/amb_{self.mapname}_{index}.tpl",
                "SoundChannel": 0,
                "StartOffset": 0,
                "StopsOnEnd": clip["StopsOnEnd"],
                "AccountedForDuration": 0
            })
            self.ambtpls.append({
                "COMPONENTS": [{
                    "__class": "SoundComponent_Template",
                    "soundList": [{
                        "__class": "SoundDescriptor_Template",
                        "category": "amb",
                        "files": [f"world/maps/{self.mapname}/audio/amb/amb_{self.mapname}_{index}.tpl"],
                        "limitCategory": "",
                        "limitMode": 0,
                        "maxInstances": 4294967295,
                        "name": f"amb_{self.mapname}_{clip['name'].lower()}",
                        "outDevices": 4294967295,
                        "params": {
                            "__class": "SoundParams",
                            "delay": 0,
                            "fadeInTime": 0,
                            "fadeOutTime": 0,
                            "filterFrequency": 0,
                            "filterType": 2,
                            "loop": 0,
                            "pitch": 1,
                            "playMode": 1,
                            "playModeInput": "",
                            "randomDelay": 0,
                            "randomPitchMax": 1,
                            "randomPitchMin": 1,
                            "randomVolMax": 0,
                            "randomVolMin": 0,
                            "transitionSampleOffset": 0
                        },
                        "pauseInsensitiveFlags": 0,
                        "serialPlayingMode": 0,
                        "serialStoppingMode": 0,
                        "soundPlayAfterdestroy": 0,
                        "volume": 0
                    }
                    ]
                }
                ],
                "FORCEISENVIRONMENT": 0,
                "LOWUPDATE": 0,
                "PROCEDURAL": 0,
                "STARTPAUSED": 0,
                "UPDATE_LAYER": 0,
                "WIP": 0,
                "__class": "Actor_Template"
            })
        self.mainsequence["Clips"].extend(clips)
