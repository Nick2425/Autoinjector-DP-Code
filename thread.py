import sys  
import threading
import time

num = 0

def detection():
    global num
    num+=1
    print(num)
    time.sleep(1)
def even_or_odd():
    global num
    time.sleep(3)
    if num&1==1:
        print("odd")
    if num&1==0:
        print("even")
detection = threading.Thread(target=detection)
main = threading.Thread(target=even_or_odd)

detection.run()
main.run()