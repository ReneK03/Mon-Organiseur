import customtkinter as ctk
from datetime import timedelta, date
import calendar
import sqlite3

from modules.agenda_db import (
    init_db, add_event, get_events,
    update_event, delete_event
)

# Traductions manuelles
MOIS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]
JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

COULEURS_NOM_FR = {
    "bleu": "blue", "rouge": "red", "vert": "green",
    "jaune": "yellow", "violet": "purple", "gris": "gray"
}

def mois_en_fr(mois_index):
    return MOIS_FR[mois_index - 1]

def jour_en_fr(date_obj):
    return JOURS_FR[date_obj.weekday()]

class AgendaView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        init_db()
        self.today = date.today()
        self.current_date = self.today
        self.current_view = "month"

        controls = ctk.CTkFrame(self)
        controls.pack(fill="x", pady=10)

        self.label_month = ctk.CTkLabel(controls, text="", font=("Arial", 18, "bold"))
        self.label_month.pack(pady=5)

        nav_frame = ctk.CTkFrame(controls, fg_color="transparent")
        nav_frame.pack(fill="x", pady=5)

        ctk.CTkButton(nav_frame, text="⏪", width=40, command=self.prev_period).pack(side="left", padx=10)
        ctk.CTkButton(nav_frame, text="⏩", width=40, command=self.next_period).pack(side="right", padx=10)

        self.view_selector = ctk.CTkSegmentedButton(
            nav_frame,
            values=["Mois", "Semaine", "Jour"],
            command=self.change_view
        )
        self.view_selector.set("Mois")
        self.view_selector.pack(expand=True)

        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.render_view()

    def change_view(self, value):
        mapping = {"Mois": "month", "Semaine": "week", "Jour": "day"}
        self.current_view = mapping.get(value, "month")
        self.render_view()

    def prev_period(self):
        if self.current_view == "month":
            m = self.current_date.month - 1 or 12
            y = self.current_date.year - 1 if m == 12 else self.current_date.year
            self.current_date = self.current_date.replace(year=y, month=m, day=1)
        elif self.current_view == "week":
            self.current_date -= timedelta(days=7)
        else:
            self.current_date -= timedelta(days=1)
        self.render_view()

    def next_period(self):
        if self.current_view == "month":
            m = self.current_date.month + 1 if self.current_date.month < 12 else 1
            y = self.current_date.year + 1 if m == 1 else self.current_date.year
            self.current_date = self.current_date.replace(year=y, month=m, day=1)
        elif self.current_view == "week":
            self.current_date += timedelta(days=7)
        else:
            self.current_date += timedelta(days=1)
        self.render_view()

    def render_view(self):
        for w in self.calendar_frame.winfo_children():
            w.destroy()
        if self.current_view == "month":
            self.render_month_view()
        elif self.current_view == "week":
            self.render_week_view()
        else:
            self.render_day_view()

    def render_month_view(self):
        year = self.current_date.year
        month = self.current_date.month
        self.label_month.configure(text=f"{mois_en_fr(month)} {year}")

        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdatescalendar(year, month)

        grid = ctk.CTkFrame(self.calendar_frame)
        grid.pack(fill="both", expand=True)

        # Configuration des colonnes (1 pour Sem, 7 pour jours)
        for i in range(8):
            grid.grid_columnconfigure(i, weight=1, minsize=100)

        # Ligne d'en-tête + une ligne par semaine
        for j in range(len(weeks) + 1):
            # Ligne 0 (en-tête) plus petite
            grid.grid_rowconfigure(j, weight=1, minsize=40 if j == 0 else 120)

        # --- Ligne 0 : noms des jours + colonne semaine ---
        sem_frame = ctk.CTkFrame(grid, corner_radius=4, fg_color="#2b2b2b")
        sem_frame.grid(row=0, column=0, padx=1, pady=1, sticky="nsew")
        ctk.CTkLabel(sem_frame, text="Sem", font=("Arial", 12)).pack(expand=True)

        for idx, jour in enumerate(JOURS_FR):
            day_header = ctk.CTkFrame(grid, corner_radius=4, fg_color="#2b2b2b")
            day_header.grid(row=0, column=idx + 1, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(day_header, text=jour, font=("Arial", 12)).pack(expand=True)

        # --- Contenu des jours ---
        for r, week in enumerate(weeks):
            num_sem = week[0].isocalendar()[1]

            # Colonne "semaines"
            week_num_frame = ctk.CTkFrame(grid, corner_radius=4, fg_color="#2b2b2b")
            week_num_frame.grid(row=r + 1, column=0, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(week_num_frame, text=f"{num_sem}", font=("Arial", 11)).pack(expand=True)

            # Jours
            for c, day in enumerate(week):
                cell = ctk.CTkFrame(grid, fg_color="#1e1e1e", corner_radius=6)
                cell.grid(row=r + 1, column=c + 1, padx=1, pady=1, sticky="nsew")

                btn_text = str(day.day) if day.month == month else ""
                ctk.CTkButton(cell, text=btn_text, width=30, height=20,
                            command=lambda d=day: self.open_event_popup(d)).pack(pady=(4, 0))

                # Affichage des événements avec 2 lignes max
                events = get_events(day.strftime("%Y-%m-%d"))
                for idx, (_, title, tag, color) in enumerate(events):
                    if idx >= 2:
                        break  # max 2 lignes
                    tag_color = COULEURS_NOM_FR.get(color, "gray")
                    row_f = ctk.CTkFrame(cell, fg_color="transparent")
                    row_f.pack(anchor="w", padx=2, pady=1, fill="x")
                    if tag:
                        ctk.CTkLabel(row_f, text=tag, fg_color=tag_color,
                                    text_color="white", corner_radius=4, width=50, height=20).pack(
                                    side="left", padx=(0, 4))
                    ctk.CTkLabel(row_f, text=title[:15], text_color="white", wraplength=80, justify="left").pack(side="left")

    def render_week_view(self):
        start = self.current_date - timedelta(days=self.current_date.weekday())
        self.label_month.configure(
            text=f"Semaine du {start.day} {mois_en_fr(start.month)} {start.year}"
        )
    
        frame = ctk.CTkFrame(self.calendar_frame)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
    
        # Colonnes = jours de la semaine
        for col in range(7):
            frame.grid_columnconfigure(col, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
    
        # Entêtes des jours
        for col, i in enumerate(range(7)):
            jour = start + timedelta(days=i)
            label = ctk.CTkLabel(
                frame,
                text=f"{JOURS_FR[jour.weekday()]}\n{jour.day} {mois_en_fr(jour.month)}",
                font=("Arial", 12, "bold"),
                anchor="center"
            )
            label.grid(row=0, column=col, padx=5, pady=5)
    
        # Affichage des événements
        for col, i in enumerate(range(7)):
            jour = start + timedelta(days=i)
            day_frame = ctk.CTkFrame(frame, fg_color="transparent")
            day_frame.grid(row=1, column=col, sticky="nsew", padx=5, pady=5)
    
            events = get_events(jour.strftime("%Y-%m-%d"))
            if not events:
                ctk.CTkLabel(day_frame, text="").pack()
            else:
                for eid, title, tag, color in events[:4]:  # max 4 événements pour éviter overflow
                    row_f = ctk.CTkFrame(day_frame, fg_color="transparent")
                    row_f.pack(anchor="w", padx=2, pady=2, fill="x")
                    if tag:
                        tag_color = COULEURS_NOM_FR.get(color, "gray")
                        ctk.CTkLabel(
                            row_f, text=tag, fg_color=tag_color, text_color="white",
                            corner_radius=4, width=45
                        ).pack(side="left", padx=(0, 4))
                    ctk.CTkLabel(row_f, text=title[:15], text_color="white", wraplength=80).pack(side="left")


    def render_day_view(self):
        d = self.current_date
        self.label_month.configure(text=f"{jour_en_fr(d)} {d.day} {mois_en_fr(d.month)} {d.year}")
        frame = ctk.CTkFrame(self.calendar_frame)
        frame.pack(fill="both", expand=True, pady=30)

        add_button = ctk.CTkButton(
            frame, text="➕ Ajouter un événement",
            command=lambda: self.open_event_popup(d)
        )
        add_button.pack(pady=10)

        events = get_events(d.strftime("%Y-%m-%d"))
        if not events:
            ctk.CTkLabel(frame, text="Aucun événement").pack(pady=10)
        else:
            for eid, title, tag, color in events:
                row_f = ctk.CTkFrame(frame)
                row_f.pack(fill="x", pady=5, padx=10)

                if tag:
                    tag_color = COULEURS_NOM_FR.get(color, "gray")
                    ctk.CTkLabel(
                        row_f, text=tag, fg_color=tag_color,
                        text_color="white", corner_radius=4, width=60
                    ).pack(side="left", padx=(0, 5))

                ctk.CTkLabel(row_f, text=title, text_color="white").pack(side="left", padx=5)

                ctk.CTkButton(
                    row_f, text="✏️", width=40,
                    command=lambda eid=eid: self.edit_event_popup(eid)
                ).pack(side="right", padx=2)

                ctk.CTkButton(
                    row_f, text="🗑️", width=40, fg_color="red",
                    command=lambda eid=eid: self.confirm_delete_event(eid)
                ).pack(side="right", padx=2)

    def open_event_popup(self, day):
        popup = ctk.CTkToplevel(self)
        popup.title("Nouvel événement")
        popup.geometry("300x280")
        popup.grab_set()

        ctk.CTkLabel(popup, text="Titre :").pack(pady=(10, 0))
        entry_title = ctk.CTkEntry(popup)
        entry_title.pack()

        ctk.CTkLabel(popup, text="Tag (facultatif) :").pack(pady=(10, 0))
        entry_tag = ctk.CTkEntry(popup)
        entry_tag.pack()
    
        ctk.CTkLabel(popup, text="Couleur du tag :").pack(pady=(10, 0))
        combo_color = ctk.CTkOptionMenu(
            popup,
            values=list(COULEURS_NOM_FR.keys())
        )
        combo_color.set("bleu")  # Valeur par défaut
        combo_color.pack()

        def save():
            title = entry_title.get()
            tag = entry_tag.get()
            color = combo_color.get()
            if title:
                add_event(day.strftime("%Y-%m-%d"), title, tag, color)
                popup.destroy()
                self.render_view()
    
        ctk.CTkButton(popup, text="Enregistrer", command=save).pack(pady=15)

    def edit_event_popup(self, event_id):
        conn = sqlite3.connect("agenda.db")
        c = conn.cursor()
        c.execute("SELECT date, title, tag, color FROM events WHERE id = ?", (event_id,))
        result = c.fetchone()
        conn.close()
    
        if not result:
            return
    
        date_str, title_old, tag_old, color_old = result
    
        popup = ctk.CTkToplevel(self)
        popup.title("Modifier l'événement")
        popup.geometry("300x280")
        popup.grab_set()
    
        ctk.CTkLabel(popup, text="Titre :").pack(pady=(10, 0))
        entry_title = ctk.CTkEntry(popup)
        entry_title.insert(0, title_old)
        entry_title.pack()
    
        ctk.CTkLabel(popup, text="Tag (facultatif) :").pack(pady=(10, 0))
        entry_tag = ctk.CTkEntry(popup)
        entry_tag.insert(0, tag_old)
        entry_tag.pack()
    
        ctk.CTkLabel(popup, text="Couleur du tag :").pack(pady=(10, 0))
        combo_color = ctk.CTkOptionMenu(
            popup,
            values=list(COULEURS_NOM_FR.keys())
        )
        combo_color.set(color_old if color_old in COULEURS_NOM_FR else "bleu")
        combo_color.pack()
    
        # ✅ Fonction update définie à l’intérieur
        def update():
            new_title = entry_title.get()
            new_tag = entry_tag.get()
            new_color = combo_color.get()
            if new_title:
                update_event(event_id, new_title, new_tag, new_color)
                popup.destroy()
                self.render_view()
    
        ctk.CTkButton(popup, text="Enregistrer", command=update).pack(pady=15)

    def confirm_delete_event(self, event_id):
        confirm = ctk.CTkToplevel(self)
        confirm.title("Confirmer la suppression")
        confirm.geometry("250x120")
        confirm.grab_set()

        ctk.CTkLabel(confirm, text="Supprimer cet événement ?").pack(pady=10)

        ctk.CTkButton(confirm, text="Oui", fg_color="red",
                  command=lambda: self.delete_and_close(event_id, confirm)).pack(pady=5)
        ctk.CTkButton(confirm, text="Non", command=confirm.destroy).pack()

    def delete_and_close(self, event_id, window):
        delete_event(event_id)
        window.destroy()
        self.render_view()
