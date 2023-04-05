from BlueStar import *
import json, requests, os
import tkinter as tk
from tkinter import filedialog

### Tk window ###
root = tk.Tk()
root.withdraw()  # hide the window
root.call('wm', 'attributes', '.', '-topmost', '1')  # put the window on always top


def fileDialog(title: str, type: str) -> None:
    path = filedialog.askopenfilename(title=title,
                                      filetypes=((f"{type.upper()} files", f"*.{type.lower()}"), ("All Files", ".*")))
    if not path: raise FileNotFoundError("Select a file!")
    return path


def main():
    Moves: list = []
    KinectMoves: list = []
    MainJson: dict = {}

    print("Welcome to Eliott's Bluestar tools!")
    choice = input(
        "What do you want to do?\n"
        "[1] Use the jsons from the folder\n"
        "[2] Select them\n"
        "[3] Use from jdn servers\n"
        "Select an option: ")

    if choice == "1":
        MainJson = openJson("main.json")
        for i in range(4):
            Moves.append(openJson(f"moves{i}.json"))

    elif choice == "2":
        print("Open the main json")
        MainJson = openJson(fileDialog("Select the Main JSON", "json"))
        print("Now select the moves")
        CoachCount = CoachCountResolver(MainJson.get("NumCoach", 1))
        for coach in range(CoachCount):
            Moves.append(openJson(fileDialog(f"Select the Moves{coach} JSON", "json")))
        if input("Do you want to select KinectMoves (y/n): ") == "y":
            for coach in range(CoachCount):
                KinectMoves.append(openJson(fileDialog(f"Select the KinectMoves{coach} JSON", "json")))

    elif choice == "3":
        mapname = input("What's the CodeName of the song? ")
        MainJson = loadJson(requests.get(
            f"http://jdnowweb-s.cdn.ubi.com/uat/release_tu2/20150928_1740/songs/{mapname}/{mapname}.json").text)
        MainJson["isJDN"] = MainJson.get("OriginalJDVersion", 0) < 5
        CoachCount = CoachCountResolver(MainJson.get("NumCoach", 1))
        for coach in range(CoachCount):
            Moves.append(loadJson(requests.get(
                f"http://jdnowweb-s.cdn.ubi.com/uat/release_tu2/20150928_1740/songs/{mapname}/data/moves/{mapname}_moves{coach}.json").text))

    print(MainJson["Title"] + " by " + MainJson["Artist"] + " loaded successfully!")

    if not MainJson.get("isJDN") and MainJson.get("OriginalJDVersion", 0) < 5:
        MainJson["isJDN"] = input("Are this tmls from jdn? (y/n): ") == "y"

    if not MainJson.get("goldEffects", None):
        MainJson["autoGoldEffects"] = {"1": "Pictos", "2": "Moves"}[
            input("What method you want to use for the Automatic Gold Moves?\n[1] Pictos\n[2] Moves\n: ")]

    song = Song(**MainJson, moves=Moves, kinectMoves=KinectMoves)
    song.makeUAF()

    ### Create folders ###
    os.makedirs(f"output/{MainJson['MapName']}/timeline", exist_ok=True)
    os.makedirs(f"output/{MainJson['MapName']}/audio", exist_ok=True)
    os.makedirs(f"output/{MainJson['MapName']}/cinematics", exist_ok=True)

    mapname = MainJson['MapName'].lower()

    ### Save the UAF ###
    json.dump(song.tml_dance,
              open(f"output/{MainJson['MapName']}/timeline/{mapname}_tml_dance.dtape.ckd", "w", encoding="utf-8"),
              ensure_ascii=False)
    json.dump(song.tml_karaoke,
              open(f"output/{MainJson['MapName']}/timeline/{mapname}_tml_karaoke.ktape.ckd", "w", encoding="utf-8"),
              ensure_ascii=False)
    json.dump(song.mainsequence,
              open(f"output/{MainJson['MapName']}/cinematics/{mapname}_mainsequence.tape.ckd", "w", encoding="utf-8"),
              ensure_ascii=False)
    json.dump(song.musictrack,
              open(f"output/{MainJson['MapName']}/audio/{mapname}_musictrack.tpl.ckd", "w", encoding="utf-8"),
              ensure_ascii=False)
    for index, amb in enumerate(song.ambtpls):
        os.makedirs(f"output/{MainJson['MapName']}/audio/amb", exist_ok=True)
        json.dump(amb,
                  open(f"output/{MainJson['MapName']}/audio/amb/amb_{mapname}_{index}.tpl.ckd", "w", encoding="utf-8"),
                  ensure_ascii=False)
    json.dump(song.songdesc, open(f"output/{MainJson['MapName']}/songdesc.tpl.ckd", "w", encoding="utf-8"),
              ensure_ascii=False)


if __name__ == "__main__":
    main()
