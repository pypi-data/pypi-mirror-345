from mod2.cat import cat 
from mod2.dog import dog1
from mod2.wolf import wolf1

def callback2():
    print("callback2")
    cat.print_cat()

def callback3():
    print("callback3")
    dog1.print_dog() 

def callback4():
    print("callback4")
    wolf1.print_wolf()


if __name__ == '__main__':
    callback3()
    