# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 20:17:26 2020

@author: rcxsm
"""

# https://stackoverflow.com/questions/4071633/python-turtle-module-saving-an-image

from turtle import *  # @UnusedWildImport

import svgwrite

from svg_turtle import SvgTurtle


def draw_spiral():
    fillcolor('blue')
    begin_fill()
    for i in range(20):
        d = 50 + i*i*1.5
        pencolor(0, 0.05*i, 0)
        width(i)
        forward(d)
        right(144)
    end_fill()



def draw_onscreen(draw_func):
    #drawing = svgwrite.Drawing(filename, size=size)
    #drawing.add(drawing.rect(fill='white', size=("100%", "100%")))
    
    s = Turtle.getscreen()
    t = Turtle.Turtle()
  
    Turtle._pen = t
    draw_func()
    


def write_file(draw_func, filename, size):
    drawing = svgwrite.Drawing(filename, size=size)
    drawing.add(drawing.rect(fill='white', size=("100%", "100%")))
    t = SvgTurtle(drawing)
    Turtle._screen = t.screen
    Turtle._pen = t
    draw_func()
    drawing.save()


def main():
    #write_file(draw_spiral, 'example.svg', size=("500px", "500px"))
    draw_onscreen(draw_spiral)
    print('Done.')


if __name__ == '__main__':
    main()