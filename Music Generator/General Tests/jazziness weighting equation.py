chord=[9,6,4,3,2]
notes=[3,4,5,6,7]

"""
def q(j):
  for x in notes:
    print(-((0.5*x)**2)-5)
"""

def e(j):
  coefficients = []
  for x in notes:
    coefficients.append((0.5+j)**x)
    
  for c in coefficients:
    print(c)
  
  comparison = coefficients[0]/coefficients[4]
  
  print()
  print("3:7 = ",comparison)
  print("7:3 = ", 1/comparison)

for i in range(11):
  j=float(i)/10
  print("j=",j)
  e(j)
  print()
