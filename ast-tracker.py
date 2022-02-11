print("Starting...")

from numpy import linspace, arange, pi, sin, zeros, int16, tan, arctan, arcsin
import wave, os, random, time, requests, sys, json
from numpy import random as nprandom
from numpy import abs as npabs
from numpy import max as npmax
from numpy import min as npmin

version = "v1.4.3"
title = "Ast-Tracker " + version
api_git_link = "https://api.github.com/repos/mrtnvgr/ast-tracker/releases/latest"
exe_download_link = "https://github.com/mrtnvgr/ast-tracker/releases/latest/download/ast-tracker.exe"
src_download_link = "https://raw.githubusercontent.com/mrtnvgr/ast-tracker/main/ast-tracker.py"

def download(url, filename):
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')
        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50-done)))
                sys.stdout.flush()
    sys.stdout.write('\n')

def clear():
    if os.name=='nt':
        os.system('cls')
    else:
        os.system("clear")
clear()

def wait():
    if os.name=='nt':
        os.system("pause")
    else:
        os.system('read -n1 -r -p "Press any key to continue..."')

def delete(file):
    if os.name=='nt':
        os.system("del /q /p " + file)
    else:
        os.system("rm " + file)

def settings_func(mode):
    global settings
    try:
        settings = json.loads(open("settings.json", "r").read())
    except FileNotFoundError:
        settings = {
            'sample_folder': 'default'
        }
        json.dump(settings, open("settings.json", "w"), indent=4)
    if mode=="r":
        settings = json.loads(open("settings.json", "r").read())
        # required settings check
        for sett in ['sample_folder']:
            if sett in settings:
                pass
            else:
                print("Setting not found: " + sett)
                print("Please check your settings file! Default value will be used.")
                if sett=="sample_folder":
                    settings['sample_folder'] = 'default'
                wait()
    elif mode=="s":
        json.dump(settings, open("settings.json", "w"), indent=4)
settings_func("r")

def sawtooth_gen(f_c, duration_s, amp): return int16(amp * arctan(tan(2.0 * pi * f_c * arange(44100 * duration_s)/44100))*32768)

def sin_gen(f_c, duration_s, amp): return int16(amp * sin(2.0 * pi * f_c * arange(44100 * duration_s)/44100)*32768)

def triangle_gen(f_c, duration_s, amp): return int16(amp * arcsin(sin(2.0 * pi * f_c * arange(44100 * duration_s)/44100))*32768)

def noise_gen(duration_s, amp):
    pure = linspace(0, 1, int(duration_s * 44100))
    noise = nprandom.normal(0, 1, pure.shape)
    return int16((pure + noise)*amp * 32768)

# guitar_gen(990.0, 5.0, 1)
def guitar_gen(f_c, duration_s, amp):
    noise = nprandom.uniform(-1, 1, int(44100/f_c))
    samples = zeros(int(44100*duration_s))
    for i in range(len(noise)):
        samples[i] = noise[i]
    for i in range(len(noise), len(samples)):
        samples[i] = (samples[i-len(noise)]+samples[i-len(noise)-1])/2
    samples = samples / npmax(npabs(samples))
    waveform_quiet = samples * amp
    return int16(waveform_quiet * 32768)

def pitched_nse_gen(f_c, duration_s, amp):
    noise = nprandom.uniform(-1, 1, int(44100/f_c))
    samples = zeros(int(44100*duration_s))
    for i in range(len(noise)):
        samples[i] = noise[i]
    for i in range(len(noise), len(samples)):
        samples[i] = (samples[i-len(noise)])
    samples = samples / npmax(npabs(samples))
    waveform_quiet = samples * amp
    return int16(waveform_quiet * 32768) # NOTE: pitched noise function (maybe temporary)

def sample_gen(sample_name):
    try:
        obj = wave.open(settings['sample_folder'] + "\\" + sample_name + ".wav", 'r')
        sample_data = obj.readframes(obj.getnframes())
        obj.close()
        return(sample_data)
    except FileNotFoundError:
        print("Sample doesnt exist")
        wait()
        return False

# write("example.wav", sawtooth_gen(...))
def write(filename, data):
    global prev_data
    try:
        obj = wave.open(filename,'r')
        prev_data = obj.readframes(obj.getnframes())
        obj.close()
    except FileNotFoundError:
        pass # print("Not found.")
    obj = wave.open(filename,'w')
    obj.setnchannels(2)
    obj.setsampwidth(2)
    obj.setframerate(44100)
    if prev_data!="":
        obj.writeframesraw( prev_data )
    obj.writeframesraw( data )
    obj.close()

def readfile(filename, type):
    if type=="wav":
        try:
            obj = wave.open(filename,'r')
            sound = obj.readframes(obj.getnframes())
            obj.close()
            return sound
        except FileNotFoundError:
            return False
    elif type=="ast":
        try:
            data = open(filename, "r").read()
            if "[ast v1]" in data: # if first ast format
                data = data.replace("[ast v1]\n", "") # just removing header
                return [data, "v1"]
            elif "[ast v1.1]" in data: # if 1.1 ast format
                data = data.replace("[ast v1.1]\n", "") # removing header
                c_name = data.split("[name: ")[1].split("]")[0] # getting name
                c_desc = data.split("[description: ")[1].split("]")[0] # getting description
                c_artist = data.split("[artist: ")[1].split("]")[0] # getting artist
                data = data.replace("[name: " + c_name + "]\n[description: " + c_desc + "]\n[artist: " + c_artist + "]\n", "") # getting raw data
                return [data, "v1.1", c_name, c_desc, c_artist]
            else: # v0 format (only song data)
                return [data, "v0"]
        except FileNotFoundError:
            return False

def writefile(filedata, filename, type):
    if type=="ast":
        #ttlfiledata = "[ast v1]\n" + filedata (v1 parser)
        ttlfiledata = "[ast v1.1]\n" + "[name: " + c_name + "]\n[description: " + c_desc + "]\n" + "[artist: " + c_artist + "]\n" + filedata # v1.1 parser
        open(filename, "w").write(ttlfiledata)

def fetchsngdata(filename):
    global c_name,c_desc,c_artist
    data = readfile(filename, "ast")
    if data[1]=="v1.1":
        c_name = data[2]
        c_desc = data[3]
        c_artist = data[4]

while True:
    clear()
    print(title)
    print(" ")
    print(" 1) .AST editor")
    print(" 2) .AST tools")
    print(" 3) .WAV tools")
    print(" ")
    print(" s) Settings")
    print(" h) Help")
    print(" a) About")
    print(" u) Update")
    print(" e) Exit")
    print(" ")
    mn_ch = input(": ")
    if mn_ch=="1":
        clear()
        print(title)
        print(" .AST editor")
        print(" ")
        file = input("File (only name): ")
        if file=="":
            continue
        oldstuff = ""
        fastmodeActive = False
        view_mode = "ALL"
        view_mode_lines = 0
        while True:
            rawfiledata = readfile(file + ".ast", "ast")
            if rawfiledata==False:
                clear()
                c_name = input("Song name: ")
                c_artist = input("Song artist: ")
                c_desc = input("Song description: ")
                rawfiledata = ["", "v1.1", c_name, c_desc, c_artist]
            clear()
            print(title)
            print(" .AST editor ", end="")
            if view_mode=="ALL":
                print("[VIEW MODE: " + view_mode + "]")
            elif "FT" in view_mode:
                lines_list = view_mode.replace("FT", "").split("-")
                print("[VIEW MODE: FROM " + lines_list[0] + " TO " + lines_list[1] + " LINE")
            else:
                print("[VIEW MODE: " + view_mode + " " + str(view_mode_lines) + " LINES]")
            if rawfiledata[1]=="v0" or rawfiledata=="v1":
                print(" Song: [AST version: " + rawfiledata[1])
                print("        File: " + file + ".ast]")
            elif rawfiledata[1]=="v1.1":
                c_name = rawfiledata[2]
                c_artist = rawfiledata[4]
                c_desc = rawfiledata[3]
                print(" Song: [AST version: " + rawfiledata[1])
                print("        Name: " + c_name)
                print("        Artist: " + c_artist)
                print("        Description: " + c_desc + "]")
                print(" Change song data - 'sd'")
            print(" ")
            oldstuff = rawfiledata[0]
            print(" ")
            print("[№] [NOTE] [LENGTH] [INST] [AMP]")
            oldlines = oldstuff.split("!")
            if oldlines[0]=="":
                oldlines.pop(0) # [0] empty string bug fix
            n = -1
            if view_mode=="ALL":
                for i in oldlines:
                    n = n + 1
                    print("[" + str(n) + "] " + i)
            elif view_mode=="FIRST":
                for i in oldlines[:view_mode_lines]:
                    n = n + 1
                    print("[" + str(n) + "] " + i)
            elif view_mode=="LAST":
                n = len(oldlines)-len(oldlines[-view_mode_lines:])-1
                for i in oldlines[-view_mode_lines:]:
                    n = n + 1
                    print("[" + str(n) + "] " + i)
            elif "FT" in view_mode:
                lines_list = view_mode.replace("FT", "").split("-")
                n = int(lines_list[0])-1
                for i in oldlines[int(lines_list[0]):int(lines_list[1])+1]:
                    n = n + 1
                    print("[" + str(n) + "] " + i)
            print(" ")
            print(" Go to menu - 'm' ")
            print(" Exit - 'exit'")
            print(" Delete last line - 'u' ")
            print(" Repeat last line - 'r' ")
            print(" Edit specific line - 'e' + number")
            print(" Delete specific line - 'd' + number")
            print(" Delete song - 'delete-song'")
            print(" Fragment repeater - 'fr'")
            print(" View mode - 'v-' + mode (all, f(n), l(n))")
            print(" Fast mode switcher (at least 1 line needed) - 'fm'")
            print("     (ONLY FAST MODE): s - new line with silence")
            print("     (ONLY FAST MODE): sr - silence line repeater")
            print(" Make .wav - 'make', 'make(start)-(end)'")
            print(" New note at specific position - 'sp'")
            print(" New note - '' ")
            if fastmodeActive==True:
                ch = input("[FAST MODE]: ")
            elif fastmodeActive==False:
                ch = input(": ")
            if ch=="exit":
                sys.exit(0)
            if rawfiledata[1]=="v1.1" and ch=="sd":
                while True:
                    clear()
                    print(" Song: [Name[n]: " + c_name)
                    print("        Artist[a]: " + c_artist)
                    print("        Description[d]: " + c_desc + "]")
                    print()
                    tmp_ch = input(": ")
                    if tmp_ch=="n":
                        c_name = input("Name: ")
                    elif tmp_ch=="a":
                        c_artist = input("Artist: ")
                    elif tmp_ch=="d":
                        c_desc = input("Description: ")
                    else:
                        break
                writefile(oldstuff, file + ".ast", "ast")
            if ch=="s": # fast mode silence
                if fastmodeActive==True: # use only in fast mode
                    fast_prev_lines = oldlines[-1].split(" ") # last line parser
                    length = input("LENGTH: ")
                    note = "NN" # silence
                    inst = "NN" # silence
                    amp = fast_prev_lines[3]
                    writefile(oldstuff.replace("\n", "") + "!" + note + " " + length + " " + inst + " " + amp, file + ".ast", "ast")
                    continue
                else:
                    continue # avoiding unknown bugs
            if ch=="sr": # fast mode silence repeater
                if fastmodeActive==True: # use only in fast mode
                    i = -1
                    while True:
                        fast_prev_lines = oldlines[i].split(" ")
                        if fast_prev_lines[2]!="NN":
                            i = i - 1
                        else:
                            break
                    writefile(oldstuff.replace("\n", "") + "!" + fast_prev_lines[0] + " " + fast_prev_lines[1] + " " + fast_prev_lines[2] + " " + fast_prev_lines[3], file + ".ast", "ast")
                else:
                    continue
            if "v-" in ch: # view mode changer
                tvm = ch.replace("v-", "").upper()
                if tvm=="ALL": # all view mode
                    view_mode = tvm
                elif "F" in tvm: # first view mode
                    view_mode = "FIRST"
                    try:
                        view_mode_lines = int(tvm.replace("F", ""))
                    except ValueError:
                        continue
                elif "L" in tvm: # last view mode
                    view_mode = "LAST"
                    try:
                        view_mode_lines = int(tvm.replace("L", ""))
                    except ValueError:
                        continue
                elif "-" in tvm: # from-to view mode
                    view_mode = "FT" + tvm.split("-")[0] + "-" + tvm.split("-")[1]
            if ch=="" or "sp" in ch: # adding lines
                if "sp" in ch:
                    try:
                        place = int(input("Place: "))
                    except ValueError:
                        continue
                note = input("NOTE: ")
                if note=="": continue
                length = input("LENGTH: ")
                if length=="": continue
                if fastmodeActive==False:
                    inst = input("INST: ")
                    if length=="": continue
                    amp = input("AMPLITUDE: ")
                    if amp=="": amp = "1"
                elif fastmodeActive==True and oldlines!=[]:
                    # last line parser
                    i = -1
                    while True:
                        fast_prev_lines = oldlines[i].split(" ")
                        if fast_prev_lines[2]=="NN": # if silence
                            i = i - 1
                        else: # if instrument
                            break
                    inst = fast_prev_lines[2]
                    amp = fast_prev_lines[3]
                newstuff = oldstuff.replace("\n", "").split("!")
                if "sp" in ch:
                    newstuff.insert(place, note + " " + length + " " + inst + " " + amp)
                else:
                    newstuff.append(note + " " + length + " " + inst + " " + amp)
                writefile("!".join(newstuff), file + ".ast", "ast")
                continue
            if "make" in ch or ch=="make":
                prev_data = ""
                astsng = oldstuff.split("!")
                i = 0
                try:
                    open(file + ".wav", "r") # deleting old builds
                    os.remove(file + ".wav")
                except FileNotFoundError:
                    pass
                for section in astsng:
                    if "-" in ch: # line to line mode
                        if ch.replace("make","").split("-")[0]>str(i): continue # if start less than i -> skip this note
                        if ch.replace("make", "").split("-")[1]==str(i-1): break # if end == i -> end (хз почему -1, работает значит надо)
                    i = i + 1
                    if section!="":
                        params = section.split()
                        if params[0]=="C0":
                            params[0] = 16.35
                        elif params[0]=="C#0":
                            params[0] = 17.32
                        elif params[0]=="D0":
                            params[0] = 18.35
                        elif params[0]=="D#0":
                            params[0] = 19.45
                        elif params[0]=="E0":
                            params[0] = 20.60
                        elif params[0]=="F0":
                            params[0] = 21.83
                        elif params[0]=="F#0":
                            params[0] = 23.12
                        elif params[0]=="G0":
                            params[0] = 24.50
                        elif params[0]=="G#0":
                            params[0] = 25.96
                        elif params[0]=="A0":
                            params[0] = 27.50
                        elif params[0]=="A#0":
                            params[0] = 29.14
                        elif params[0]=="B0":
                            params[0] = 30.87
                        elif params[0]=="C1":
                            params[0] = 32.70
                        elif params[0]=="C#1":
                            params[0] = 34.65
                        elif params[0]=="D1":
                            params[0] = 36.71
                        elif params[0]=="D#1":
                            params[0] = 38.89
                        elif params[0]=="E1":
                            params[0] = 41.20
                        elif params[0]=="F1":
                            params[0] = 43.65
                        elif params[0]=="F#1":
                            params[0] = 46.25
                        elif params[0]=="G1":
                            params[0] = 49.00
                        elif params[0]=="G#1":
                            params[0] = 51.91
                        elif params[0]=="A1":
                            params[0] = 55.00
                        elif params[0]=="A#1":
                            params[0] = 58.27
                        elif params[0]=="B1":
                            params[0] = 61.74
                        elif params[0]=="C2":
                            params[0] = 65.41
                        elif params[0]=="C#2":
                            params[0] = 69.30
                        elif params[0]=="D2":
                            params[0] = 73.42
                        elif params[0]=="D#2":
                            params[0] = 77.78
                        elif params[0]=="E2":
                            params[0] = 82.41
                        elif params[0]=="F2":
                            params[0] = 87.31
                        elif params[0]=="F#2":
                            params[0] = 92.50
                        elif params[0]=="G2":
                            params[0] = 98.00
                        elif params[0]=="G#2":
                            params[0] = 103.83
                        elif params[0]=="A2":
                            params[0] = 110.00
                        elif params[0]=="A#2":
                            params[0] = 116.54
                        elif params[0]=="B2":
                            params[0] = 123.47
                        elif params[0]=="C3":
                            params[0] = 130.81
                        elif params[0]=="C#3":
                            params[0] = 138.59
                        elif params[0]=="D3":
                            params[0] = 146.83
                        elif params[0]=="D#3":
                            params[0] = 155.56
                        elif params[0]=="E3":
                            params[0] = 164.81
                        elif params[0]=="F3":
                            params[0] = 174.61
                        elif params[0]=="F#3":
                            params[0] = 185.00
                        elif params[0]=="G3":
                            params[0] = 196.00
                        elif params[0]=="G#3":
                            params[0] = 207.65
                        elif params[0]=="A3":
                            params[0] = 220.00
                        elif params[0]=="A#3":
                            params[0] = 233.08
                        elif params[0]=="B3":
                            params[0] = 246.94
                        elif params[0]=="C4":
                            params[0] = 261.63
                        elif params[0]=="C#4":
                            params[0] = 277.18
                        elif params[0]=="D4":
                            params[0] = 293.66
                        elif params[0]=="D#4":
                            params[0] = 311.13
                        elif params[0]=="E4":
                            params[0] = 329.63
                        elif params[0]=="F4":
                            params[0] = 349.23
                        elif params[0]=="F#4":
                            params[0] = 369.99
                        elif params[0]=="G4":
                            params[0] = 392.00
                        elif params[0]=="G#4":
                            params[0] = 415.30
                        elif params[0]=="A4":
                            params[0] = 440.00
                        elif params[0]=="A#4":
                            params[0] = 466.16
                        elif params[0]=="B4":
                            params[0] = 493.88
                        elif params[0]=="C5":
                            params[0] = 523.25
                        elif params[0]=="C#5":
                            params[0] = 554.37
                        elif params[0]=="D5":
                            params[0] = 587.33
                        elif params[0]=="D#5":
                            params[0] = 622.25
                        elif params[0]=="E5":
                            params[0] = 659.25
                        elif params[0]=="F5":
                            params[0] = 698.46
                        elif params[0]=="F#5":
                            params[0] = 739.99
                        elif params[0]=="G5":
                            params[0] = 783.99
                        elif params[0]=="G#5":
                            params[0] = 830.61
                        elif params[0]=="A5":
                            params[0] = 880.00
                        elif params[0]=="A#5":
                            params[0] = 932.33
                        elif params[0]=="B5":
                            params[0] = 987.77
                        elif params[0]=="C6":
                            params[0] = 1046.50
                        elif params[0]=="C#6":
                            params[0] = 1108.73
                        elif params[0]=="D6":
                            params[0] = 1174.66
                        elif params[0]=="D#6":
                            params[0] = 1244.51
                        elif params[0]=="E6":
                            params[0] = 1318.51
                        elif params[0]=="F6":
                            params[0] = 1396.91
                        elif params[0]=="F#6":
                            params[0] = 1479.98
                        elif params[0]=="G6":
                            params[0] = 1567.98
                        elif params[0]=="G#6":
                            params[0] = 1661.22
                        elif params[0]=="A6":
                            params[0] = 1760.00
                        elif params[0]=="A#6":
                            params[0] = 1864.66
                        elif params[0]=="B6":
                            params[0] = 1975.53
                        elif params[0]=="C7":
                            params[0] = 2093.00
                        elif params[0]=="C#7":
                            params[0] = 2217.46
                        elif params[0]=="D7":
                            params[0] = 2349.32
                        elif params[0]=="D#7":
                            params[0] = 2489.02
                        elif params[0]=="E7":
                            params[0] = 2637.02
                        elif params[0]=="F7":
                            params[0] = 2793.83
                        elif params[0]=="F#7":
                            params[0] = 2959.96
                        elif params[0]=="G7":
                            params[0] = 3135.96
                        elif params[0]=="G#7":
                            params[0] = 3322.44
                        elif params[0]=="A7":
                            params[0] = 3520.00
                        elif params[0]=="A#7":
                            params[0] = 3729.31
                        elif params[0]=="B7":
                            params[0] = 3951.07
                        elif params[0]=="C8":
                            params[0] = 4186.01
                        elif params[0]=="C#8":
                            params[0] = 4434.92
                        elif params[0]=="D8":
                            params[0] = 4698.63
                        elif params[0]=="D#8":
                            params[0] = 5274.04
                        elif params[0]=="E8":
                            params[0] = 5274.04
                        elif params[0]=="F8":
                            params[0] = 5587.65
                        elif params[0]=="F#8":
                            params[0] = 5919.91
                        elif params[0]=="G8":
                            params[0] = 6271.93
                        elif params[0]=="G#8":
                            params[0] = 6644.88
                        elif params[0]=="A8":
                            params[0] = 7040.00
                        elif params[0]=="A#8":
                            params[0] = 7458.62
                        elif params[0]=="B8":
                            params[0] = 7902.13
                        else:
                            if params[0]!="NN": # delay skip fix
                                print("Note doesn't exist. Skip.")
                                continue
                        if params[2]=="NN" or params[0]=="NN":
                            write(file + ".wav", sawtooth_gen(1.0, float(params[1]), 0))
                        elif params[2]=="SWT":
                            write(file + ".wav", sawtooth_gen(float(params[0]), float(params[1]), float(params[3])))
                        elif params[2]=="SIN":
                            write(file + ".wav", sin_gen(float(params[0]), float(params[1]), float(params[3])))
                        elif params[2]=="TRE":
                            write(file + ".wav", triangle_gen(float(params[0]), float(params[1]), float(params[3])))
                        elif params[2]=="GTR":
                            write(file + ".wav", guitar_gen(float(params[0]), float(params[1]), float(params[3])))
                        elif params[2]=="NSE":
                            write(file + ".wav", noise_gen(float(params[1]), float(params[3])))
                        elif params[2]=="PSE":
                            write(file + ".wav", pitched_nse_gen(float(params[0]), float(params[1]), float(params[3])))
                        else: # sample logic
                            result = sample_gen(params[2])
                            if result!=False:
                                write(file + ".wav", result)
                        print("Line: " + str(i) + "/" + str(len(astsng)))
                continue
            if ch=="m":
                break
            if ch=="u":
                writefile("!".join(oldlines[:-1]), file + ".ast", "ast")
                continue
            if ch=="r":
                try:
                    oldlines.append(oldlines[-1])
                    writefile("!".join(oldlines), file + ".ast", "ast")
                except IndexError:
                    pass
                continue
            if ch=="delete-song":
                clear()
                print("Are you sure?")
                life_ch = input("Y/N: ").lower()
                if life_ch=="y":
                    delete(file + ".ast")
                    break
                else:
                    continue
            if ch=="fr": # fragment repeater
                try:
                    start = int(input("Start line: "))
                    stop = int(input("Stop line: "))+1
                except ValueError:
                    continue
                for line in oldlines[start:stop]:
                    oldstuff = readfile(file + ".ast", "ast")[0]
                    writefile(oldstuff.replace("\n", "") + "!" + line, file + ".ast", "ast")
                continue
            if ch=="fm": # fast mode switcher
                if fastmodeActive:
                    fastmodeActive = False
                else:
                    if oldlines!=[]:
                        fastmodeActive = True
                continue
            if 'e' in ch and ch!="e":
                line = ch.replace('e', '').replace(' ', '')
                note = input("NOTE: ")
                length = input("LENGTH: ")
                if fastmodeActive==False:
                    inst = input("INST: ")
                    amp = input("AMPLITUDE: ")
                elif fastmodeActive==True:
                    # last line parser
                    fast_prev_lines = oldlines[-1].split(" ")
                    inst = fast_prev_lines[2]
                    amp = fast_prev_lines[3]
                oldlines[int(line)] = note + " " + length + " " + inst + " " + amp
                writefile('!'.join(oldlines), file + ".ast", "ast")
                continue
            if 'd' in ch and ch!="sd":
                line = ch.replace('d', '').replace(' ', '')
                oldlines.pop(int(line))
                writefile('!'.join(oldlines), file + ".ast", "ast")
                continue
    elif mn_ch=="2":
        clear()
        print(title)
        print(" .AST tools")
        print()
        print(" 1) Speed changer")
        print(" 2) Pitch changer")
        print(" 3) Amplitude changer")
        print(" 4) Instrument changer")
        print(" 5) Joiner")
        print(" 6) Repeater")
        print(" 7) Version updater")
        print(" ")
        tl = input(": ")
        clear()
        if tl=="1":
            print(title)
            print(" .AST speed changer")
            print(" ")
            filename = input("File (only name): ")
            speed = input("Speed (1.0): ")
            try:
                speed = float(speed)
            except ValueError:
                print("Couldn't convert '" + speed + "' to float.")
                wait()
                continue
            data = readfile(filename + ".ast", "ast")
            if data==False:
                continue
            for i in data[0].split("!"):
                if i!='':
                    temp = i.split(" ")
                    fetchsngdata(filename + ".ast")
                    writefile(data[0] + "!" + temp[0] + " " + str(float(temp[1]) / speed) + " " + temp[2] + " " + temp[3], filename + ".ast", "ast")
        elif tl=="5":
            print(title)
            print(" .AST joiner")
            print(" ")
            filelist = input("Files (only names): ").split(" ")
            resultfile = input("Result file (only name): ")
            total_file_data = ""
            for filename in filelist:
                data = readfile(filename + ".ast", "ast")
                if data==False:
                    break
                total_file_data = total_file_data + "!" + data[0].replace("\n", "")
            if total_file_data=="":
                continue
            fetchsngdata(filename + ".ast")
            writefile(total_file_data, resultfile + ".ast", "ast")
        elif tl=="4":
            print(title)
            print(" .AST instrument changer")
            print(" ")
            print(" 1) Change all instruments to ...")
            print(" 2) Change ... instrument to ...")
            print(" 3) Change ... instrument to random instrument from ...")
            ch = input(": ")
            if ch!="1" and ch!="2" and ch!="3":
                continue
            filename = input("File (only name): ")
            if ch=="1":
                instrument = input("Instrument: ")
            elif ch=="2":
                oinst = input("Instrument (old): ")
                ninst = input("Instrument (new): ")
            elif ch=="3":
                oinst = input("Instrument (old): ")
                ninst = input("Instruments list (new): ").split(" ")
            data = readfile(filename + ".ast", "ast")[0]
            if data==False:
                continue
            data = data.split("!")
            if data=="":
                continue
            i = -1
            for dat in data:
                i += 1
                if dat!="":
                    dat = dat.split(" ")
                    if ch=="1":
                        dat[2] = instrument
                    elif ch=="2" or ch=="3":
                        if dat[2]==oinst:
                            if ch=="3":
                                dat[2] = random.choice(ninst)
                            else:
                                dat[2] = ninst
                    data[i] = ' '.join(dat)
            fetchsngdata(filename + ".ast")
            writefile('!'.join(data), filename + ".ast", "ast")
        elif tl=="2":
            clear()
            print(title)
            print(" .AST pitch changer")
            print(" ")
            filename = input("File (only name): ")
            data = readfile(filename + ".ast", "ast")[0]
            if data==False:
                continue
            pc = input("Pitch (half-octaves): ")
            data = data.split("!")
            if data=="":
                continue
            i = -1
            ndata = []
            for dat in data:
                i += 1
                if dat!="":
                    dat = dat.split(" ")
                    instrument = dat[0]
                    # checking for up pitch or down pitch
                    if pc[:1]!="-": # pitch up
                        for i in range(0, int(pc)):
                            if instrument[0]=="C" and instrument[1]!="#":
                                instrument = "C#" + instrument.replace("C", "")
                            elif instrument[0]=="C" and instrument[1]=="#":
                                instrument = "D" + instrument.replace("C#", "")
                            elif instrument[0]=="D" and instrument[1]!="#":
                                instrument = "D#" + instrument.replace("D", "")
                            elif instrument[0]=="D" and instrument[1]=="#":
                                instrument = "E" + instrument.replace("D#", "")
                            elif instrument[0]=="E":
                                instrument = "F" + instrument.replace("E", "")
                            elif instrument[0]=="F" and instrument[1]!="#":
                                instrument = "F#" + instrument.replace("F", "")
                            elif instrument[0]=="F" and instrument[1]=="#":
                                instrument = "G" + instrument.replace("F#", "")
                            elif instrument[0]=="G" and instrument[1]!="#":
                                instrument = "G#" + instrument.replace("G", "")
                            elif instrument[0]=="G" and instrument[1]=="#":
                                instrument = "A" + instrument.replace("G#", "")
                            elif instrument[0]=="A" and instrument[1]!="#":
                                instrument = "A#" + instrument.replace("A", "")
                            elif instrument[0]=="A" and instrument[1]=="#":
                                instrument = "B" + instrument.replace("A#", "")
                            elif instrument[0]=="B":
                                if instrument[-1]!="7": # max octave
                                    instrument = "C" + str(int(instrument[-1]) + 1) # octave up
                            else: # invalid note
                                print("Invalid note")
                    elif pc[:1]=="-": # pitch down
                        for i in range(1, int(pc.replace("-", ""))):
                            if instrument[0]=="B":
                                if instrument[-1]!="0": # minimal octave
                                    instrument = "C" + str(int(instrument[-1]) - 1) # octave down
                            elif instrument[0]=="A" and instrument[1]=="#":
                                instrument = "A" + instrument.replace("A#", "")
                            elif instrument[0]=="A" and instrument[1]!="#":
                                instrument = "G#" + instrument.replace("A", "")
                            elif instrument[0]=="G" and instrument[1]=="#":
                                instrument = "G" + instrument.replace("G#", "")
                            elif instrument[0]=="G" and instrument[1]!="#":
                                instrument = "F#" + instrument.replace("G", "")
                            elif instrument[0]=="F" and instrument[1]=="#":
                                instrument = "F" + instrument.replace("F#", "")
                            elif instrument[0]=="F" and instrument[1]!="#":
                                instrument = "E" + instrument.replace("F", "")
                            elif instrument[0]=="E":
                                instrument = "D#" + instrument.replace("E", "")
                            elif instrument[0]=="D" and instrument[1]=="#":
                                instrument = "D" + instrument.replace("D#", "")
                            elif instrument[0]=="D" and instrument[1]!="#":
                                instrument = "C#" + instrument.replace("D", "")
                            elif instrument[0]=="C" and instrument[1]=="#":
                                instrument = "C" + instrument.replace("C#", "")
                            elif instrument[0]=="C" and instrument[1]!="#":
                                if instrument[-1]!="0": # minimal octave
                                    instrument = "B" + str(int(instrument[-1]) - 1) # octave down
                            else:
                                print("Invalid note!")
                    dat[0] = instrument
                    ndata.append(' '.join(dat))
            fetchsngdata(filename + ".ast")
            writefile('!'.join(ndata), filename + ".ast", "ast")
        elif tl=="6":
            clear()
            print(title)
            print(" .AST repeater")
            print(" ")
            filename = input("File (only name): ")
            data = readfile(filename + ".ast", "ast")
            if data==False:
                continue
            try:
                count = int(input("Count: "))
            except ValueError:
                print("Invalid integer!")
                wait()
                continue
            data = data[0].replace("\n", "")
            if data[1]!="!": # '1' bug fix
                data = data + "!"
            fetchsngdata(filename + ".ast")
            writefile((data * count)[:-1], filename + ".ast", "ast")
        elif tl=="3":
            clear()
            print(title)
            print(" .AST amplitude changer")
            print(" ")
            filename = input("File (only name): ")
            data = readfile(filename + ".ast", "ast")
            if data==False:
                continue
            pc = input("Amplitude: ")
            data = data[0].split("!")
            if data=="":
                continue
            i = -1
            ndata = []
            for dat in data:
                i += 1
                if dat!="":
                    dat = dat.split(" ")
                    dat[3] = pc
                    ndata.append(' '.join(dat))
            fetchsngdata(filename + ".ast")
            writefile('!'.join(ndata), filename + ".ast", "ast")
        elif tl=="7": # .ast version updater
            clear()
            print(title)
            print(" .AST version updater")
            print(" ")
            filename = input("File (only name): ")
            data = readfile(filename + ".ast", "ast")
            if data==False:
                continue
            clear()
            if data[1]=="v1.1": # lastest ast version
                print("Current version is latest: v1.1")
            else: # old version
                print("Old version: " + data[1])
                print("New version: v1.1")
                print()
                c_name = input("New name: ")
                c_artist = input("New artist: ")
                c_desc = input("New description: ")
                # data = "[ast v1]\n" + data (updating for v1 version)
                fetchsngdata(filename + ".ast")
                writefile(data[0], filename + ".ast", "ast") # update logic in func
            continue
        else:
            continue
    elif mn_ch=="3":
        clear()
        print(title)
        print(" .WAV tools")
        print()
        print(" 1) Joiner")
        print(" 2) Repeater")
        print(" ")
        tl = input(": ")
        clear()
        if tl=="1":
            clear()
            print(title)
            print(" .WAV joiner")
            print(" ")
            filenames = input("Files (only names): ").split(" ")
            output_file_name = input("Result file (only name): ")
            for filename in filenames:
                sound = readfile(filename + ".wav", "wav")
                if sound==False:
                    continue
                write(output_file_name + ".wav", sound)
        elif tl=="2":
            clear()
            print(title)
            print(" .WAV Repeater")
            print(" ")
            filename = input("File (only name): ")
            data = readfile(filename + ".ast", "ast")
            if data==False:
                continue
            try:
                count = int(input("Count: "))
            except ValueError:
                print("Invalid integer!")
                wait()
                continue
            sound = readfile(filename + ".wav", "wav")
            if sound==False:
                continue
            for i in range(1, count):
                write(filename + ".wav", sound)
        else:
            continue
    elif mn_ch=="s": # settings
        clear()
        print(title)
        print(" Settings")
        print()
        print(" Pick:")
        print(" [1] Sample pack: " + settings['sample_folder'])
        print(" ")
        ch = input(": ")
        if ch=="1":
            settings['sample_folder'] = input("New value: ")
        elif ch=="m":
            continue
        else:
            continue
        settings_func("s")
    elif mn_ch=="h":
        clear()
        print(title)
        print("Help")
        print(" ")
        print("Default instruments:")
        print(" 'SWT' - Sawtooth wave generator")
        print(" 'SIN' - Sinusoid wave generator")
        print(" 'TRE' - Triangle wave generator")
        print(" 'NSE' - Noise generator")
        print(" 'PSE' - Pitched noise generator")
        print(" 'GTR' - Guitar sound generator")
        print(" 'NN' - Silence generator")
        print(" ")
        print(".AST Editor view modes:")
        print(" 'all' - display all lines")
        print(" 'f' + number - display first (number) lines")
        print(" 'l' + number - display last (number) lines")
        print(" start + '-' + stop - display from-to lines ")
        print(" ")
        print("FAQ:")
        print(" Error: 'wave.Error: unknown format'")
        print(" Solution: use only 16 bit wav files")
        print(" ")
        wait()
    elif mn_ch=="a":
        clear()
        print(title)
        print("About")
        print("""
https://github.com/mrtnvgr/ast-tracker
Copyright © 2021-2022 mrtnvgr (MIT License)
        """)
        wait()
    elif mn_ch=="u":
        git_version = requests.get(api_git_link).json()["name"]
        if version!=git_version:
            clear()
            print(title)
            print()
            print("New update " + git_version + "!")
            u_ch = input("Download update? (y/n): ").lower()
            if u_ch=="y":
                w_ch = input("Source code or .exe (src/exe): ").lower()
                if w_ch=="exe":
                    download(exe_download_link, "ast-tracker-" + git_version + ".exe")
                elif w_ch=="src":
                    download(src_download_link, "ast-tracker-" + git_version + ".py")
            else:
                continue
        else:
            clear()
            print(title)
            print(" ")
            print("You are using latest release!")
            print(" ")
            wait()
    elif mn_ch=="e":
        sys.exit(0) # exit from main menu
    else:
        continue
