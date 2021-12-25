from __future__ import division

print("Starting...")

from numpy import ceil, linspace, tile, arange, pi, int16, sin, random, zeros
from numpy import abs as npabs
from numpy import max as npmax
import wave, time, sys, os, random, base64, math, struct
from scipy import signal
import soundfile as sf
from soundfile import read as sfread
# Drum library
exec("""\nclass Sine:\n  def __init__(self):\n    self.phase = 0\n  def next(self, freq, pm=0):\n    s = math.sin(self.phase + pm)\n    self.phase = (self.phase + 2 * math.pi * freq / 44100) % (2 * math.pi)\n    return s\ndef linear_env(segs, t):\n  x0 = 0\n  y0 = 0\n  for x1, y1 in segs:\n    if t < x1:\n      return y0 + (t - x0) * ((y1 - y0) / (x1 - x0))\n    x0, y0 = x1, y1\n  return y0\nclass Env:\n  def __init__(self, segs):\n    self.segs = segs\n    self.phase = 0\n  def next(self, scale=1):\n    s = linear_env(self.segs, self.phase)\n    self.phase += scale / 44100\n    return s\ndef kick(samples, dur):\n  o1 = Sine()\n  o2 = Sine()\n  e1 = Env([(0, 1), (0.02, 1), (1, 0)])\n  e2 = Env([(0, 1), (0.01, 0)])\n  for t in range(int(44100 * dur)):\n    o = o1.next(100 * e1.next(2.5), 16 * e2.next() * o2.next(100))\n    samples.append(0.5 * o)\ndef snare(samples, dur):\n  o1 = Sine()\n  o2 = Sine()\n  e1 = Env([(0, 1), (0.2, 0.2), (0.4, 0)])\n  e2 = Env([(0, 1), (0.17, 0)])\n  e3 = Env([(0, 1), (0.005, 0.15), (1, 0)])\n  fb = 0\n  for t in range(int(44100 * dur)):\n    fb = e2.next() * o1.next(100, 1024 * fb)\n    samples.append(0.5 * o2.next(e1.next() * 100 * 2.5, 4.3 * e3.next() * fb))\n""")

title = "Ast-Tracker v1.1.2 (beta)"
prev_data = ""

def clear(): os.system("cls")
clear()
def wait(): os.system("pause")
def delete(file): os.system("del /q " + file)

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
    noise = random.uniform(-1, 1, int(44100/f_c))
    samples = zeros(int(44100*duration_s))
    for i in range(len(noise)):
        samples[i] = noise[i]
    for i in range(len(noise), len(samples)):
        samples[i] = (samples[i-len(noise)]+samples[i-len(noise)-1])/2
    samples = samples / npmax(npabs(samples))
    waveform_quiet = samples * vol
    return int16(waveform_quiet * 32768)

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
    print(" 1) .AST to .WAV converter")
    print(" 2) .WAV to one string")
    print(" 3) .AST editor")
    print(" 4) .AST speed changer")
    print(" ")
    print(" 0) Help")
    print(" ")
    mn_ch = input(": ")
    if mn_ch=="1":
        clear()
        print(title)
        print(" .AST to .WAV converter")
        print(" ")
        sngname = input("Song (only name): ")
        # прочитка
        try:
            sngfile = open(sngname + ".ast", "r")
            astsng = sngfile.read()
            sngfile.close()
        except FileNotFoundError:
            clear()
            print(" File " + sngname + ".ast doesn't exist!")
            wait()
            continue
        i = 0
        astsng = astsng.split("!")
        for section in astsng:
            i = i + 1
            if section!="":
                params = section.split()
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
                if params[0]=="NN" and params[2]!="NSE" and params[2]!="KIK" and params[2]!="SNR":
                    write(sngname + ".wav", sawtooth_gen(1.0, float(params[1]), 0))
                else:
                    if params[2]=="SWT":
                        write(sngname + ".wav", sawtooth_gen(float(params[0]), float(params[1]), float(params[3])))
                    elif params[2]=="SIN":
                        write(sngname + ".wav", sin_gen(float(params[0]), float(params[1]), float(params[3])))
                    elif params[2]=="TRE":
                        write(sngname + ".wav", triangle_gen(float(params[0]), float(params[1]), float(params[3])))
                    elif params[2]=="GTR":
                        write(sngname + ".wav", guitar_gen(float(params[0]), float(params[1]), float(params[3])))
                    elif params[2]=="KIK" or params[2]=="SNR":
                        samples = []
                        if params[2]=="KIK":
                            kick(samples, 0.25)
                        elif params[2]=="SNR":
                            snare(samples, 0.5)
                        prev_data = ""
                        try:
                            obj = wave.open(sngname + ".wav",'r')
                            prev_data = obj.readframes(obj.getnframes())
                            obj.close()
                        except FileNotFoundError:
                            pass
                        obj = wave.open(sngname + ".wav",'w')
                        obj.setnchannels(2)
                        obj.setsampwidth(2)
                        obj.setframerate(44100)
                        if prev_data!="":
                            obj.writeframesraw( prev_data )
                        for sample in samples:
                            waveform_quiet = sample * float(params[3])
                            waveform_ints = int16(waveform_quiet * 32768)
                            obj.writeframesraw( waveform_ints )
                        obj.close()
                    elif params[2]=="NSE":
                        write(sngname + ".wav", noise_gen(float(params[1]), float(params[3])))
                print("Lines: " + str(i) + "/" + str(len(astsng)))
                print("Converted!")
                wait()
                continue
    elif mn_ch=="2":
        clear()
        print(title)
        print(" .WAV to one string Converter")
        print(" ")
        filename = input(".WAV File (only name): ")
        outputfile = input("Output File (*): ")
        try:
            data, fs = sfread(filename + ".wav", dtype='float32')
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
    elif mn_ch=="3":
        clear()
        print(title)
        print(" .AST editor")
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
    elif mn_ch=="4":
        clear()
        print(title)
        print(" .AST Speed changer")
        print(" ")
        filename = input("File (only name): ")
        speed = float(input("Speed (1.0): "))
        try:
            data = open(filename + ".ast", "r").read()
        except FileNotFoundError:
            clear()
            print(" File " + filename + ".ast doesn't exist!")
            wait()
            continue
        f = open(filename + ".ast", "w")
        for i in data.split("!"):
            if i!='':
                temp = i.split(" ")
                f.write("!" + temp[0] + " " + str(float(temp[1]) / speed) + " " + temp[2] + " " + temp[3])
        f.close()
        continue
    elif mn_ch=="0":
        clear()
        print(title)
        print("Help")
        print(" ")
        print("Instruments:")
        print(" Sawtooth wave - SWT")
        print(" Sine wave - SIN")
        print(" Triangle wave - TRE")
        print(" Noise - NSE")
        print(" Guitar - GTR")
        print(" Drum kick - KIK")
        print(" Drum snare - SNR")
        print(" ")
        print(" Delay - NN")
        print(" ")
        print(" ")
        wait()
        continue
    else:
        continue
