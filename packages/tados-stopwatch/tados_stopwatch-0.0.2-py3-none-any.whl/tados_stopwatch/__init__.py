import time

class Stopwatch:
    def __init__(self):
        self.running=False
        self.startTime=0
        self.elapsedTime=0
        self.listeners={}

    def start(self):
        if self.running: return
        self.running=True
        self.startTime=time.monotonic()-self.elapsedTime

    def get(self):
        if not self.running: return self.elapsedTime
        before=self.elapsedTime
        self.elapsedTime=time.monotonic()-self.startTime
        difference=self.elapsedTime-before
        for listener in self.listeners.values():
            targetTime,callback=listener
            if before<targetTime<=self.elapsedTime:
                callback()
        return self.elapsedTime

    def stop(self):
        if not self.running: return
        self.elapsedTime=self.get()
        self.running=False

    def reset(self):
        self.set(0,True)

    def set(self,time,forceStop=False):
        r=self.running
        self.stop()
        self.elapsedTime=time
        if r and not forceStop: self.start()

    def bind(self,time,callback):
        id=len(self.listeners)
        self.listeners[id]=(time,callback)
        return id

    def unbind(self,listenerID):
        del self.listeners[listenerID]

if __name__=="__main__":
    import tkinter as tk

    s=Stopwatch()

    app=tk.Tk()
    app.title("Stopwatch")
    app.geometry("300x120")
    label=tk.Label(app,text="",font=("Roboto",30))
    label.pack()
    frame=tk.Frame(app,padx=10,pady=10)
    frame.pack(pady=5)
    startButton=tk.Button(frame,text="Start",command=s.start)
    startButton.grid(row=0,column=0)
    stopButton=tk.Button(frame,text="Stop",command=s.stop)
    stopButton.grid(row=0,column=1)
    resButton=tk.Button(frame,text="Reset",command=s.reset)
    resButton.grid(row=0,column=2)

    def updater():
        label.configure(text=f"{s.get():.3f}")
        app.after(16,updater)

    app.after(0,updater)
    app.mainloop()
