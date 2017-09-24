#--------------------------------------------------------------------------------------
# Name:         generator.py
# Purpose:      Generate small songs as midi files
#
# Author:       Samuel Bowyer
#
# Created:      19/04/2017
#--------------------------------------------------------------------------------------

from midiutil.MidiFile import MIDIFile
from datetime import datetime
import random, os, pickle

"""
MIDI Standards:
Tone-numbers - all relative to Middle C (C5) which is 60
             - int (0-127)

Duration     - (of notes) measured in beats, length of which is defined by tempo (bpm)
             - float (usually power of 2 (even eg. 0.25 - semi-demi-quaver)
"""

#Create classes and functions
#Used to store track data that can be used to input into midi file at end of program
class Track():
    def __init__(self, trackName, trackNo, channelNo, programNo):
        self.trackName = trackName
        self.trackNo = trackNo
        self.channelNo = channelNo
        self.programNo = programNo

        midi.addTempo(trackNo, channelNo, tempo)
        midi.addTrackName(trackNo, 0, trackName)
        midi.addProgramChange(trackNo, channelNo, 0, programNo)

def choose(items):
    """
    Given a 2D list of options and respective probabilities, in form [option, prob]
    this will return a random option based on the given probabilities.
    """
    sum=0
    for i in items:
        sum += i[1]
    rnd = random.random() * sum
    for i, w in items:
        rnd -= w
        if rnd < 0:
            return i

#Music Theory Setup
def createRhythm(durations, length, overflowLimit=0):
    """
    durations - 2D [option, prob] list
    length - length of time to be covered in beats (float)
    absoluteOverflow - whether chosen duration lengths can sum to more than length (bool)
    overflowLimit - an overflow cannot be more than this length
    """
    beatsLeft = length
    durationOptions = durations[:]  #creates new copy of 'durations', not just another name to reference 'durations' with
    rhythm = []

    while beatsLeft > 0:
        for i in durationOptions:
            if i[0] > (beatsLeft + overflowLimit):
                durationOptions.remove(i)   #remove options which would cause an overflow that is larger than overflowLimit

        durationValue = choose(durationOptions)
        rhythm.append(durationValue)
        beatsLeft -= durationValue

    return rhythm

#Chord Class for storing info of chords in chord progression
class Chord():
    def __init__(self, notes,duration, function):
        self.notes = notes          #list of MIDI notes
        self.duration = duration    #chord duration
        self.function = function    #chord function

#Chord Function class to store info about chord functions and the probability changes they incur
class ChordFuntion():
    def __init__(self, scaleTones, displayName):
        self.scaleTones = scaleTones    #list of possible scale tones whose diatonic chords fit this funciton (all equal probability)
        self.displayName = displayName  #Tonic/Dominant/Subdominant (used in tests)

    def updateNewOptions(self, newOptions):
        self.newOptions = newOptions    #probabilities for the following chord function in the progression

T = ChordFuntion([[1,1],[3,1],[6,1]], "Tonic")
D = ChordFuntion([[5,1],[7,1]], "Dominant")
S = ChordFuntion([[2,1],[4,1]], "Subdominant")

#updateNewOptions not part of __init__() beacuse T, D & S all have to be created for newOptions to reference any objects
T.updateNewOptions([[T, 10], [D, 20], [S, 40]]) #Tonic --> Subdominant
D.updateNewOptions([[T, 40], [D, 10], [S, 20]]) #Dominant --> Tonic
S.updateNewOptions([[T, 20], [D, 40], [S, 10]]) #Subdominant --> Dominant

#Note Class for storing info for each note in the melody
class Note():
    def __init__(self, tone, duration):
        self.tone = tone
        self.duration = duration

#Song class to store (and then pickle) information about each song created
class Song():
    def __init__(self, fileName, timeCreated, tempo, key, jazziness):
        self.fileName = fileName
        self.timeCreated = timeCreated
        self.tempo = tempo
        self.key = key
        self.jazziness = jazziness

    def display(self, singleLine):
        info = "File name: %s      Created: %s      " % (self.fileName, self.timeCreated)
        if not singleLine:
            info += "\n"
        info += "Tempo: %s       Key: %s     Jazziness: %s \n" % (self.tempo, self.key, self.jazziness)
        return info

print("""##################################################

                Music Generator 0.1

               Created by Sam Bowyer

##################################################

""")

isRunning = True

while isRunning:

    menuOption = None
    while menuOption not in ("1", "2","3"):
        menuOption = input("""What would you like to do?

        1. Create a new song
        2. View past songs
        3. Exit

Enter your choice: """)
    print()

    if menuOption == "1":
        #MIDI Setup
        midi=MIDIFile(2, adjust_origin=False) #create MIDI file with 2 tracks (for chords and for melody)

        #Global Variables
        inputs = input("""Enter each of the letters together that you wish to input yourself (e.g. "tkj" for all self-input)
Or leave blank for all random/preset values:
        "t"-tempo  "k"-key  "j"-jazziness
==> """)

        #Set tempo
        tempo = None
        if "t" in inputs:
            while tempo not in range(80,121):
                try:
                    tempo = int(input("Tempo (bpm 80-120): "))
                except ValueError:
                    pass
        else:
            tempo = random.randint(80,120)

        keys = {"C":0, "C#":1, "D":2, "D#":3, "E":4, "F":5, "F#":6, "G":7, "G#":8, "A":9, "A#":10, "B":11}

        key = None
        if "k" in inputs:
            while key not in keys:  # ***in*** only seaches the 'key' before the ':' (in this case the string of the musical key name) of a dictionary, not the value after the ':' (the midi tone value)
                key = input("Key (major only, enter note letter and possibly also a '#' to indicate a sharp): ").upper()
        else:
            key = "C"

        tonicTone = keys[key]


        majorScaleIntervals = [2,2,1,2,2,2,1]
        diatonicTones= [tonicTone]
        for i in range(80): #max number of diatonic tones in MIDI vale range (0-127)
            diatonicTones.append(diatonicTones[-1]+majorScaleIntervals[i%7])

        #Track Setup
        chordTrack = Track("Chords [Bright Acoustic Piano]", 0, 0, 1)
        melodyTrack = Track("Melody [Electric Guitar (Jazz)]", 1, 0, 26)

        #CHORDS
        chordProgression = []

        chordDurations = [[1.0, 20], [2.0, 25], [4.0, 15]]   #[duration (in beats), probability (arbitrary relative units)]

        chordFunctionOptions = [[T, 10], [D, 10], [S, 10]]

        #Jazziness
        jazziness = 1.1 #Arbitrary value so that the while loop is ran at least once if jazziness is chosen for user-input
        if "j" in inputs:
            while jazziness < 0.0 or jazziness > 1.0:
                try:
                    jazziness = float(input("Jazziness (0.0-1.0): "))
                except ValueError:
                    pass
        else:
            jazziness = 0.3

        chordSizeOptions = [[3,None],[4,None],[5,None],[6,None],[7,None]]
        #how many notes in the chord (3-triad, 4-7th, 5-9th)
        #to incorporate jazziness, create exponential function to multiply
        #each weighting by, changing the minimum/maximum of curve for different values for no. of notes
        for i in chordSizeOptions:
            i[1] = (0.5+jazziness)**i[0]

        chordRhythm = createRhythm(chordDurations, 16)

        for i in chordRhythm:
            currentChordFunction = choose(chordFunctionOptions)     #Choose chord function
            chordFunctionOptions = currentChordFunction.newOptions  #Update probabilities of the next function based on what they all lead to

            currentScaleTone = choose(currentChordFunction.scaleTones)  #Choose root note of diatonic chord that fits that function
            currentChordSize = choose(chordSizeOptions)                 #Choose chord size

            root = diatonicTones[diatonicTones.index(tonicTone)+currentScaleTone+23] #find index of key centre, add new root note, add 36 to get to 4th octave, minus one because scale numbers start on 1
            chordTones = [root]
            for note in range(currentChordSize-1):
                chordTones.append(diatonicTones[diatonicTones.index(chordTones[note])+2])   #add two to the last note to get a diatonic third to build up the chord

            chordProgression.append(Chord(chordTones, i, currentChordFunction)) #Add Chord object to list chordProgression

        repeats = 4                     #could be an input in a future version, but no need for this currently
        chordProgression *= repeats     #repeat the chord in chordProgression for **repeats** amount of times

        #add chordProgression info to the midi file
        time = 0    #time since start
        for chord in chordProgression:
            for note in chord.notes:
                midi.addNote(chordTrack.trackNo, chordTrack.channelNo, note, time, chord.duration, random.randint(80, 90))  #add each note of the current chord to the midi file
            time += chord.duration                                                                 #^^^ volume is made random to humanize the sounds

        #Melody
        melody = []

        melodyDurations = [[0.125,10],[0.25,30],[0.5,30],[1.0,25],[2.0,5], [3.0, 5]]

        toneOptions = [[i, 0] for i in range(tonicTone+60, tonicTone+85)]
        #2 octaves of chromatic scale - will add a constant amount of weight to diatonic tones
        #will increase chromatic weight if duration == 0.125

        def toneOptionsUpdate(addedWeight, mustBelongTo):
            """
            updating toneOptions so many times decided to save space by writing a function to do it

            addedWeight - increases probably weighting of certain tones by this amount (float)
            mustBelongTo - but only with tones that are in this particular list
            """

            for tone in toneOptions:
                if tone[0] in mustBelongTo:
                    tone[1] += addedWeight

        toneOptionsUpdate(15, diatonicTones)    #+15 if in major scale
        diatonicToneOptions = toneOptions[:]    #snapshot of toneOptions when notes that are: **in the scale** have been given weight

        oneNoteInMelody = False #bool to check if the melody has one non-rest element. Used later on to deal with lastNote

        overflow = 0
        for chordIndex, chord in enumerate(chordProgression):

            melodyRhythm = []

            if chordIndex == len(chordProgression)-1:   #if this is the final chord
                melodyRhythm = createRhythm(melodyDurations, chord.duration - overflow, 4.0)  #overflowLimit = 4.0 (might as well be limitless)
            else:
                melodyRhythm = createRhythm(melodyDurations, chord.duration - overflow, chordProgression[chordIndex+1].duration) #overflowLimit = the duration of the next chord

            overflow = sum(melodyRhythm) - (chord.duration - overflow)

            chordTones = []
            for i in chordTones:
                chordTones.append((i%12)+tonicTone+60)    #add weighting to chord tones in any octave
                chordTones.append((i%12)+tonicTone+72)    #                   ^^^
                if i%12 == 0:
                    chordTones.append(tonicTone+84)       #so that the highest note possible (84/C7) can have its weight increased if the chord includes a C note

            toneOptionsUpdate(15, chordTones)  #+15 if in chord
            harmonicToneoptions = toneOptions[:]   #snapshot of toneOptions when notes that are: **in the scale AND in the chord** have been given weight

            for noteDuration in melodyRhythm:
                if noteDuration == 0.125:
                    toneOptionsUpdate(5, range(tonicTone+60, tonicTone+85)) #+5 to all (even chromatic notes) if a semi-demi-hemi-quaver (dont want to stay on chrom note too long)

                if oneNoteInMelody:

                    for i in toneOptions:
                        if i[0] in diatonicTones:
                            addedWeight = -0.6*(i[0]-lastTone)**2 + 45
                            if i[0] == lastTone:
                                addedWeight *= 0.5

                            i[1] += addedWeight
                            if i[1] < 0:    #addedWeight can go -ve so need to check that the probability >= 0 or choose() might be broken
                                i[1] = 0

                totalWeight = 0
                for i in toneOptions:
                    totalWeight += i[1]
                averageWeight = totalWeight/len(toneOptions)

                toneOptions.append(["rest",averageWeight])  #add the option of a rest with the average probability of all the tone options

                newTone = choose(toneOptions)
                if newTone != "rest":
                    oneNoteInMelody = True
                    lastTone = newTone

                melody.append(Note(newTone, noteDuration))   #append a new Note object to the melody. Possibility of Note.tone == "rest" dealt with later in code. No problems with this for now as Note.tone type not defined yet
                toneOptions = harmonicToneoptions[:]   #Update tone options to before chromatic notes could've been given any weight

            toneOptions = diatonicToneOptions[:]   #Update toneOptions to before harmonic notes (in the chord) have been given weight so the weights can be added for the notes in the next chord

        #add melody info to the midi file
        time = 0
        for note in melody:
            if note.tone != "rest": #rests will not be added, but the next note will be added in at the correct time because time is still updated 2 lines down
                midi.addNote(melodyTrack.trackNo, melodyTrack.channelNo, note.tone, time, note.duration, random.randint(95, 105))   #add each note of the melody one-by-one to the midi file
            time += note.duration                                                                    #^^^ volume is made random to humanize the sounds

        #export the midi file
        testNo = 0
        with open("history.txt","r") as f:
            testNo = len(f.readlines())  #find out what number test this is


        fileName = "Test%s.mid" % (testNo+1)

        illegalCharacters = ('\\', '/', ':', '*', '?', '"', '<', '>', '|')  #characters not allowed by Windows'/MacOS's file system (NTFS)
        safeCustomFileName = False
        while not safeCustomFileName:
            safeCustomFileName = True #so that the loop isnt repeated unless an illegal character is found

            customFileName = input("\nFile will be called '%s'.\nEnter a custom filename (without \\ / : * ? \" < > | )or just press enter to keep this name:\n" % fileName)

            if customFileName == "":
                break   #to ensure the follwing for loop won't run if it doesn't need to be (the whole while loop will be stopped)

            for i in illegalCharacters:
                if i in customFileName:
                    safeCustomFileName = False
                    break   #stops for loop as soon as one illegal character is found

        if customFileName != "":
            fileName = customFileName

        d = datetime.now()
        newSong = Song(fileName, "%s/%s/%s  %s:%s:%s" % (d.day, d.month, d.year, d.hour, d.minute, d.second), tempo, key, jazziness)

        with open("GeneratorTests\\"+fileName, "wb") as f:    #name the output midi file, including the test number in the file name
            midi.writeFile(f) #finally write the output midi file

        with open("history.txt","a") as f:  #open as "a" -- append. So that previous records are not destroyed
            f.write(newSong.display(True))  #add one to the testNo text file so the next midi file can be named with a test number that is one larger than the one just created

        history = []
        with open("pickledHistory.pkl", "rb") as f:
             while True:
                try:
                     history.append(pickle.load(f))
                except EOFError:    #keep loading until an error is thrown because there are no more objects to load
                    break

        with open("pickledHistory.pkl", "wb") as f:
            for i in history:
                pickle.dump(i, f)   #have to repickle every previous song or they will be lost
            pickle.dump(newSong, f) #pickle newsong object to store history info better

        print("\nSong created.")
        print(newSong.display(False))

        playback = None

        while playback not in ("y","n"):
            playback = input("\nPlay the new piece? (y/n): ").lower()

        if playback == "y":
            print("Playing %s..." % newSong.fileName)
            os.startfile("GeneratorTests\\"+fileName)

    if menuOption == "2":

        history = []
        with open("pickledHistory.pkl", "rb") as f:
             while True:
                try:
                     history.append(pickle.load(f))
                except EOFError:    #keep loading until an error is thrown because there are no more objects to load
                    break

        for songNo, song in enumerate(history):
            print(str(songNo+1).zfill(2) + "    --    " + song.display(True))   #.zfill(x) adds leading zeroes so the string is always x digits long

        playback = True
        while playback:

            songNo = None
            while songNo not in range(len(history)+1):
                try:
                    songNo = int(input("Enter the number of the file you wish to open (or 0 to go back to the menu): "))
                except ValueError:
                    pass    #while loop will repeat and program will not be stopped because of this error

            if songNo != 0:
                chosenSong = history[songNo-1]
                print("Playing %s..." % chosenSong.fileName)
                os.startfile("GeneratorTests\\"+chosenSong.fileName)

                while playback not in ("y","n"):
                    playback = input("\nPlay another piece? (y/n): ").lower()

                if playback == "y":
                    playback = True
                else:
                    playback = False

            else:
                playback = False

        print()

    if menuOption == "3":

        isRunning = False

input("\nPress the Enter key to exit.")
