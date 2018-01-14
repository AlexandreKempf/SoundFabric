import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile

#####               #####
#####   PARAMETERS  #####
#####               #####


def addfreq(lenSound, duration, freqOn, freqOff, chirpMode, whitenoise):
    freqOn = float(freqOn)
    freqOff = float(freqOff)
    if freqOn == freqOff:
        chirpMode='linear'
    if whitenoise: # For whitenoise sounds
        sound = np.random.random(lenSound)
        sound -= 0.5
    else: # for frequency sounds
        if chirpMode == 'exp':
            b = np.log(freqOff/freqOn) / duration
            a = 2 * np.pi * freqOn / b
            x = np.arange(lenSound)
            delta = x / float(lenSound)
            t = duration * delta
            sound = np.sin(a * np.exp(b * t))
        elif chirpMode == 'linear':
            x = np.arange(lenSound)
            delta = x / float(lenSound)
            t = duration * delta
            sound = np.sin(2 * np.pi * t * (freqOn + (freqOff - freqOn) * delta / 2))
        else:
            print("NANANANA BATMAN ! \n No mode like that !! \n Try again ;)")
    return sound

def soundgenerator(filename,duration, chirpMode, freqOn, freqOff, dbOn, dbOff, whitenoise=False, framerate=192000, transitionDuration=0.01, silenceBefore=0, silenceAfter=0):
    """
    # General parameters
    filename = "sweep 2"
    duration = 3 # in seconds
    framerate = 192000 # in Hz
    transitionDuration = 0.010 # in seconds

    # Frequency parameters
    whitenoise = False
    chirpMode = 'exp'  # 'linear' or 'exp'
    freqOn = 2000 or [2000,4000,8000] # in Hz, list if you want to create chords
    freqOff = 2000 or [2000,4000,8000] # in Hz, list if you want to create chords

    # Amplitude parameters
    dbOn = 80 # in dB
    dbOff = 80 # in dB

    # Silence parameters
    silenceBefore = 0# in seconds
    silenceAfter = 0 # in seconds
    """

    # Input part to convert all the input in the right format  -> Not important
    duration = float(duration)
    framerate = float(framerate)
    transitionDuration = float(transitionDuration)
    whitenoise = bool(whitenoise)
    dbOn = float(dbOn)
    dbOff = float(dbOff)
    silenceBefore = float(silenceBefore)
    silenceAfter = float(silenceAfter)


    # Estimated parameters
    dbRef = 100 + np.log10(np.sqrt(2))*20 # DO NOT TOUCH
    idxStart = int(silenceBefore * framerate)
    idxEnd = int((silenceBefore + duration) * framerate)
    lenFile = int((silenceBefore + duration + silenceAfter) * framerate)
    lenSound = int(duration * framerate)

    #####                             #####
    #####   GENERATE FREQUENCY SOUND  #####
    #####                             #####

    wave = np.zeros(lenFile)

    sound = np.zeros(lenSound)
    if isinstance(freqOn, (list, tuple)):
        if len(freqOn) == len(freqOff):
            for i in np.arange(len(freqOn)):
                sound += addfreq(lenSound, duration, freqOn[i], freqOff[i], chirpMode=chirpMode, whitenoise=whitenoise)
        else:
            print("Problem, the two frequency vectors (On and Off) should have the same size")
            return
    else:
        sound = addfreq(lenSound, duration, freqOn, freqOff, chirpMode=chirpMode, whitenoise=whitenoise)

    sound /= np.std(sound)
    wave[idxStart:idxEnd] = sound

    #####                          #####
    #####   GENERATE DB ENVELOPE   #####
    #####                          #####
    envelope = np.zeros_like(wave)
    envelope[idxStart:idxEnd] = np.linspace(dbOn,dbOff,lenSound)
    envelope = 10**((envelope-dbRef)/20)
    wave *= envelope


    #####                                 #####
    #####   GENERATE SMOOTH TRANSITIONS   #####
    #####                                 #####
    smoothDuration = int(transitionDuration*framerate)
    freqMod = 1/(smoothDuration*4)
    modSin = np.zeros_like(wave)
    modSin[idxStart:idxStart+smoothDuration] = np.linspace(0,1,smoothDuration)
    modSin[idxStart+smoothDuration:idxEnd-smoothDuration] = 1
    modSin[idxEnd-smoothDuration:idxEnd] = np.linspace(1,0,smoothDuration)
    smoothingEnvelope = (np.sin(2*np.pi*(modSin-0.5)/2)+1)/2
    wave *= smoothingEnvelope


    #####                                            #####
    #####   TEST PART FOR AMPLITUDE SIN MODULATION   #####
    #####                                            #####
    #
    # MODHz = 5
    # x = np.linspace(0,duration,lenSound)
    # envelope = np.sin((x*2*np.pi*MODHz)-(np.pi/2))
    # envelope += 1
    # envelope /= 2
    #
    # wave *= envelope




    #####          #####
    #####   SAVE   #####
    #####          #####
    # plt.plot(wave);plt.show()
    wave = np.asarray(wave*(2**15), dtype=np.int16)
    wavfile.write(filename,int(framerate),wave)



freq = np.arange(2,81)[::2]*1000
for fre in freq:
    soundgenerator("80dB_"+ str(fre)+".wav",duration=3, chirpMode='exp', freqOn=fre, freqOff=fre, dbOn=80, dbOff=80, whitenoise=False, framerate=192000, transitionDuration=0.01 ,silenceBefore=0, silenceAfter=0)



# 4*np.exp((np.arange(5)/4.)*np.log(25/4))
