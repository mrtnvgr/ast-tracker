print("Starting...")

import wave, os, random, base64, pyaudio, time, requests, urllib, json
from numpy import linspace, arange, pi, sin, zeros, int16, frombuffer
from numpy import random as nprandom
from numpy import abs as npabs
from numpy import max as npmax
from numpy import min as npmin
import soundfile as sf

title = "Ast-Tracker v1.3.5-1"
api_git_link = "https://api.github.com/repos/martynovegor/ast-tracker/releases/latest"
download_link = "https://github.com/martynovegor/ast-tracker/releases/latest/download/ast-tracker.exe"
version = "v1.3.5-1"

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

# sawtooth_gen(990.0, 5.0, 1)
def sawtooth_gen(f_c, duration_s, amp):
    t_samples = arange(44100 * duration_s) / 44100
    waveform = f_c * t_samples
    waveform_quiet = waveform * amp
    waveform_ints = int16(waveform_quiet * 32768)
    return(waveform_ints)


# sin_gen(990.0, 5.0, 1)
def sin_gen(f_c, duration_s, amp):
    t_samples = arange(44100 * duration_s) / 44100
    waveform = sin(2 * pi * f_c * t_samples)
    waveform_quiet = waveform * amp
    waveform_ints = int16(waveform_quiet * 32768)
    return(waveform_ints)

# White noise
# noise_gen(5.0, 1.0)
def noise_gen(duration_s, amp):
    pure = linspace(0, 1, int(duration_s * 44100))
    noise = nprandom.normal(0, 1, pure.shape)
    signal = pure + noise
    waveform_quiet = signal * amp
    waveform_ints = int16(waveform_quiet * 32768)
    return(waveform_ints)

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
    global settings
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
            print("File " + filename + " doesn't exist")
            wait()
            return False
    try:
        data = open(filename, "r").read()
        return data
    except FileNotFoundError:
        clear()
        print(" File " + filename + " doesn't exist")
        wait()
        return False

while True:
    clear()
    print(title)
    print(" ")
    print(" 1) .AST editor")
    print(" 2) .AST tools")
    print(" 3) .WAV tools")
    print(" ")
    print(" 4) Settings")
    print(" 5) Help")
    print(" 0) About")
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
        while True:
            clear()
            print(title)
            print(" .AST editor [Current song: " + file + "]")
            try:
                oldstuff = open(file + ".ast", "r").read()
            except FileNotFoundError:
                pass
            print(" ")
            print("[NOTE] [LENGTH] [INSTR] [AMP]")
            oldlines = oldstuff.split("!")
            if oldlines[0]=="":
                oldlines.pop(0) # [0] empty string bug fix
            n = -1
            for i in oldlines:
                n = n + 1
                print("[" + str(n) + "] " + i)
            print(" ")
            print(" Go to menu - 'm' ")
            print(" Delete last line - 'u' ")
            print(" Repeat last line - 'r' ")
            print(" Edit specific line - 'e' + number")
            print(" Delete specific line - 'd' + number")
            print(" Delete song - 'delete-song'")
            print(" Fragment repeater - 'fr'")
            print(" Fast mode switcher (at least 1 line needed) - 'fm'")
            print(" Make .wav - 'make'")
            print(" Graphical player - 'play'")
            print(" New note - '' ")
            if fastmodeActive==True:
                ch = input("[FAST MODE]: ")
            elif fastmodeActive==False:
                ch = input(": ")
            if ch=='make' or ch=='play':
                prev_data = ""
                astsng = readfile(file + ".ast", "ast").split("!")
                i = 0
                if ch=='make':
                    try:
                        open(file + ".wav", "r") # deleting old builds
                        os.remove(file + ".wav")
                    except FileNotFoundError:
                        pass
                elif ch=='play':
                    str_note = []
                    length_note = []
                    instrument_note = []
                    amp_note = []
                    data_note = []
                for section in astsng:
                    i = i + 1
                    if section!="":
                        params = section.split()
                        if ch=='play': # string note for player
                            str_note.append(params[0])
                            length_note.append(params[1])
                            instrument_note.append(params[2])
                            amp_note.append(params[3])
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
                        if ch=='make':
                            if params[2]=="NN" or params[0]=="NN":
                                write(file + ".wav", sawtooth_gen(1.0, float(params[1]), 0))
                            elif params[2]=="SWT":
                                write(file + ".wav", sawtooth_gen(float(params[0]), float(params[1]), float(params[3])))
                            elif params[2]=="SIN":
                                write(file + ".wav", sin_gen(float(params[0]), float(params[1]), float(params[3])))
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
                        elif ch=='play':
                            if params[2]=="NN" or params[0]=="NN":
                                data_note.append(sawtooth_gen(1.0, float(params[1]), 0))
                            elif params[2]=="SWT":
                                data_note.append(sawtooth_gen(float(params[0]), float(params[1]), float(params[3])))
                            elif params[2]=="SIN":
                                data_note.append(sin_gen(float(params[0]), float(params[1]), float(params[3])))
                            elif params[2]=="GTR":
                                data_note.append(guitar_gen(float(params[0]), float(params[1]), float(params[3])))
                            elif params[2]=="NSE":
                                data_note.append(noise_gen(float(params[1]), float(params[3])))
                            elif params[2]=="PSE":
                                data_note.append(pitched_nse_gen(float(params[0]), float(params[1]), float(params[3])))
                            else: # sample logic
                                result = sample_gen(params[2])
                                if result!=False:
                                    data_note.append(result)
                            print("Parsing line: " + str(i) + "/" + str(len(astsng)))
                if ch=='play':
                    p = pyaudio.PyAudio()
                    stream = p.open(format=pyaudio.paInt16,
                                    channels=2,
                                    rate=44100,
                                    output=True)
                    i = -1
                    while True:
                        if i==len(str_note)-1:
                            break
                        i = i + 1
                        clear()
                        print(".AST Player [Current song: " + file + "]")
                        print(" ")
                        print("Note: " + str_note[i])
                        print("Length: " + length_note[i])
                        print("Instrument: " + instrument_note[i])
                        print("Amplitude: " + amp_note[i])
                        print(" ")
                        print(" ")
                        stream.write(data_note[i])
                    stream.stop_stream()
                    stream.close()
                continue
            if ch=="":
                note = input("NOTE: ")
                if note=="": continue
                length = input("LENGTH: ")
                if length=="": continue
                if fastmodeActive==False:
                    inst = input("INST: ")
                    if length=="": continue
                    amp = input("AMPLITUDE: ")
                    if amp=="": amp = "1"
                elif fastmodeActive==True:
                    # last line parser
                    fast_prev_lines = oldlines[-1].split(" ")
                    inst = fast_prev_lines[2]
                    amp = fast_prev_lines[3]
                open(file + ".ast", "w").write(oldstuff.replace("\n", "") + "!" + note + " " + length + " " + inst + " " + amp) # new line bug fix
            elif ch=="m":
                break
            elif ch=="u":
                open(file + ".ast", "w").write("!".join(oldlines[:-1]))
            elif ch=="r":
                try:
                    oldlines.append(oldlines[-1])
                    open(file + ".ast", "w").write("!".join(oldlines))
                except IndexError:
                    pass
            elif ch=="delete-song":
                clear()
                print("Are you sure?")
                life_ch = input("Y/N: ").lower()
                if life_ch=="y":
                    delete(file + ".ast")
                    break
                else:
                    continue
            elif ch=="fr": # fragment repeater
                try:
                    start = int(input("Start line: "))
                    stop = int(input("Stop line: "))+1
                except ValueError:
                    continue
                for line in oldlines[start:stop]:
                    oldstuff = open(file + ".ast", "r").read()
                    open(file + ".ast", "w").write(oldstuff.replace("\n", "") + "!" + line)
            elif ch=="fm": # fast mode switcher
                if fastmodeActive:
                    fastmodeActive = False
                else:
                    if oldlines!=[]: # bug fix
                        fastmodeActive = True
            elif 'e' in ch:
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
                open(file + ".ast", "w").write(oldstuff.replace("\n", "") + "!" + note + " " + length + " " + inst + " " + amp) # new line bug fix
                oldlines[int(line)] = note + " " + length + " " + inst + " " + amp
                open(file + ".ast", "w").write('!'.join(oldlines))
            elif 'd' in ch:
                line = ch.replace('d', '').replace(' ', '')
                oldlines.pop(int(line))
                open(file + ".ast", "w").write('!'.join(oldlines))
    elif mn_ch=="2":
        clear()
        print(title)
        print(" .AST tools")
        print(" 1) Speed changer")
        print(" 2) Pitch changer")
        print(" 3) Amplitude changer")
        print(" 4) Instrument changer")
        print(" 5) Joiner")
        print(" 6) Repeater")
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
            f = open(filename + ".ast", "w")
            for i in data.split("!"):
                if i!='':
                    temp = i.split(" ")
                    f.write("!" + temp[0] + " " + str(float(temp[1]) / speed) + " " + temp[2] + " " + temp[3])
            f.close()
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
                    continue
                total_file_data = total_file_data + data.replace("\n", "")
            open(resultfile + ".ast", "w").write(total_file_data)
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
            data = readfile(filename + ".ast", "ast")
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
            open(filename + ".ast", "w").write('!'.join(data))
        elif tl=="2":
            clear()
            print(title)
            print(" .AST pitch changer")
            print(" ")
            filename = input("File (only name): ")
            data = readfile(filename + ".ast", "ast")
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
                                    instrument = "B" + str(int(instrument[-1]) + 1) # octave down
                            else:
                                print("Invalid note!")
                    dat[0] = instrument
                    ndata.append(' '.join(dat))
            open(filename + ".ast", "w").write('!'.join(ndata))
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
            data = data.replace("\n", "")
            if data[1]!="!": # '1' bug fix
                data = data + "!"
            open(filename + ".ast", "w").write(data * count)
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
            data = data.split("!")
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
            open(filename + ".ast", "w").write('!'.join(ndata))
        else:
            continue
    elif mn_ch=="3":
        clear()
        print(title)
        print(" .WAV tools")
        print(" 1) .WAV to one string converter")
        print(" 2) Joiner")
        print(" 3) Repeater")
        print(" ")
        tl = input(": ")
        clear()
        if tl=="1":
            clear()
            print(title)
            print(" .WAV to one string converter")
            print(" ")
            filename = input(".WAV File (only name): ")
            outputfile = input("Output File (*): ")
            try:
                data, fs = sf.read(filename + ".wav", dtype='float32')
            except RuntimeError:
                clear()
                print(" File " + filename + ".wav doesn't exist!")
                wait()
                continue
            st = open(outputfile, "wb")
            a = b'exec("""import simpleaudio as sa\\nimport numpy as np\\nimport base64\\nobj = sa.play_buffer(np.frombuffer(base64.decodebytes(b"' + base64.b64encode(data) + b'"), dtype=np.float64), 2, 2, 44100)\nobj.wait_done()""")'
            st.write(a)
            st.close()
        elif tl=="2":
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
        elif tl=="3":
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
    elif mn_ch=="4": # settings
        clear()
        print(title)
        print(" Settings")
        print(" Pick:")
        print(" [1] Sample pack: " + settings['sample_folder'])
        print(" ")
        print(" [0] Check for new updates")
        print(" [m] Main menu")
        print(" ")
        ch = input(": ")
        if ch=="1":
            settings['sample_folder'] = input("New value: ")
        elif ch=="0":
            git_version = requests.get(api_git_link).json()["name"]
            if version!=git_version:
                clear()
                print(title)
                print("New update! Version:" + git_version)
                u_ch = input("Download update? (y/n): ").lower()
                if u_ch=="y":
                    urllib.request.urlretrieve(download_link, "ast-tracker-" + git_version + ".exe")
                else:
                    continue
            else:
                clear()
                print(title)
                print(" ")
                print("You are using latest release!")
                print(" ")
                wait()
        elif ch=="m":
            continue
        else:
            continue
        settings_func("s")
    elif mn_ch=="5":
        clear()
        print(title)
        print("Help")
        print(" ")
        print("Default instruments:")
        print(" Sawtooth wave - SWT")
        print(" Sine wave - SIN")
        print(" Noise - NSE")
        print(" Pitched noise wave - PSE")
        print(" Guitar - GTR")
        print(" Delay - NN")
        print(" ")
        print("FAQ:")
        print(" Error: 'wave.Error: unknown format'")
        print(" Solution: use only 16 bit wav files")
        print(" ")
        wait()
    elif mn_ch=="0":
        clear()
        print(title)
        print("About")
        print("""
Just a simple tracker
Stay tuned for new releases! https://github.com/martynovegor/ast-tracker
Copyright © 2022 martynovegor (MIT License)
        """)
        wait()
    else:
        continue
