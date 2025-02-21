import tkinter as tk

# from subreddit: https://www.reddit.com/r/learnpython/comments/985umy/limit_user_input_to_only_int_with_tkinter/ by novel_yet_trivial

class IntegerEntry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        self.var = tk.StringVar()
        tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace_add('write', self.check)
        self.get, self.set = self.var.get, self.var.set # replace the set and get functions to the custom widget's set and get

    def check(self, *args):
        if self.get().isdigit() or self.get() == "": 
            # the current value is only digits; allow this
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this 
            self.set(self.old_value)