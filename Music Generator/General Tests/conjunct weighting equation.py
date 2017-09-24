#range = 60-85

lastNote= 72

for i in range(60, 85):
    print(str(i) + ":  " + str(-0.6*(i - (lastNote))**2 + 45)) 
