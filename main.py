import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.ttk import Frame
import openai
import sql

openai.api_key = "<API-KEY>"


class MainView:
    def __init__(self, master):
        self.master = master
        master.title("Chat App")

        self.chat_module = self.ChatModule(self)

        # region TREE GROUPS
        self.tree_groups_frame = ttk.Frame(master)
        self.tree_groups_frame.pack(side="left", fill="both", expand=True)

        # BUTTON STRIP
        self.button_frame = ttk.Frame(self.tree_groups_frame)
        self.button_frame.pack(side="top", fill="x")
        self.add_group_button = ttk.Button(self.button_frame, text="+", width=3, command=self.add_group)
        self.add_group_button.pack(side="left")
        self.rename_group_button = ttk.Button(self.button_frame, text="✎", width=2, command=self.rename_group)
        self.rename_group_button.pack(side="left")
        self.delete_group_button = ttk.Button(self.button_frame, text="✕", width=2, command=self.delete_group)
        self.delete_group_button.pack(side="left")
        self.moveup_group = ttk.Button(self.button_frame, text="↑", width=2)  #, command=self.delete_context)
        self.moveup_group.pack(side="left")
        self.movedown_group = ttk.Button(self.button_frame, text="↓", width=2)  #, command=self.delete_context)
        self.movedown_group.pack(side="left")

        # TREEVIEW
        self.tree_groups = ttk.Treeview(self.tree_groups_frame)
        self.tree_groups.insert("", 0, text="Context 1")
        self.tree_groups.insert("", 1, text="Context 2")
        # self.tree_groups.bind("<<TreeviewSelect>>", lambda event: self.load_context(event.widget.set(event.widget.selection()[0], 'path')))
        self.tree_groups.bind("<Button-3>", self.show_groups_popup_menu)
        self.tree_groups.pack(side="left", fill="both", expand=True)
        # endregion

        # region TREE CONTEXTS
        self.tree_contexts_frame = ttk.Frame(master)
        self.tree_contexts_frame.pack(side="left", fill="both", expand=True)

        # BUTTON STRIP
        self.button_contexts_frame = ttk.Frame(self.tree_contexts_frame)
        self.button_contexts_frame.pack(side="top", fill="x")
        self.new_context_button = ttk.Button(self.button_contexts_frame, text="New", width=4, command=self.add_context)
        self.new_context_button.pack(side="left")
        self.rename_context_button = ttk.Button(self.button_frame, text="✎", width=2, command=self.rename_context)
        self.rename_context_button.pack(side="left")
        self.delete_context_button = ttk.Button(self.button_contexts_frame, text="✕", width=2, command=self.delete_context)
        self.delete_context_button.pack(side="left")
        self.moveup_group = ttk.Button(self.button_contexts_frame, text="↑", width=2)  #, command=self.delete_context)
        self.moveup_group.pack(side="left")
        self.movedown_group = ttk.Button(self.button_contexts_frame, text="↓", width=2)  #, command=self.delete_context)
        self.movedown_group.pack(side="left")

        # TREEVIEW
        self.tree_contexts = ttk.Treeview(self.tree_contexts_frame)
        self.tree_contexts.insert("", 0, text="Context 1")
        self.tree_contexts.insert("", 1, text="Context 2")
        self.tree_contexts.bind("<<TreeviewSelect>>", lambda event: self.load_context(event.widget.item(event.widget.selection()[0])['values'][0]) if event.widget.selection() else None)
        # self.tree_contexts.bind("<<TreeviewSelect>>", lambda event: self.load_context(event.widget.item(event.widget.selection()[0])['values'][0]))
        self.tree_contexts.bind("<Button-3>", self.show_contexts_popup_menu)
        self.tree_contexts.pack(side="left", fill="both", expand=True)
        # endregion

        # Create a frame to hold the chat box
        self.chat_frame = ttk.Frame(master)
        self.chat_frame.pack(side="right", fill="both", expand=True)

        # Create a label for the chat history
        self.chat_label = ttk.Label(self.chat_frame, text="Chat History")
        self.chat_label.pack()

        # Create a PanedWindow to hold the chat input and chat text
        self.chat_pane = ttk.PanedWindow(self.chat_frame, orient=tk.VERTICAL)
        self.chat_pane.pack(fill="both", expand=True)
        # self.chat_pane.paneconfig(1, minsize=200)

        # Create the chat text widget and link it to a scrollbar
        self.chat_text_frame = ttk.Frame(self.chat_pane)
        self.chat_text = tk.Text(self.chat_text_frame)  #state="normal")
        # self.chat_text.editable = False
        self.chat_text.pack(side="left", fill="both", expand=True)
        self.chat_scrollbar = ttk.Scrollbar(self.chat_text_frame, command=self.chat_text.yview)
        self.chat_scrollbar.pack(side="right", fill="y")
        self.chat_text["yscrollcommand"] = self.chat_scrollbar.set
        self.chat_text.tag_configure("user", foreground="black")
        self.chat_text.tag_configure("assistant", foreground="blue")
        self.chat_pane.add(self.chat_text_frame)  # , weight=5)

        # Create the chat input widget and link it to a scrollbar
        self.chat_input_frame = ttk.Frame(self.chat_pane)
        self.chat_input = tk.Text(self.chat_input_frame)
        self.chat_input.pack(side="left", fill="both", expand=True)
        self.chat_input_scrollbar = ttk.Scrollbar(self.chat_input_frame, command=self.chat_input.yview)
        self.chat_input_scrollbar.pack(side="right", fill="y")
        self.chat_input["yscrollcommand"] = self.chat_input_scrollbar.set
        self.chat_pane.add(self.chat_input_frame)

        # Create the submit button
        self.submit_button = ttk.Button(self.chat_input_frame, text="Send", command=self.chat_module.send_message)
        self.submit_button.pack(side="right")
        master.bind('<Return>', self.press_enter)

        self.load_groups()
        self.load_all_contexts()

    def press_enter(self, event):
        # if shift held down, return
        if event.state == 1:
            return
        keysym = event.keysym
        if keysym == "Return":  #  and not event.state:
            self.submit_button.invoke()

# region Groups

    def load_groups(self):
        contexts = sql.get_results("""
            SELECT id, group_name FROM groups
        """)
        self.tree_groups.delete(*self.tree_groups.get_children())
        for gid, name in contexts:

            # Add the file to the Treeview
            self.tree_groups.insert("", "end", text=name, values=(gid))

    def show_groups_popup_menu(self, event):
        # Display a popup menu with options to rename or delete the selected treeview item
        try:
            self.tree_groups.selection()[0]
        except IndexError:
            return
        menu = tk.Menu(self.tree_groups, tearoff=0)
        menu.add_command(label="Rename", command=self.rename_context)
        menu.add_command(label="Delete", command=self.delete_context)
        menu.post(event.x_root, event.y_root)

    def add_group(self):
        name = tk.simpledialog.askstring("New group", "Enter name for new group:")
        if name:
            sql.execute("""
                INSERT INTO groups (group_name) VALUES (?)
            """, (name,))
            self.load_groups()

    def rename_group(self):
        sel_item = self.tree_groups.selection()[0]
        sel_id = self.tree_groups.item(sel_item, 'values')[0]
        sel_name = self.tree_groups.item(sel_item, 'text')
        new_name = tk.simpledialog.askstring("Rename", "Enter new name for `" + sel_name + "`:")
        if new_name:
            sql.execute("""
                UPDATE groups SET group_name=? WHERE id=?
            """, (new_name, sel_id))
            self.load_groups()

    def delete_group(self):
        sel_item = self.tree_groups.selection()[0]
        sel_id = self.tree_groups.item(sel_item, 'values')[0]
        sel_name = self.tree_groups.item(sel_item, 'text')
        if messagebox.askyesno("Delete", "Are you sure you want to delete " + sel_name + "?"):
            sql.execute("""
                DELETE FROM groups WHERE id = ?
            """, (sel_id,))
            self.load_groups()

# endregion

# region Contexts

    def load_all_contexts(self):
        contexts = sql.get_results("""
            SELECT id, context_name FROM contexts
        """)
        self.tree_contexts.delete(*self.tree_contexts.get_children())
        for cid, name in contexts:

            # Add the file to the Treeview
            self.tree_contexts.insert("", "end", text=name, values=(cid))

    def load_context(self, context_id):
        self.chat_module.load_context(context_id)

    def show_contexts_popup_menu(self, event):
        # Display a popup menu with options to rename or delete the selected treeview item
        try:
            self.tree_contexts.selection()[0]
        except IndexError:
            return
        menu = tk.Menu(self.tree_contexts, tearoff=0)
        menu.add_command(label="Rename", command=self.rename_context)
        menu.add_command(label="Delete", command=self.delete_context)
        menu.post(event.x_root, event.y_root)

    def add_context(self):
        self.chat_module.new_context()

    def rename_context(self):
        # Allow the user to rename the selected treeview item
        old_name = self.tree_contexts.selection()[0]
        new_name = tk.simpledialog.askstring("Rename", "Enter new name for " + old_name + ":")
        if new_name:
            self.tree_contexts.item(old_name, text=new_name)

    def delete_context(self):
        sel_item = self.tree_contexts.selection()[0]
        sel_id = self.tree_contexts.item(sel_item, 'values')[0]
        sel_name = self.tree_contexts.item(sel_item, 'text')
        if messagebox.askyesno("Delete", "Are you sure you want to delete " + sel_name + "?"):
            sql.execute("""
                DELETE FROM contexts WHERE id = ?;
            """, (sel_id,))
            sql.execute("""
                DELETE FROM context_history WHERE context_id = ?;
            """, (sel_id,))
            self.load_all_contexts()
            self.chat_module.clear_chat_text()

# endregion

    class ChatModule:
        def __init__(self, main_view):
            self.main_view = main_view
            self.context_id = None
            self.title = None
            self.messages = []
            self.messages_to_push = []

        def new_context(self):
            self.context_id = None
            self.title = None
            self.messages = []
            self.clear_chat_text()
            for item in self.main_view.tree_contexts.selection():
                self.main_view.tree_contexts.selection_remove(item)

        def load_context(self, context_id):
            self.context_id = context_id
            if not self.context_id: raise Exception("No context selected")
            self.clear_chat_text()

            msg_log = sql.get_results("""
                SELECT mode, text FROM context_history WHERE context_id = ?
            """, (self.context_id,))

            self.messages = []
            for role, content in msg_log:
                self.messages.append({"role": role, "content": content})
                self.add_message(role, content)
            self.messages_to_push = []

            self.title = sql.get_scalar("""
                SELECT context_name FROM contexts WHERE id = ?
            """, (self.context_id,))

        def clear_chat_text(self):
            # self.main_view.chat_text.config(state="normal")
            self.main_view.chat_text.delete("1.0", "end")
            # self.main_view.chat_text.config(state="disabled")

        def save_context(self):
            if not self.context_id:
                self.context_id = sql.execute("""
                    INSERT INTO contexts (context_name) VALUES (?)
                """, (self.title,))
                self.main_view.load_all_contexts()

            # Add all messages_to_push to the context_history table, in one query, not using executemany
            # because it's faster to do it this way
            # qq = """
            #     INSERT INTO context_history (context_id, mode, content) VALUES """ + ",".join(["(?, ?, ?)"] * len(self.messages_to_push)),
            # pp = [val for val_dict in self.messages_to_push for _, val in val_dict.items()]
            # print(pp)

            values = [(self.context_id, val_dict['role'], val_dict['content']) for val_dict in self.messages_to_push]

            sql.execute("""
                INSERT INTO context_history (context_id, mode, text) VALUES """ + ",".join(["(?, ?, ?)"] * len(self.messages_to_push)),
                        [val for sublist in values for val in sublist])
            self.messages_to_push = []




            # if len(self.messages_to_push) > 0:
            #     query = "INSERT INTO context_history (context_id, mode, content) VALUES "
            #     ddd = [f"({self.context_id}, {msg['role']}, {msg['content']})" for msg in self.messages_to_push]
            #     query += ", ".join(ddd)
            #     sql.execute(query)
            #
            # sql.execute("""
            #     UPDATE contexts SET context_name=? WHERE id=?
            # """, (self.title, self.context_id))
            pass

        def send_message(self):
            message = self.main_view.chat_input.get("1.0", tk.END)
            self.add_message("user", message)
            self.main_view.chat_input.delete("1.0", tk.END)

            if not self.title:
                self.title = self.summarise_prompt(message)

            cc_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)
            response = cc_response["choices"][0]["message"]["content"]
            self.add_message("assistant", response)

            self.save_context()

        def add_message(self, role, content):
            # self.main_view.chat_text.configure(state="normal")
            self.main_view.chat_text.insert(tk.END, content, role)
            self.main_view.chat_text.insert(tk.END, "\n\n\n" if role == "assistant" else "\n\n")
            self.main_view.chat_text.see(tk.END)
            # self.main_view.chat_text.configure(state="disabled")
            self.messages.append({"role": role, "content": content})
            self.messages_to_push.append({"role": role, "content": content})

        def summarise_prompt(self, prompt):
            summary_prompt = "output a short title for the following request, under 8 words, avoiding stop words:\n"\
                             + prompt
            messages = [{"role": "user",
                        "content": summary_prompt}]
            cc_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            return cc_response["choices"][0]["message"]["content"].replace("\"", "")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainView(root)
    root.mainloop()
