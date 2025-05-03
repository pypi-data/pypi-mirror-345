import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from pythagore import Pythagore

pythagore = Pythagore()

a = 3
b = 4
hypotenuse = pythagore.hypotenus(a,b) # hypotenus 

if pythagore.is_rectangle(hypotenuse, a, b) == True:
    print("the triangle is indeed right-angled according to the Pythagorean theorem")
else:
    print("the triangle is not a right triangle")

find_missing_side = pythagore.adjacent_side(hypotenuse, a) # 4
if find_missing_side == b:
    print(f"the missing side is b its value and : {find_missing_side}")

print()

print(f"hypotenus : {hypotenuse}\ncoter_a : {a}\ncote_b : {b}")