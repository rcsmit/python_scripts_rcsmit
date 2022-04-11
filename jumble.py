# https://medium.com/swlh/how-to-create-better-ui-for-your-python-scripts-60c71924fae3
def jumble(message,rotate=13):
    AtoZ = range(ord('A'), ord('Z')+1)
    atoz = range(ord('a'), ord('z')+1)
    output = []
    for letter in message:
        ascii_val = ord(letter)
        start = None
        if ascii_val in AtoZ:
            start = AtoZ[0]
        elif ascii_val in atoz:
            start = atoz[0]
        if start:
            alpha = ord(letter)-start
            rotated = (alpha+rotate)%26
            output.append(chr(start+rotated))
        else:
            output.append(letter)
    return "".join(output)

def main_tkinter():
    import tkinter as tk
    def dojumble():
        res.configure(text=entry.get()+" -> "+jumble(entry.get()))
    w = tk.Tk()
    lbl = tk.Label(w, text="Enter your message for jumbling below…")
    lbl.pack(pady=10)
    entry = tk.Entry(w)
    entry.pack(pady=10)
    tk.Button(w, text="Jumble", command=dojumble).pack(pady=10)
    res = tk.Label(w)
    res.pack(pady=10)
    w.mainloop()

def main_cherrypy():
    import cherrypy
    import os
    class Jumbler(object):
        @cherrypy.expose
        def jumble(self, message):
            return jumble(message)
    cherrypy.config.update( {
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 9090,
    } )
    cherrypy.quickstart(Jumbler())
    #http://localhost:9090/jumble?message=hello

if __name__ == "__main__":
    #main_tkinter()
    main_cherrypy()