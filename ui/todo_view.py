# ui/todo_view.py
import customtkinter as ctk
from modules.todo import load_tasks, save_tasks

class TodoView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.tasks = load_tasks()

        self.task_entry = ctk.CTkEntry(self, placeholder_text="Nouvelle tâche...")
        self.task_entry.pack(pady=15, padx=20, fill="x")

        self.add_button = ctk.CTkButton(self, text="Ajouter la tâche", command=self.add_task)
        self.add_button.pack(pady=5)

        self.task_listbox = ctk.CTkScrollableFrame(self, height=350)
        self.task_listbox.pack(padx=20, pady=10, fill="both", expand=True)

        self.refresh_tasks()

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append(task)
            save_tasks(self.tasks)
            self.task_entry.delete(0, "end")
            self.refresh_tasks()

    def delete_task(self, task):
        self.tasks.remove(task)
        save_tasks(self.tasks)
        self.refresh_tasks()

    def refresh_tasks(self):
        for widget in self.task_listbox.winfo_children():
            widget.destroy()

        for task in self.tasks:
            frame = ctk.CTkFrame(self.task_listbox)
            frame.pack(fill="x", pady=5, padx=5)

            label = ctk.CTkLabel(frame, text=task, anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=(10, 0))

            delete_btn = ctk.CTkButton(
                frame, text="❌", width=30, command=lambda t=task: self.delete_task(t)
            )
            delete_btn.pack(side="right", padx=10)
