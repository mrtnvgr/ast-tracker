import numpy as np
import wave, time, sys, os, random, base64
import soundfile as sf
title = "Ast-Tracker v1.0.0 (beta)"

# A_c: Amplitude of the sawtooth
A_c = 0.3
prev_data = ""

def clear(): os.system("cls")

# sawtooth_gen(990.0, 5.0, 1)
def sawtooth_gen(f_c, duration_s, vol):
    period_c = 1.0 / f_c
    periods_in_duration = int(np.ceil(duration_s / period_c))
    samples_per_period = int(np.ceil(period_c * 44100))
    sawtooth_period = np.linspace(1.0, -1.0, samples_per_period)
    tiled_sawtooth = np.tile(sawtooth_period, periods_in_duration)
    samples_in_duration = int(np.ceil(duration_s * 44100))
    waveform = tiled_sawtooth[:samples_in_duration]
    waveform *= A_c
    waveform_quiet = waveform * vol
    waveform_ints = np.int16(waveform_quiet * 32768)
    return(waveform_ints)

# sin_gen(990.0, 5.0, 1)
def sin_gen(f_c, duration_s, vol):
    t_samples = np.arange(44100 * duration_s)
    waveform = np.sin(2 * np.pi * f_c * t_samples / 44100)
    waveform_quiet = waveform * vol
    waveform_ints = np.int16(waveform_quiet * 32768)
    return(waveform_ints)

# noise_gen(5.0, 1.0)
def noise_gen(duration_s, vol):
    pure = np.linspace(0, 1, int(duration_s) * 44100)
    noise = np.random.normal(0, 1, pure.shape)
    signal = pure + noise
    waveform_quiet = signal * vol
    waveform_ints = np.int16(waveform_quiet * 32768)
    return(waveform_ints)

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

# ГЛАВНОЕ МЕНЮ
while True:
    clear()
    print(title)
    print(" 1) .AST to .WAV Converter")
    print(" 2) .WAV to OneString")
    print(" 3) .AST Editor")
    print(" ")
    mn_ch = input(": ")
    if mn_ch=="1":
        mode = "SAVER"
        clear()
        print(title)
        print(" .AST to .WAV Converter")
        print(" ")
        break
    elif mn_ch=="2":
        clear()
        print(title)
        print(" .WAV to OneString Converter")
        print(" ")
        filename = input(".WAV File (only name): ")
        outputfile = input("Output File (*): ")
        try:
            data, fs = sf.read(filename + ".wav", dtype='float32')
        except FileNotFoundError:
            print("Not found.")
        st = open(outputfile, "w")
        a = 'exec("""import sounddevice as sd\\nimport numpy as np\\nimport base64\\nsd.play(np.frombuffer(base64.decodebytes(b"' + base64.b64encode(data).decode() + '"), dtype=np.float64), 44100)""")'
        st.write(a)
        st.close()
    elif mn_ch=="3":
        clear()
        print(" .AST Editor")
        print(" ")
        file = input("File (only name): ")
        oldstuff = ""
        while True:
            os.system("cls")
            try:
                f = open(file + ".ast", "r")
                oldstuff = f.read()
                f.close()
            except:
                pass
            print(" Current File: " + file + ".ast")
            print("[NOTE] [LENGTH] [INSTR] [VOL]")
            for i in oldstuff.split("!")[-10:]:
                print(i) # 10 last elems
            print(" ")
            ch = input("Undo last line? (empty-no)|(main menu-mm): ")
            if ch=="":
                note = input("NOTE: ")
                length = input("LENGTH: ")
                inst = input("INST (SWT,SIN,NSE) (NN-delay): ")
                vol = input("VOLUME: ")
                f = open(file + ".ast", "w")
                f.write(oldstuff + "!" + note + " " + length + " " + inst + " " + vol)
            elif ch=="mm":
                break
            else:
                f = open(file + ".ast", "w")
                f.writelines("!".join(oldstuff.split('!')[:-1]))
            f.close()
    else:
        sys.exit()

sngname = input("Song (only name): ")
# прочитка
sngfile = open(sngname + ".ast", "r")
asfsng = sngfile.read()
sngfile.close()

i = 0
asfsng = asfsng.split("!")
for section in asfsng:
    i = i + 1
    if section!="":
        params = section.split()
        # NOTE CONVERTER START
        if params[0]=="C2":
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
        # NOTE CONVERTER END

        if mode=="SAVER":
            if params[0]=="NN" and params[2]!="NSE":
                write(sngname + ".wav", sawtooth_gen(1.0, float(params[1]), float(params[3])))
            else:
                if params[2]=="SWT":
                    write(sngname + ".wav", sawtooth_gen(float(params[0]), float(params[1]), float(params[3])))
                elif params[2]=="SIN":
                    write(sngname + ".wav", sin_gen(float(params[0]), float(params[1]), float(params[3])))
                elif params[2]=="NSE":
                    write(sngname + ".wav", noise_gen(float(params[1]), float(params[3])))
                else:
                    pass
        clear()
        print("Lines: " + str(i) + "/" + str(len(asfsng)))
