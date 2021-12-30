from __future__ import division

print("Starting...")

from numpy import ceil, linspace, tile, arange, pi, int16, sin, zeros, float32, int16, frombuffer
from numpy import random as nprandom
from numpy import abs as npabs
from numpy import max as npmax
import wave, time, sys, os, random, base64, math
from scipy import signal
import soundfile as sf

title = "Ast-Tracker v1.2.3"
prev_data = ""

def clear(): os.system("cls")
clear()
def wait(): os.system("pause")
def delete(file): os.system("del /q " + file)

# settings logic
def settings(mode):
    global setting_sample_pack
    try:
        settings_lines = open("settings.as", "r").readlines()
    except FileNotFoundError:
        print("Couldnt find settings file. Creating...")
        open("settings.as", "w").write("sample_pack = default")
        settings_lines = open("settings.as", "r").readlines()
    if mode=="r":
        for settings_line in settings_lines:
            if "sample_pack" in settings_line:
                setting_sample_pack = settings_line.replace("sample_pack = ", "")
    elif mode=="s":
        i = -1
        for settings_line in settings_lines:
            i += 1
            if "sample_pack" in settings_line:
                settings_lines[i] = "sample_pack = " + setting_sample_pack
        open("settings.as", "w").writelines(settings_lines)
settings("r")

# sawtooth_gen(990.0, 5.0, 1)
def sawtooth_gen(f_c, duration_s, vol):
    A_c = 0.3
    period_c = 1.0 / f_c
    periods_in_duration = int(ceil(duration_s / period_c))
    samples_per_period = int(ceil(period_c * 44100))
    sawtooth_period = linspace(1.0, -1.0, samples_per_period)
    tiled_sawtooth = tile(sawtooth_period, periods_in_duration)
    samples_in_duration = int(ceil(duration_s * 44100))
    waveform = tiled_sawtooth[:samples_in_duration]
    waveform *= A_c
    waveform_quiet = waveform * vol
    waveform_ints = int16(waveform_quiet * 32768)
    return(waveform_ints)

# sin_gen(990.0, 5.0, 1)
def sin_gen(f_c, duration_s, vol):
    t_samples = arange(44100 * duration_s) / 44100
    waveform = sin(2 * pi * f_c * t_samples)
    waveform_quiet = waveform * vol
    waveform_ints = int16(waveform_quiet * 32768)
    return(waveform_ints)


# triangle_gen(990.0, 5.0, 1)
def triangle_gen(f_c, duration_s, vol):
    t_samples = arange(44100 * duration_s) / 44100
    waveform = signal.sawtooth(2 * pi * f_c * t_samples, 0.5)
    waveform_quiet = waveform * vol
    waveform_ints = int16(waveform_quiet * 32768)
    return(waveform_ints)

# noise_gen(5.0, 1.0)
def noise_gen(duration_s, vol):
    pure = linspace(0, 1, int(duration_s) * 44100)
    noise = random.normal(0, 1, pure.shape)
    signal = pure + noise
    waveform_quiet = signal * vol
    waveform_ints = int16(waveform_quiet * 32768)
    return(waveform_ints)

# guitar_gen(990.0, 5.0, 1)
def guitar_gen(f_c, duration_s, vol):
    noise = nprandom.uniform(-1, 1, int(44100/f_c))
    samples = zeros(int(44100*duration_s))
    for i in range(len(noise)):
        samples[i] = noise[i]
    for i in range(len(noise), len(samples)):
        samples[i] = (samples[i-len(noise)]+samples[i-len(noise)-1])/2
    samples = samples / npmax(npabs(samples))
    waveform_quiet = samples * vol
    return int16(waveform_quiet * 32768)

def sample_gen(sample_name, sample_volume):
    global setting_sample_pack
    try:
        obj = wave.open(setting_sample_pack + "\\" + sample_name.lower() + ".wav", 'r')
        sample_data = obj.readframes(obj.getnframes())
        obj.close()
    except FileNotFoundError:
        print("Sample doesnt exist.")
    return(sample_data)

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
            print("File " + filename + " doesnt exist.")
            wait()
            return False
    try:
        data = open(filename, "r").read()
        return data
    except FileNotFoundError:
        clear()
        print(" File " + filename + " doesn't exist!")
        wait()
        return False

while True:
    clear()
    print(title)
    print(" 1) .AST to .WAV converter")
    print(" 2) .AST editor")
    print(" 3) .AST tools")
    print(" 4) .WAV tools")
    print(" ")
    print(" 5) Settings")
    print(" 0) Help")
    print(" ")
    mn_ch = input(": ")
    if mn_ch=="1":
        clear()
        print(title)
        print(" .AST to .WAV converter")
        print(" ")
        sngname = input("Song (only name): ")
        astsng = readfile(sngname + ".ast", "ast")
        if astsng==False:
            continue
        i = 0
        astsng = astsng.split("!")
        for section in astsng:
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
                    print("Note doesnt exist. Skip.")
                    continue
                if params[2]=="NN":
                    write(sngname + ".wav", sawtooth_gen(1.0, float(params[1]), 0))
                elif params[2]=="SWT":
                    write(sngname + ".wav", sawtooth_gen(float(params[0]), float(params[1]), float(params[3])))
                elif params[2]=="SIN":
                    write(sngname + ".wav", sin_gen(float(params[0]), float(params[1]), float(params[3])))
                elif params[2]=="TRE":
                    write(sngname + ".wav", triangle_gen(float(params[0]), float(params[1]), float(params[3])))
                elif params[2]=="GTR":
                    write(sngname + ".wav", guitar_gen(float(params[0]), float(params[1]), float(params[3])))
                elif params[2]=="NSE":
                    write(sngname + ".wav", noise_gen(float(params[1]), float(params[3])))
                else: # sample logic
                    write(sngname + ".wav", sample_gen(params[2], float(params[3])))
                print("Lines: " + str(i) + "/" + str(len(astsng)))
                continue
    elif mn_ch=="2":
        clear()
        print(title)
        print(" .AST editor")
        print(" ")
        file = input("File (only name): ")
        oldstuff = ""
        while True:
            clear()
            try:
                oldstuff = open(file + ".ast", "r").read()
            except FileNotFoundError:
                pass
            print(" Current file: " + file + ".ast")
            print("[NOTE] [LENGTH] [INSTR] [VOL]")
            oldlines = oldstuff.split("!")
            if oldlines[0]=="":
                oldlines.pop(0) # [0] empty string bug fix
            n = -1
            for i in oldlines:
                n = n + 1
                print("[" + str(n) + "] " + i)
            print(" ")
            print(" Delete last line - 'u' ")
            print(" Go to menu - 'm' ")
            print(" Edit specific line - 'e' + number")
            print(" Delete specific line - 'd' + number")
            print(" Delete song - 'delete-song'")
            print(" New note - '' ")
            ch = input(": ")
            if ch=="":
                note = input("NOTE: ")
                length = input("LENGTH: ")
                inst = input("INST: ")
                vol = input("VOLUME: ")
                f = open(file + ".ast", "w")
                f.write(oldstuff + "!" + note + " " + length + " " + inst + " " + vol)
            elif ch=="m":
                break
            elif ch=="u":
                f = open(file + ".ast", "w")
                f.write("!".join(oldlines[:-1]))
            elif ch=="delete-song":
                clear()
                print("Are you sure?")
                life_ch = input("Y/N: ").lower()
                if life_ch=="y":
                    delete(file + ".ast")
                    break
                else:
                    continue
            elif 'e' in ch:
                line = ch.replace('e', '').replace(' ', '')
                f = open(file + ".ast", "w")
                note = input("NOTE: ")
                length = input("LENGTH: ")
                inst = input("INST: ")
                vol = input("VOLUME: ")
                oldlines[int(line)] = note + " " + length + " " + inst + " " + vol
                f.write('!'.join(oldlines))
            elif 'd' in ch:
                line = ch.replace('d', '').replace(' ', '')
                oldlines.pop(int(line))
                f = open(file + ".ast", "w")
                f.write('!'.join(oldlines))
            else:
                continue
            f.close()
        continue
    elif mn_ch=="3":
        clear()
        print(title)
        print(" .AST tools")
        print(" 1) Speed changer")
        print(" 2) Joiner")
        print(" 3) Instrument replacer")
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
                speed = float(speed) # for avoiding bugs
            except ValueError:
                print("Couldnt convert '" + speed + "' to float.")
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
            continue
        elif tl=="2":
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
            continue
        elif tl=="3":
            print(title)
            print(" .AST instrument replacer")
            print(" ")
            print(" 1) Replace all instruments to ...")
            print(" 2) Replace ... instrument to ...")
            ch = input(": ")
            filename = input("File (only name): ")
            if ch=="1":
                instrument = input("Instrument: ")
            elif ch=="2":
                oinst = input("Instrument (old): ")
                ninst = input("Instrument (new): ")
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
                    elif ch=="2":
                        if dat[2]==oinst:
                            dat[2] = ninst
                    data[i] = ' '.join(dat)
            open(filename + ".ast", "w").write('!'.join(data))
            continue
        else:
            continue
    elif mn_ch=="4":
        clear()
        print(title)
        print(" .WAV tools")
        print(" 1) .WAV to one string Converter")
        print(" 2) Joiner")
        print(" ")
        tl = input(": ")
        clear()
        if tl=="1":
            clear()
            print(title)
            print(" .WAV to one string Converter")
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
            continue
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
            continue
        else:
            continue
    elif mn_ch=="5": # settings
        clear()
        print(title)
        print(" Settings")
        print(" Pick:")
        print(" [1] Sample pack: " + setting_sample_pack)
        print(" [0] Main menu")
        print(" ")
        ch = input(": ")
        if ch=="1":
            setting_sample_pack = input("New value: ")
        elif ch=="0":
            continue
        else:
            continue
        settings("s")
        continue
    elif mn_ch=="0":
        clear()
        print(title)
        print("Help")
        print(" ")
        print("Default instruments:")
        print(" Sawtooth wave - SWT")
        print(" Sine wave - SIN")
        print(" Triangle wave - TRE")
        print(" Noise - NSE")
        print(" Guitar - GTR")
        print(" Delay - NN")
        print(" ")
        print("FAQ:")
        print(" Error: 'wave.Error: unknown format'")
        print(" Solution: use only 16 bit wav files")
        print(" ")
        wait()
        continue
    else:
        continue
