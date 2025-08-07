# main.py
import customtkinter as ctk
from ui.todo_view import TodoView
from ui.agenda_view import AgendaView

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mon Organiseur")
        self.geometry("1000x700")
        ctk.set_appearance_mode("System")  # ou "light" pour forcer un thème clair
        ctk.set_default_color_theme("blue")

        self.views = {
            "To-Do Liste": {"icon": "📝", "class": TodoView},
            "Agenda": {"icon": "📅", "class": AgendaView},
        }

        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.main_content = ctk.CTkFrame(self)
        self.main_content.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(self.sidebar, text="📂 Menu", font=("Arial", 16)).pack(pady=10)

        for view_name, info in self.views.items():
            label = f"{info['icon']} {view_name}"
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda name=view_name: self.show_view(name),
            )
            btn.pack(pady=5, padx=10, fill="x")

        self.current_view = None
        self.show_view("To-Do Liste")

    def clear_view(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        self.current_view = None

    def show_view(self, name):
        self.clear_view()
        view_class = self.views[name]["class"]
        self.current_view = view_class(self.main_content)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
