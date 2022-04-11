
"""
Minimal Example
===============
Generating a square wordcloud from the US constitution using default arguments.
"""

import os

from os import path
from wordcloud import WordCloud

import matplotlib
matplotlib.use('SVG') #set the backend to SVG
import matplotlib.pyplot as plt


# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
#d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# Read the whole text.
#text = open(path.join(d, 'meditation.txt',  encoding="Latin-1")).read()
#text = open('meditation.txt',  encoding='utf8').read()
text  = open('workvalues.txt',  encoding='utf8').read()

#Generate a word cloud image
wordcloud = WordCloud(collocations=False).generate(text)

# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

# lower max_font_size
wordcloud = WordCloud(max_font_size=40, collocations=False).generate(text)
#max_words=1000, stopwords=stopwords, margin=10, , color_func=grey_color_func, background_color=Background_Color, random_state=1


wordcloud_svg = wordcloud.to_svg(embed_font=True)
f = open("filename.svg","w+")
f.write(wordcloud_svg )
f.close()


# plt.figure()
# plt.imshow(wordcloud, interpolation="bilinear")
# plt.axis("off")
# #plt.show()
# plt.savefig("wordcloud.svg")
# #The pil way (if you don't have matplotlib)
# #image = wordcloud.to_image()
# #image.show()

# fname = "cloud_test"
# plt.imshow(wordcloud, interpolation="bilinear") 
# plt.axis("off")
# fig = plt.gcf() #get current figure
# fig.set_size_inches(10,10)  
# plt.savefig(fname, dpi=700)


# wordcloud_svg = wordcloud.to_svg(embed_font=True)
# f = open("filename.svg","w+")
# f.write(wordcloud_svg )
# f.close()