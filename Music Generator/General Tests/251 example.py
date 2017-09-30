from midiutil.MidiFile import MIDIFile

degrees  = [60, 62, 64, 65, 67, 69, 71, 72] # MIDI note number
track    = 0
channel  = 0
time     = 0   # In beats
duration = 0.25  # In beats
tempo    = 60  # In BPM
volume   = 100 # 0-127, as per the MIDI standard

MyMIDI = MIDIFile(2) # One track, defaults to format 1 (tempo track
                     # automatically created)
MyMIDI.addTempo(track,time, tempo)


track   = 0
channel = 0
time    = 0 # Two beats into the composition
program = 1 # A Cello

MyMIDI.addProgramChange(track, channel, time, program)

#c major chord
dmin = [62, 65, 69]
for pitch in dmin:
    MyMIDI.addNote(track, channel, pitch, time=0, duration=2, volume=99)

g7 = [67, 71, 74, 77]
for pitch in g7:
    MyMIDI.addNote(track, channel, pitch, time=2, duration=2, volume=99)

cmaj = [60, 64, 67]
for pitch in cmaj:
    MyMIDI.addNote(track, channel, pitch, time=4, duration=4, volume=99)


"""
for pitch in degrees:
    MyMIDI.addNote(1, 0, pitch, time, duration, volume)
    time = time + duration
"""
#MyMIDI.addProgramChange(1, 0, 0, 60)
with open("251.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
