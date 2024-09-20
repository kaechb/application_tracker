import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ApplicationTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Application Tracker")
        self.create_database()
        self.create_widgets()
        self.populate_treeview()
        self.create_visualization()
        self.configure_grid()

    def create_database(self):
        self.conn = sqlite3.connect('applications.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                status TEXT NOT NULL,
                date_applied TEXT NOT NULL
            )
        ''')
        self.conn.commit()
        # Ensure new columns exist
        self.cursor.execute("PRAGMA table_info(applications)")
        columns = [column_info[1] for column_info in self.cursor.fetchall()]
        if 'rejection_stage' not in columns:
            self.cursor.execute("ALTER TABLE applications ADD COLUMN rejection_stage TEXT")
        if 'received_coding_challenge' not in columns:
            self.cursor.execute("ALTER TABLE applications ADD COLUMN received_coding_challenge INTEGER DEFAULT 0")
        if 'received_interview' not in columns:
            self.cursor.execute("ALTER TABLE applications ADD COLUMN received_interview INTEGER DEFAULT 0")
        self.conn.commit()

    def create_widgets(self):
        # Frame for form inputs
        self.form_frame = ttk.Frame(self.root)
        self.form_frame.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)

        # Configure grid weights in form_frame
        self.form_frame.columnconfigure(1, weight=1)
        self.form_frame.columnconfigure(3, weight=1)

        # Company Name
        tk.Label(self.form_frame, text="Company Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.company_entry = tk.Entry(self.form_frame)
        self.company_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Position
        tk.Label(self.form_frame, text="Position:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.position_entry = tk.Entry(self.form_frame)
        self.position_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Status
        tk.Label(self.form_frame, text="Status:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.status_var = tk.StringVar()
        self.status_combobox = ttk.Combobox(self.form_frame, textvariable=self.status_var, state='readonly')
        self.status_combobox['values'] = ('No Answer', 'Interviewing', 'Offered', 'Accepted', 'Rejected', 'Offer Rejected')
        self.status_combobox.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        self.status_combobox.current(0)
        self.status_combobox.bind('<<ComboboxSelected>>', self.on_status_change)

        # Date Applied
        tk.Label(self.form_frame, text="Date Applied (DD.MM.YYYY):").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.date_entry = tk.Entry(self.form_frame)
        self.date_entry.grid(row=1, column=3, padx=5, pady=5, sticky='ew')

        # New Fields for Rejection Details
        self.rejection_stage_var = tk.StringVar()
        self.received_coding_challenge_var = tk.IntVar()
        self.received_interview_var = tk.IntVar()

        # Rejection Stage
        self.rejection_stage_label = tk.Label(self.form_frame, text="Rejection Stage:")
        self.rejection_stage_entry = tk.Entry(self.form_frame, textvariable=self.rejection_stage_var)
        self.rejection_stage_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.rejection_stage_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # Received Coding Challenge
        self.received_coding_challenge_check = tk.Checkbutton(
            self.form_frame,
            text="Received Coding Challenge",
            variable=self.received_coding_challenge_var,
            command=self.ensure_exclusive_checks
        )
        self.received_coding_challenge_check.grid(row=2, column=2, padx=5, pady=5, sticky='w')

        # Received Interview
        self.received_interview_check = tk.Checkbutton(
            self.form_frame,
            text="Received Interview",
            variable=self.received_interview_var,
            command=self.ensure_exclusive_checks
        )
        self.received_interview_check.grid(row=2, column=3, padx=5, pady=5, sticky='w')

        # Disable the new fields initially
        self.rejection_stage_entry.config(state='disabled')
        self.received_coding_challenge_check.config(state='disabled')
        self.received_interview_check.config(state='disabled')

        # Search Frame
        self.search_frame = ttk.Frame(self.root)
        self.search_frame.grid(row=1, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)

        # Search Entry
        tk.Label(self.search_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Search Criteria
        tk.Label(self.search_frame, text="In:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.search_criteria_var = tk.StringVar()
        self.search_criteria_combobox = ttk.Combobox(
            self.search_frame,
            textvariable=self.search_criteria_var,
            state='readonly'
        )
        self.search_criteria_combobox['values'] = ('Company', 'Position', 'Status')
        self.search_criteria_combobox.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        self.search_criteria_combobox.current(0)

        # Search Buttons
        tk.Button(self.search_frame, text="Search", command=self.search_entries).grid(row=0, column=4, padx=5, pady=5)
        tk.Button(self.search_frame, text="Clear Search", command=self.clear_search).grid(row=0, column=5, padx=5, pady=5)

        # Configure grid weights in search_frame
        self.search_frame.columnconfigure(1, weight=1)
        self.search_frame.columnconfigure(3, weight=1)

        # Treeview for displaying applications
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.grid(row=2, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=('ID', 'Company', 'Position', 'Status', 'Date Applied'),
            show='headings'
        )
        self.tree.heading('ID', text='ID')
        self.tree.heading('Company', text='Company')
        self.tree.heading('Position', text='Position')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Date Applied', text='Date Applied')
        self.tree.column('ID', width=30)
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind the treeview selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Frame for matplotlib canvas
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.grid(row=3, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)
        self.canvas_frame.rowconfigure(0, weight=1)
        self.canvas_frame.columnconfigure(0, weight=1)

    def ensure_exclusive_checks(self):
        # Ensure that 'Received Coding Challenge' and 'Received Interview' are exclusive
        if self.received_coding_challenge_var.get():
            self.received_interview_var.set(0)
        elif self.received_interview_var.get():
            self.received_coding_challenge_var.set(0)

    def on_status_change(self, event):
        status = self.status_var.get()
        if status == 'Rejected':
            # Enable the rejection details widgets
            self.rejection_stage_entry.config(state='normal')
            self.received_coding_challenge_check.config(state='normal')
            self.received_interview_check.config(state='normal')
        else:
            # Disable and clear the rejection details widgets
            self.rejection_stage_entry.config(state='disabled')
            self.received_coding_challenge_check.config(state='disabled')
            self.received_interview_check.config(state='disabled')
            self.rejection_stage_var.set('')
            self.received_coding_challenge_var.set(0)
            self.received_interview_var.set(0)

    def add_application(self):
        company = self.company_entry.get().strip()
        position = self.position_entry.get().strip()
        status = self.status_var.get()
        date_applied = self.date_entry.get().strip()

        # Initialize new fields
        rejection_stage = None
        received_coding_challenge = 0
        received_interview = 0

        if status == 'Rejected':
            rejection_stage = self.rejection_stage_var.get().strip()
            received_coding_challenge = self.received_coding_challenge_var.get()
            received_interview = self.received_interview_var.get()

        if company and position and date_applied:
            try:
                self.cursor.execute('''
                    INSERT INTO applications (
                        company, position, status, date_applied,
                        rejection_stage, received_coding_challenge, received_interview
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    company, position, status, date_applied,
                    rejection_stage, received_coding_challenge, received_interview
                ))
                self.conn.commit()
                self.populate_treeview()
                self.clear_entries()
                self.update_visualization()
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")
        else:
            messagebox.showwarning("Input Error", "Please fill in all required fields.")

    def update_status(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            app_id = item['values'][0]
            new_status = self.status_var.get()

            # Initialize new fields
            rejection_stage = None
            received_coding_challenge = 0
            received_interview = 0

            if new_status == 'Rejected':
                rejection_stage = self.rejection_stage_var.get().strip()
                received_coding_challenge = self.received_coding_challenge_var.get()
                received_interview = self.received_interview_var.get()

            try:
                self.cursor.execute('''
                    UPDATE applications
                    SET status=?, rejection_stage=?, received_coding_challenge=?, received_interview=?
                    WHERE id=?
                ''', (
                    new_status, rejection_stage, received_coding_challenge, received_interview, app_id
                ))
                self.conn.commit()
                self.populate_treeview()
                self.update_visualization()
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")
        else:
            messagebox.showwarning("Selection Error", "Please select an application to update.")

    def delete_entry(self):
        selected_item = self.tree.selection()
        if selected_item:
            confirm = messagebox.askyesno("Delete Entry", "Are you sure you want to delete this entry?")
            if confirm:
                item = self.tree.item(selected_item)
                app_id = item['values'][0]
                try:
                    self.cursor.execute('DELETE FROM applications WHERE id=?', (app_id,))
                    self.conn.commit()
                    self.populate_treeview()
                    self.update_visualization()
                    self.clear_entries()
                except Exception as e:
                    messagebox.showerror("Database Error", f"An error occurred: {e}")
        else:
            messagebox.showwarning("Selection Error", "Please select an application to delete.")

    def populate_treeview(self, search_query=None, search_column=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            if search_query and search_column:
                query = f"SELECT id, company, position, status, date_applied FROM applications WHERE {search_column} LIKE ?"
                self.cursor.execute(query, (f"%{search_query}%",))
            else:
                self.cursor.execute('SELECT id, company, position, status, date_applied FROM applications')
            for row in self.cursor.fetchall():
                self.tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def search_entries(self):
        search_query = self.search_entry.get().strip()
        search_criteria = self.search_criteria_var.get().lower()

        column_map = {
            'company': 'company',
            'position': 'position',
            'status': 'status'
        }

        if search_query:
            search_column = column_map.get(search_criteria)
            self.populate_treeview(search_query=search_query, search_column=search_column)
        else:
            messagebox.showwarning("Search Error", "Please enter a search term.")

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.search_criteria_combobox.current(0)
        self.populate_treeview()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            app_id = item['values'][0]
            try:
                self.cursor.execute('SELECT * FROM applications WHERE id=?', (app_id,))
                row = self.cursor.fetchone()
                # Unpack the row
                _, company, position, status, date_applied, rejection_stage, received_coding_challenge, received_interview = row

                # Populate the fields
                self.company_entry.delete(0, tk.END)
                self.company_entry.insert(0, company)
                self.position_entry.delete(0, tk.END)
                self.position_entry.insert(0, position)
                self.status_var.set(status)
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, date_applied)

                if status == 'Rejected':
                    self.rejection_stage_var.set(rejection_stage if rejection_stage else '')
                    self.received_coding_challenge_var.set(received_coding_challenge)
                    self.received_interview_var.set(received_interview)
                    # Enable the rejection details widgets
                    self.rejection_stage_entry.config(state='normal')
                    self.received_coding_challenge_check.config(state='normal')
                    self.received_interview_check.config(state='normal')
                else:
                    # Disable and clear the rejection details widgets
                    self.rejection_stage_entry.config(state='disabled')
                    self.received_coding_challenge_check.config(state='disabled')
                    self.received_interview_check.config(state='disabled')
                    self.rejection_stage_var.set('')
                    self.received_coding_challenge_var.set(0)
                    self.received_interview_var.set(0)
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")

    def clear_entries(self):
        self.company_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.status_combobox.current(0)
        # Clear the new fields and disable them
        self.rejection_stage_var.set('')
        self.received_coding_challenge_var.set(0)
        self.received_interview_var.set(0)
        self.rejection_stage_entry.config(state='disabled')
        self.received_coding_challenge_check.config(state='disabled')
        self.received_interview_check.config(state='disabled')

    def create_visualization(self):
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        self.update_visualization()

    def update_visualization(self):
        # Fetch data for visualization
        try:
            self.cursor.execute('SELECT status, received_interview, received_coding_challenge FROM applications')
            data = self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return

        # Initialize counts
        status_counts = {
            'No Answer': 0,
            'Interviewing': 0,
            'Offered': 0,
            'Accepted': 0,
            'Offer Rejected': 0,
            'Rejected without Interview': 0,
            'Rejected after Coding Challenge': 0,
            'Rejected after Interview': 0
        }

        # Process data
        for row in data:
            status = row[0]
            received_interview = row[1]
            received_coding_challenge = row[2]

            if status == 'Rejected':
                if received_interview:
                    status_counts['Rejected after Interview'] += 1
                elif received_coding_challenge:
                    status_counts['Rejected after Coding Challenge'] += 1
                else:
                    status_counts['Rejected without Interview'] += 1
            else:
                status_counts[status] += 1

        # Prepare data for plotting
        labels = []
        counts = []
        for status, count in status_counts.items():
            if count > 0:
                labels.append(status)
                counts.append(count)

        # Colors for statuses
        color_map = {
            'No Answer': 'lightgrey',
            'Interviewing': 'gold',
            'Offered': 'lightgreen',
            'Accepted': 'blue',
            'Offer Rejected': 'lightblue',
            'Rejected without Interview': 'salmon',
            'Rejected after Coding Challenge': 'orangered',
            'Rejected after Interview': 'red'
        }
        colors = [color_map[status] for status in labels]

        # Clear the previous plot
        self.ax.clear()

        if counts:
            # Plot the data
            wedges, texts, autotexts = self.ax.pie(counts, autopct='%1.1f%%', startangle=140, colors=colors)
            self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            # Add legend
            self.ax.legend(wedges, labels, title="Statuses", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        else:
            # Display a message when there is no data
            self.ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                         verticalalignment='center', fontsize=16)
            self.ax.axis('off')

        # Adjust layout to make room for legend
        self.figure.tight_layout()

        # Draw the canvas
        self.canvas.draw()

    def configure_grid(self):
        # Configure root grid weights
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)

    def close_connection(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationTracker(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.close_connection(), root.destroy()))
    root.mainloop()
