import cv2
import imutils
import numpy as np
from PIL import Image
import pytesseract
from subprocess import Popen, PIPE

file = 'sudoku2.jpg'

img = cv2.imread(file)

proc = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
proc = cv2.GaussianBlur(proc,(9, 9),0)
proc = cv2.adaptiveThreshold(proc, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 2);
proc = cv2.bitwise_not(proc)

#extracting contour
_, border = cv2.threshold(proc,127,0,cv2.THRESH_BINARY)
cnts = cv2.findContours(proc, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
biggestCnt = None
for c in cnts:
  peri = cv2.arcLength(c, True)
  approx = cv2.approxPolyDP(c, 0.015 * peri, True)
  if len(approx) == 4:
    biggestCnt = approx
    break
cv2.drawContours(border, [biggestCnt], -1, (255, 255, 255), 3)

#finding corners
corners = cv2.goodFeaturesToTrack(border,4,0.01,10)
points = []
for i in corners:
  point = tuple(i.ravel())
  points.append(point)
dist = [ i[0]**2+i[1]**2 for i in points ]
br = points[dist.index(max(dist))]
points.pop(dist.index(max(dist)))
dist = [ i[0]**2+i[1]**2 for i in points ]
tl = points[dist.index(min(dist))]
points.pop(dist.index(min(dist)))
if points[0][0]<points[1][0]:
  bl = points[0]
  tr = points[1]
else:
  bl = points[1]
  tr = points[0]

#finding middle points (sudoku grid coordinates)
def getMidPoints(a,b):
  incx = (b[0] - a[0])/9
  incy = (b[1] - a[1])/9
  values = []
  for i in range(10):
    x = int(a[0] + incx * i)
    y = int(a[1] + incy * i)
    point = (x,y)
    values.append(point)
  return values
  
left = getMidPoints(tl,bl)
right = getMidPoints(tr,br)

both = cv2.addWeighted(cv2.cvtColor(proc,cv2.COLOR_GRAY2BGR), 0.5, cv2.cvtColor(border,cv2.COLOR_GRAY2BGR), 0.5, 0)

for i in left+right:
  cv2.circle(both,i,3,(12,123,255),-1)
  
cv2.circle(both,tl,3,(255,0,0),-1)
cv2.circle(both,tr,3,(0,255,0),-1)
cv2.circle(both,bl,3,(0,255,255),-1)
cv2.circle(both,br,3,(0,0,255),-1)

def getBox(x,y):
  pixelx = left[y][0] + (right[y][0] - left[y][0])*x/9
  pixely = left[y][1] + (right[y][1] - left[y][1])*x/9
  return (int(pixelx),int(pixely))
cv2.rectangle(both,getBox(4,4),getBox(4+1,4+1),(0,255,255),-1)

#digit recognition
digits = np.zeros((9,9),dtype=np.int8)
board = ''
proc = cv2.bitwise_not(proc)
for x in range(9):
  for y in range(9):
    (x1,y1) = getBox(y,x)
    (x2,y2) = getBox(y+1,x+1)
    filename = "tmp/"+str(x)+"_"+str(y)+".bmp"
    cv2.imwrite(filename,proc[y1+5:y2-3,x1+5:x2-3])
    text = pytesseract.image_to_string(Image.open(filename),config='--psm 10 digits')
    text = [ int(letter) for letter in text if letter.isdigit() ]
    if len(text)==0:
      text = 0
    else:
      text = text[0]
    print(text,end="")
    board += str(text)
    digits[x,y] = text
  print('')
  board += '\n'

#solving
with open('tmp/board.txt', 'w') as file:
  file.write(board)
  
process = Popen(["solver/solver.exe", "tmp/board.txt"], stdout=PIPE)
(output, err) = process.communicate()
exit_code = process.wait()
output = output.decode('ascii')
print("SOLUTION:")
#print(output)

sudoku = np.zeros((9,9), dtype=np.int8)
counter = 0
for i in output:
  x = int(counter/9)
  y = int(counter%9)
  if i == '\n':
    print('')
  elif i == '\r':
    pass
  else:
    sudoku[y,x] = int(i)
    counter += 1
    print(i,end='')
  if counter==81:
    break
  
#filling digits
for x in range(9):
  for y in range(9):
    coords = getBox(x,y+1)
    coords = tuple((coords[0]+10, coords[1]-10))
    text = str(sudoku[x,y])
    if digits[y,x]==0:
      cv2.putText(img, text, coords, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
cv2.imshow("both",both)
cv2.imshow("filled",img)
    
cv2.waitKey(0)
cv2.destroyAllWindows()