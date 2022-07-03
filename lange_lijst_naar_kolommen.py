
file = r"C:\Users\rcxsm\Documents\python_scripts\in\vs_medewerkers2022.txt"
f = open(file,'r')

lines = []
x=1
with open(file) as f:
    
        lines = f.readlines()
        for line in lines:
            file_to_save = r"C:\Users\rcxsm\Documents\python_scripts\in\vs_medwerkers2022.csv"
            with open(file_to_save, "a") as f:
                print(f"{x} / Adding {line} to textfile")
                if x % 3 == 0:
                    f.write(f"{line}\n#")
                else:
                    f.write(f"{line},")
                x +=1
            
              