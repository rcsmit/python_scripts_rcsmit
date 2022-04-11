# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 20:24:20 2020

@author: rcxsm
"""

#https://codeboje.de/pysvg-meets-trundle-turle/

from pysvg.turtle import Turtle, Vector
from pysvg.structure import svg

def testLindenMayer():
    s=svg(0, 0, 2000, 2000)
    commands='F+F-F-FF+F+F-F+F+F-F-FF+F+F-F+F+F-F-FF+F+F-F+F+F-F-FF+F+F-F'
    t=Turtle()
    t.moveTo(Vector(500,250))
    t.penDown()
    angle=90
    distance=40
    for cmd in commands:
        print(cmd)
        if cmd=='F':
            t.forward(distance)
        elif cmd=='+':
            t.right(angle)
        elif cmd=='-':
            t.left(angle)
        print(t.getPosition())
    t.penDown()
    print (t.getXML())
    s=t.addTurtlePathToSVG(s)
    s.save('./testoutput/testTurtle.svg')


if __name__ == '__main__': 
    testLindenMayer()