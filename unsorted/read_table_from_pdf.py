
import tabula

file1 = "C:\\Users\\rcxsm\\Downloads\\Overzicht 2020 Week 52.pdf"
table = tabula.read_pdf(file1,pages=1)
print (table[0])