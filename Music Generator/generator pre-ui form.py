from midiutil.MidiFile import MIDIFile
import random

"""
MIDI Standards:
Tone-numbers - all relative to Middle C (C5) which is 60
             - int (0-127)

Duration     - (of notes) measured in beats, length of which is defined by tempo (bpm)
             - float (usually power of 2 (even eg. 0.25 - semi-demi-quaver)
"""

#MIDI Setup
midi=MIDIFile(2, adjust_origin=False) #create MIDI file with 2 tracks (for chords and for melody)

#Global Variables
tempo = random.randint(80,120)
key = "C"       #major
tonicTone = 48  #C4
majorScaleIntervals = [2,2,1,2,2,2,1]
diatonicTones= [0]
for i in range(70):
    diatonicTones.append(diatonicTones[-1]+majorScaleIntervals[i%7])

#Track Setup
#Used to store track data thaty can be used to input into midi file at end of program
class Track():
    def __init__(self, trackName, trackNo, channelNo, programNo):
        self.trackName = trackName
        self.trackNo = trackNo
        self.channelNo = channelNo
        self.programNo = programNo

        midi.addTempo(trackNo, channelNo, tempo)
        midi.addTrackName(trackNo, 0, trackName)
        midi.addProgramChange(trackNo, channelNo, 0, programNo)

chordTrack = Track("Chords [Bright Acoustic Piano]", 0, 0, 1)
melodyTrack = Track("Melody [Electric Guitar (Jazz)]", 1, 0, 26)


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
def createRhythm(durations, length, overflow):
    """
    durations - 2D [option, prob] list
    length - length of time to be covered in beats (float)
    overflow - whether chosen duration lengths can sum to more than length (bool)
    """
    beatsLeft = length
    durationOptions = durations[:]  #creates new copy of 'durations', not just another name to reference 'durations' with
    rhythm = []

    while beatsLeft > 0:
        if not overflow:
            for i in durationOptions:
                if i[0] > beatsLeft:
                    durationOptions.remove(i)

        durationValue = choose(durationOptions)
        rhythm.append(durationValue)
        beatsLeft -= durationValue

    return rhythm


"""
CHORDS
"""
#Chord Function class to store info about chord functions and the probability changes they incur
class ChordFuntion():
    def __init__(self, scaleTones, displayName):
        self.scaleTones = scaleTones
        self.displayName = displayName
    def updateNewOptions(self, newOptions):
        self.newOptions = newOptions

T = ChordFuntion([[1,1],[3,1],[6,1]], "Tonic")
D = ChordFuntion([[5,1],[7,1]], "Dominant")
S = ChordFuntion([[2,1],[4,1]], "Subdominant")

T.updateNewOptions([[T, 10], [D, 20], [S, 40]]) #Tonic --> Subdominant
D.updateNewOptions([[T, 40], [D, 10], [S, 20]]) #Dominant --> Tonic
S.updateNewOptions([[T, 20], [D, 40], [S, 10]]) #Subdominant --> Dominant

#Chord Class for storing info of chords in chord progression
class Chord():
    def __init__(self, notes,duration, function):
        self.notes = notes          #list of MIDI notes
        self.duration = duration    #chord duration
        self.function = function    #chord function

"""DONT LEAVE IN FUNCTION/THIS FORMAT - MOVE TO MAIN CODE FLOW (TEMPORARILY IN DEF B/C EASY FORMAT FOR NOW)"""
def createChordProgression(rhythm):

    chordProgression = []

    initialChordFunctionOptions = [[T, 10], [D, 10], [S, 10]]
    chordFunctionOptions = initialChordFunctionOptions[:]

    #AS INPUT \/\/\/
    jazziness = 0.3

    chordSizeOptions = [[3,None],[4,None],[5,None],[6,None],[7,None]]
    #how many notes in the chord (3-triad, 4-7th, 5-9th)
    #to incorporate jazziness, create exponential(?) function to multiply
    #each weighting by, changing the minimum/maximum of curve for different values for no. of notes
    for i in chordSizeOptions:
        i[1] = (0.5+jazziness)**i[0]


    for i in chordRhythm:
        currentChordFunction = choose(chordFunctionOptions)     #Choose chord function
        chordFunctionOptions = currentChordFunction.newOptions  #Update probabilities of the next function based on what they all lead to

        currentScaleTone = choose(currentChordFunction.scaleTones)  #Choose root note of diatonic chord that fits that function
        currentChordSize = choose(chordSizeOptions)                 #Choose chord size

        root = diatonicTones[diatonicTones.index(tonicTone)+currentScaleTone-1] #find index of key centre, add new root note, minus one (b/c scale numbers start on 1)
        chordTones = [root]
        for note in range(currentChordSize-1):
            chordTones.append(diatonicTones[diatonicTones.index(chordTones[note])+2])   #add two to the last note to get a diatonic third to build up the chord

        chordProgression.append(Chord(chordTones, i, currentChordFunction)) #Add Chord object to list chordProgression

    return chordProgression

"""
MELODY
"""

#Note Class for storing info for each note in the melody
class Note():
    def __init__(self, tone, duration):
        self.tone = tone
        self.duration = duration


def createMelody(chordProgression, chordRhythm):

    melody = []

    initialMelodyDurations = [[0.125,10],[0.25,30],[0.5,30],[1.0,25],[2.0,5], [3.0, 5]]
    melodyDurations = initialMelodyDurations[:]

    toneOptions = [[i, 0] for i in range(60, 85)]
    #2 octaves of chromatic scale - will add a constant amount of weight to diatonic tones
    #will increase chromatic weight if duration == 0.125


    def toneOptionsUpdate(addedWeight, mustBelongTo):
        """
        updating toneOptions so many times decided to safe space by writing a functio to do it

        addedWeight - increases probably weighting of certain tones by this amount (float)
        mustBelongTo - but only with tones that are in this particular list
        """

        for tone in toneOptions:
            if tone[1] in mustBelongTo:
                tone[1] += addedWeight

    toneOptionsUpdate(15, diatonicTones)    #+15 if in major scale
    diatonicToneOptions = toneOptions[:]    #snapshot of toneOptions when notes that are: **in the scale** have been given weight

    overflow = 0
    for chord in chordProgression:
        melodyRhythm = createRhythm(melodyDurations, chord.duration - overflow, True)
        overflow = sum(melodyRhythm) - chord.duration

        chordTones = []
        for i in chordNotes:
            chordTones.append((i%12)+60)    #add weighting to chord tones in any octave
            chordTones.append((i%12)+72)    #                   ^^^

        toneOptionsUpdate(15, chordTones)  #+15 if in chord
        harmonicToneoptions = toneOptions   #snapshot of toneOptions when notes that are: **in the scale AND in the chord** have been given weight

        for note in melodyRhythm:
            if note == 0.125:
                toneOptionsUpdate(5, range(60, 85)) #+5 to all (even chromatic notes) if a semi-demi-hemi-quaver (dont want to stay on chromatic note too long)

            if len(melody != 0):
                lastNote = melody[len(melody)-1].tone

            """
            #################################### TODO (DONE) ######################################
            Add function to increase weighting of conjunct tones
            Maybe use negative parabola with maximum's x value on lastNote


            -(0.25x-(lastNote-72))^2 + 25 ???
            maybe change c or 0.?x (a) to decrease disparity in added weighting (makes it flatter)


            Use another script to find the optimum a & c of the equation
            #######################################################################################
            """

            for i in toneOptions:
                if i[0] in diatonicTones:
                    addedWeight = -0.6*(i-lastNote)**2 + 45
                    if i == lastNote:
                        addedWeight *= 0.5

                    i[1] += addedWeight
                    if i[1] < 0:    #addedWeight can go -ve so need to check prob >= 0 or choose() can be broken
                        i[1] = 0


            melody.append(Note(choose(toneOptions), choose(melodyDurations)))   #append a new Note object to the melody
            toneOptions = harmonicToneoptions   #Update tone options to before chromatic notes could've been given any weight

        toneOptions = diatonicToneOptions   #Update toneOptions to before harmonic notes (in the chord) have been given weight so the weights can be added for the notes in the next chord

    return melody


#midiConvert

#chord
chordDurations = [[1.0, 20], [2.0, 25], [4.0, 15]]   #[duration (in beats), probability (arbitrary relative units)]
chordRhythm = createRhythm(chordDurations, 16, False)
chordProgression = createChordProgression(chordRhythm)
repeats = 4 #input
chordProgression *= repeats     #repeat the chord in chordProgression for **repeats** amount of times
time = 0    #time since start
for chord in chordProgression:
    for note in chord.notes:
        midi.addNote(chordTrack.trackNo, chordTrack.channelNo, note, time, chord.duration, random.randint(80, 90))  #add each note of the current chord to the midi file
    time += chord.duration


#melody
melody = createMelody(chordProgression, chordRhythm)
time = 0
for note in melody:
    midi.addNote(melodyTrack.trackNo, melodyTrack.channelNo, note.tone, time, note.duration, random.randint(95, 105))   #add each note of the melody one-by-one to the midi file
    time += note.duration

testNo = 0
with open("testNo.txt","r") as f:
    testNo = int(f.read())  #find out what number test this is


with open("Test%s.mid" % (testNo), "wb") as output_file:    #name the output midi file, including the test number in the file name
    midi.writeFile(output_file) #finally write the output midi file


with open("testNo.txt","w") as f:
    f.write(str(testNo+1))  #add one to the testNo text file so the next midi file can be named with a test number that is one larger than the one just created

input()
