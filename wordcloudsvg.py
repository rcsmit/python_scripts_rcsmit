#!/usr/bin/env python
"""
Using custom colors
===================
Using the recolor method and custom coloring functions.
"""

import numpy as np
from PIL import Image
from os import path

# Recently for me, following 2 lines required on osX per internet
# ...because my conda environment is messed up, or something else...
import matplotlib
matplotlib.use("TKAgg")

import matplotlib.pyplot as plt
import os
import random

from wordcloud import WordCloud, STOPWORDS

from tempfile import NamedTemporaryFile
import urllib

def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

# Adobe Illustrator doesn't recognize hsl(), so...
def RGB_grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "rgb({0}, {0}, {0})".format(random.randint(128, 255))

# dictionary of typefaces to play around with
theFonts = {
        'Roboto':['https://github.com/google/fonts/tree/master/apache/roboto/Roboto%5Bwdth%2Cwght%5D.ttf','https://fonts.googleapis.com/css?family=Roboto', '\'Roboto\''],

        'Roboto Slab':['https://github.com/googlefonts/robotoslab/tree/master/fonts/static/RobotoSlab-Regular.ttf','https://fonts.googleapis.com/css?family=Roboto+Slab', '\'Roboto Slab\', serif'],

        'Roboto Slab Bold':['https://github.com/googlefonts/robotoslab/tree/master/fonts/static/RobotoSlab-Bold.ttf','https://fonts.googleapis.com/css?family=Roboto+Slab:700', '\'Roboto Slab\', serif'],

        'Press Start 2p':['https://github.com/google/fonts/tree/master/ofl/pressstart2p/PressStart2P-Regular.ttf', 'https://fonts.googleapis.com/css?family=Press+Start+2P', '\'Press Start 2p\', cursive'],

        'Pacifico':['https://github.com/google/fonts/tree/master/ofl/pacifico/Pacifico-Regular.ttf', 'https://fonts.googleapis.com/css?family=Pacifico', '\'Pacifico\', cursive'],

        'Oswald':['https://github.com/google/fonts/tree/master/ofl/oswald/static/Oswald-Medium.ttf', 'https://fonts.googleapis.com/css?family=Oswald:500', '\'Oswald\', sans-serif'],

        'Black Ops One':['https://github.com/google/fonts/tree/master/ofl/blackopsone/BlackOpsOne-Regular.ttf', 'https://fonts.googleapis.com/css?family=Black+Ops+One', '\'Black Ops One\', cursive'],

        'Dokdo':['https://github.com/google/fonts/tree/master/ofl/dokdo/Dokdo-Regular.ttf', 'https://fonts.googleapis.com/css?family=Dokdo', '\'Dokdo\', cursive'],

        'Special Elite':['https://github.com/google/fonts/tree/master/apache/specialelite/SpecialElite-Regular.ttf', 'https://fonts.googleapis.com/css?family=Special+Elite', '\'Special Elite\', cursive'],

        'Iceland':['https://github.com/google/fonts/tree/master/ofl/iceland/Iceland-Regular.ttf', 'https://fonts.googleapis.com/css?family=Iceland', '\'Iceland\', cursive'],

        'Libre Barcode 39 Text':['https://github.com/google/fonts/tree/master/ofl/librebarcode39text/LibreBarcode39Text-Regular.ttf', 'https://fonts.googleapis.com/css?family=Libre+Barcode+39+Text', '\'Libre Barcode 39 Text\', cursive'],

        'Zilla Slab Highlight':['https://github.com/google/fonts/tree/master/ofl/zillaslabhighlight/ZillaSlabHighlight-Regular.ttf', 'https://fonts.googleapis.com/css?family=Zilla+Slab+Highlight', '\'Zilla Slab Highlight\', cursive'],

        'Zilla Slab Highlight Bold':['https://github.com/google/fonts/tree/master/ofl/zillaslabhighlight/ZillaSlabHighlight-Bold.ttf', 'https://fonts.googleapis.com/css?family=Zilla+Slab+Highlight:700', '\'Zilla Slab Highlight\', cursive'],

        'ZCOOL KuaiLe':['https://github.com/google/fonts/tree/master/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf', 'https://fonts.googleapis.com/css?family=ZCOOL+KuaiLe', '\'ZCOOL KuaiLe\', cursive'],

        'Fredericka the Great':['https://github.com/google/fonts/tree/master/ofl/frederickathegreat/FrederickatheGreat-Regular.ttf', 'https://fonts.googleapis.com/css?family=Fredericka+the+Great', '\'Fredericka the Great\', cursive'],

        'Geo':['https://github.com/google/fonts/tree/master/ofl/geo/Geo-Regular.ttf', 'https://fonts.googleapis.com/css?family=Geo', '\'Geo\', sans-serif'],

        'Stalemate':['https://github.com/google/fonts/tree/master/ofl/stalemate/Stalemate-Regular.ttf', 'https://fonts.googleapis.com/css?family=Stalemate', '\'Stalemate\', cursive'],

        'Amita':['https://github.com/google/fonts/tree/master/ofl/amita/Amita-Regular.ttf', 'https://fonts.googleapis.com/css?family=Amita', '\'Amita\', cursive'],

        'Delius Unicase':['https://github.com/google/fonts/tree/master/ofl/deliusunicase/DeliusUnicase-Regular.ttf', 'https://fonts.googleapis.com/css?family=Delius+Unicase', '\'Delius Unicase\', cursive'],

        'Amatic SC':['https://github.com/google/fonts/tree/master/ofl/amaticsc/AmaticSC-Regular.ttf', 'https://fonts.googleapis.com/css?family=Amatic+SC', '\'Amatic SC\', cursive'],

        'Amatic SC Bold':['https://github.com/google/fonts/tree/master/ofl/amaticsc/AmaticSC-Bold.ttf', 'https://fonts.googleapis.com/css?family=Amatic+SC:700', '\'Amatic SC\', cursive'],

        'Raleway Dots':['https://github.com/google/fonts/tree/master/ofl/ralewaydots/RalewayDots-Regular.ttf', 'https://fonts.googleapis.com/css?family=Raleway+Dots', '\'Raleway Dots\', cursive'],

        'Lusitana':['https://github.com/google/fonts/tree/master/ofl/lusitana/Lusitana-Regular.ttf', 'https://fonts.googleapis.com/css?family=Lusitana', '\'Lusitana\', serif'],

        'Anton':['https://github.com/google/fonts/tree/master/ofl/anton/Anton-Regular.ttf', 'https://fonts.googleapis.com/css?family=Anton', '\'Anton\', sans-serif'],

        'Audiowide':['https://github.com/google/fonts/tree/master/ofl/audiowide/Audiowide-Regular.ttf', 'https://fonts.googleapis.com/css?family=Audiowide', '\'Audiowide\', cursive'],

        'Stalinist One':['https://github.com/google/fonts/tree/master/ofl/stalinistone/StalinistOne-Regular.ttf', 'https://fonts.googleapis.com/css?family=Stalinist+One', '\'Stalinist One\', cursive'],

        'Mountains of Christmas':['https://github.com/google/fonts/tree/master/apache/mountainsofchristmas/MountainsofChristmas-Bold.ttf', 'https://fonts.googleapis.com/css?family=Mountains+of+Christmas:700', '\'Mountains of Christmas\', cursive;font-weight:bold'],

        'Permanent Marker':['https://github.com/google/fonts/tree/master/apache/permanentmarker/PermanentMarker-Regular.ttf', 'https://fonts.googleapis.com/css?family=Permanent+Marker', '\'Permanent Marker\', cursive'],

        'Syncopate Bold':['https://github.com/google/fonts/tree/master/apache/syncopate/Syncopate-Bold.ttf', 'https://fonts.googleapis.com/css?family=Syncopate:700', '\'Syncopate\', sans-serif;font-weight:bold'],

        'Crushed':['https://github.com/google/fonts/tree/master/apache/crushed/Crushed-Regular.ttf', 'https://fonts.googleapis.com/css?family=Crushed', '\'Crushed\', cursive'],

        'WeePeople':['https://github.com/propublica/weepeople/tree/master/weepeople.ttf', 'http://propublica.github.io/weepeople/weepeople.css', '\'WeePeople\''],
#        '':['', '', ''],
           }
'''
Stalinist One ttf file on github is not the same as the one
served by google fonts.
Black Ops One has a reported bug that affects uppercase "R"
https://github.com/google/fonts/issues/1131
'''
Typeface = 'Roboto'
#github_font_URL = theFonts[Typeface][0] + '?raw=true'
github_font_URL = theFonts[Typeface][0]
google_font_URL = theFonts[Typeface][1]
google_font_family = theFonts[Typeface][2]

#github_mask_URL = 'https://github.com/amueller/word_cloud/tree/master/examples/stormtrooper_mask.png' + '?raw=true'
github_mask_URL = 'https://github.com/amueller/word_cloud/tree/master/examples/stormtrooper_mask.png'

#github_text_URL = 'https://github.com/amueller/word_cloud/tree/master/examples/a_new_hope.txt' + '?raw=true'
github_text_URL = 'C:\\Users\\rcxsm\\Documents\\pyhton_scripts\\in\\WhatsApp-chat met Go ABCDE Joost.txt'
print (github_font_URL)
fontFILE = NamedTemporaryFile(delete=False, suffix='.ttf')
response = urllib.request.urlopen(github_font_URL)
fontFILE.write(response.read())
fontFILE.close()



textFILE = NamedTemporaryFile(delete=False, suffix='.txt')
response = urllib.request.urlopen(github_text_URL)
textFILE.write(response.read())
textFILE.close()

# read the mask image

# Height and Width should match the dimensions of the mask image
Height = 3000
Width = 2000
Background_Color = 'white'


text  = open('workvalues.txt',  encoding='utf8').read()

# adding movie script specific stopwords
stopwords = set(STOPWORDS)
stopwords.add("int")
stopwords.add("ext")

'''
The background color could be set in the svg style element.
svg { background-color: YOUR_COLOR_HERE; }
But the entire browser page will be colored.
Using a colored rect makes the result match the png produced
by a_new_hope.py
'''
# kerning/ligature settings don't always have an effect, but sometimes they do,
# so i go ahead and specify "none" just in case...
# https://www.w3.org/TR/css-fonts-3/#font-kerning-prop
# https://www.w3.org/TR/css-fonts-3/#font-variant-ligatures-prop
print ("""<svg width="{0}" height="{1}" xmlns="http://www.w3.org/2000/svg">
    <defs><style type="text/css">
    @import url("{2}");
    text {{font-family: {3};
    font-kerning:none;
    font-variant-ligatures:none}}
    </style></defs>""".format(Width, Height, google_font_URL, google_font_family))

# SVG background rectangle - not necessary if background is white.
print ("<rect width=\"100%\" height=\"100%\" fill=\"{}\"/>".format(Background_Color))

#wc = WordCloud(max_words=1000, mask=mask, stopwords=stopwords, margin=10, font_path=fontFILE.name, color_func=grey_color_func, background_color=Background_Color, random_state=1).generate(text)
wc = WordCloud(max_words=1000, stopwords=stopwords, margin=10, collocations=False, color_func=grey_color_func, background_color=Background_Color, random_state=1).generate(text)

print ('</svg>')

plt.title("Custom colors")
plt.imshow(wc,interpolation="bilinear")
wc.to_file('C:\\a_new_hope_' + Typeface.lower().replace(" ", "_") + '.png')
plt.axis("off")
plt.show()