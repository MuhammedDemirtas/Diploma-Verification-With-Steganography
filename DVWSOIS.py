import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import pypyodbc
import dvwstool
import os

def login():

    # Retrieve the username and password entered by the user.
    entered_username = username_entry.get()
    entered_password = password_entry.get()

    try:
        # Establish a connection to the SQL Server database.
        db = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-GLNTNNB\SQLEXPRESS;Database=Company;Trusted_Connection=True;')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM login WHERE username=? AND password=?", (entered_username, entered_password))
        user = cursor.fetchone()

        if user:
            # Execute the SQL query to find a matching username and password in the login table.
            username, password, effect = user
            messagebox.showinfo("LOGIN PROCESS", "Login Successful")
            # Open the main menu and pass the effect value.
            open_main_menu(effect)
        else:
            messagebox.showerror("WARNING", "Invalid Username or Password !")

        db.close()

    except Exception as e:
        messagebox.showerror("WARNING", f" {str(e)}")

def open_main_menu(effect):

    # Hide the login frame.
    login_frame.pack_forget()

    # Show the main menu frame.
    main_menu_frame.pack(fill="both", expand=True)

def go_back_to_main_menu(stego_window):

    # Destroy the steganography window.
    stego_window.destroy()

    # Clear the diploma entry field.
    diploma_entry.delete(0, tk.END)


def security_process():

    # Open a file dialog to select an image.
    filename = filedialog.askopenfilename(initialdir="/", title="Resim Seç", filetypes=(("Resim Dosyaları", "*.jpg;*.png;*.jpeg"), ("Tüm Dosyalar", "*.*")))

    if not filename:
        # If no image is selected, show an error message.
        messagebox.showerror("WARNING", "Please Choose A Diploma!")
        return

    # Get the absolute path of the selected image.
    full_filename = os.path.abspath(filename)

    try:
        # Perform wavelet steganalysis on the selected image.
        steganaliz = dvwstool.wavelet_steganaliz(full_filename)

        # Decode the extracted data using Reed-Solomon decoding.
        decode = dvwstool.reed_solomon_decode(bytes.fromhex(steganaliz))

        # Decrypt the decoded data using AES. The data coming out here is hash.
        decrypt = dvwstool.aes_decrypt(decode)

        # Establish a connection to the company database.
        company_db = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-GLNTNNB\SQLEXPRESS;Database=Company;Trusted_Connection=True;')
        company_cursor = company_db.cursor()

        # Query the KEYS table to find the corresponding key.
        company_cursor.execute("SELECT [Key] FROM KEYS WHERE HashData = ?", (decrypt,))
        key = company_cursor.fetchone()

        if key:

            # Extract student information from key according to key order.
            student_key = key[0]
            bolum = student_key[:2]
            ad = student_key[2]
            ad2 = student_key[5]
            tc = student_key[3:5]
            soyad = student_key[6]
            soyad2 = student_key[9]
            diploma_no = student_key[7:9]

            # Establish a connection to the school database.
            school_db = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-GLNTNNB\SQLEXPRESS;Database=School;Trusted_Connection=True;')
            school_cursor = school_db.cursor()

            # Query the Student table to find the student information.
            school_cursor.execute("SELECT Ad, Soyad FROM Student WHERE LEFT(Bolum, 2) = ? AND LEFT(Ad, 1) = ? AND RIGHT(Ad, 1) = ? AND LEFT(Soyad, 1) = ? AND RIGHT(Soyad, 1) = ? AND LEFT(Tc, 2) = ? AND LEFT(DiplomaNo, 2) = ?",
                          (bolum, ad, ad2, soyad, soyad2, tc, diploma_no))
            student_info = school_cursor.fetchone()

            if student_info:

                # If student information is found, show a success message.
                messagebox.showinfo("VERIFICATION PROCESS", f"   VERIFICATION PROCESS IS COMPLETED \n\n This Diploma Is Produced For {student_info[0]} {student_info[1]} ")
            else:

                # If student information is not found, show an error message.
                messagebox.showerror("WARNING", "Student Is Not Found !")

            # Close the school database connection.
            school_db.close()
        else:

            # If key is not found, show an error message.
            messagebox.showerror("WARNING", "Key Is Not Found.")

        # Close the company database connection.
        company_db.close()


    except Exception as e:

        # If an exception occurs, show an error message.
        messagebox.showerror("WARNING", f"Diploma Not Previously Registered")

def close_window():

    # Function to close the main window.
    root.destroy()

def resize_image(event):

    # Function to resize the background image when the window is resized.
    global resized_image
    new_width = event.width
    new_height = event.height
    resized_image = original_image.resize((new_width, new_height))
    photo = ImageTk.PhotoImage(resized_image)
    canvas.itemconfig(background, image=photo)
    canvas.image = photo
    canvas.coords(background, new_width // 2, new_height // 2)

# Initialize the main window.
root = tk.Tk()
root.title("Steganography ve Diploma Güvenliği Uygulaması")
root.attributes('-fullscreen', True)
root.configure(bg="#1B1B1D")

# Create and pack the login frame.
login_frame = tk.Frame(root, bg="#1B1B1D")
login_frame.pack(fill="both", expand=True)

# Load and place the background image for the login frame.
login_background_image = Image.open("log.png")
resized_login_background_image = login_background_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
login_photo = ImageTk.PhotoImage(resized_login_background_image)
login_background = tk.Label(login_frame, image=login_photo)
login_background.image = login_photo
login_background.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Add a label for the login menu.
login_label = tk.Label(login_frame, text="LOGIN MENU", bg="#1B1B1D", fg="white", font=("Helvetica", 24))
login_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

# Add username and password entry fields.
username_label = tk.Label(login_frame, text="USERNAME", bg="#1B1B1D", fg="white", font=("Helvetica", 14))
username_label.place(relx=0.38, rely=0.42, anchor=tk.CENTER)
username_entry = tk.Entry(login_frame, font=("Helvetica", 14))
username_entry.place(relx=0.5, rely=0.42, anchor=tk.CENTER)

password_label = tk.Label(login_frame, text="PASSWORD", bg="#1B1B1D", fg="white", font=("Helvetica", 14))
password_label.place(relx=0.385, rely=0.52, anchor=tk.CENTER)
password_entry = tk.Entry(login_frame, show="*", font=("Helvetica", 14))
password_entry.place(relx=0.5, rely=0.52, anchor=tk.CENTER)

# Add login and exit buttons.
login_button = ttk.Button(login_frame, text="Log In", command=login, width=20)
login_button.place(relx=0.5, rely=0.61, anchor=tk.CENTER)

exit_button_login = ttk.Button(login_frame, text="Exit", command=close_window, width=20)
exit_button_login.place(relx=0.5, rely=0.66, anchor=tk.CENTER)

# Create the main menu frame.
main_menu_frame = tk.Frame(root, bg="#1B1B1D")

# Create a canvas to hold the background image in the main menu.
canvas = tk.Canvas(main_menu_frame)
canvas.pack(fill="both", expand=True)

# Load and set the background image for the main menu.
original_image = Image.open("menü.png")
resized_image = original_image
photo = ImageTk.PhotoImage(original_image)
background = canvas.create_image(0, 0, anchor=tk.CENTER, image=photo)

# Bind the resize event to the resize_image function.
canvas.bind("<Configure>", resize_image)

# Configure the button style.
button_style = ttk.Style()
button_style.configure("Custom.TButton", font=("Helvetica", 12), background="#1B1B1D")

# Add a button to start the steganography process.
diploma_label = tk.Label(main_menu_frame, text="PROCESS MENU ", bg="#1B1B1D", fg="white", font=("Helvetica", 24))
diploma_label.place(relx=0.5, rely=0.30, anchor=tk.CENTER)

# Bind the resize event to the resize_image function.
security_frame = tk.Frame(main_menu_frame, bg="#1B1B1D")
security_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

security_button = ttk.Button(main_menu_frame, text="Verification Process", command=security_process, style="Custom.TButton")
security_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Add a button for the help process.
help_button = ttk.Button(main_menu_frame, text="Help", command=lambda: help_process(), style="Custom.TButton")
help_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

def help_process():

    # Function to create a help window with instructions.
    help_window = tk.Toplevel(root)
    help_window.title("Help")
    help_window.geometry("400x200")
    help_window.configure(bg="#1B1B1D")

    help_label = tk.Label(help_window, text="FOR THE SECURITY PROCESS \n\n1.Click the 'Verification Process' button.\n\n2. Select the image of the diploma.\n\n3. Confirm.", bg="#1B1B1D", fg="#ADFF2F", font=("Helvetica", 12))
    help_label.pack(expand=True, fill="both")

def go_back_to_login():

    # Function to go back to the login frame.
    main_menu_frame.pack_forget()
    login_frame.pack(fill="both", expand=True)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

# Add back and exit buttons in the main menu.
back_button = ttk.Button(main_menu_frame, text="Back ", command=go_back_to_login, style="Custom.TButton", width=20)
back_button.place(relx=0.5, rely=0.71, anchor=tk.CENTER)

exit_button_main = ttk.Button(main_menu_frame, text="Exit", command=close_window, style="Custom.TButton", width=20)
exit_button_main.place(relx=0.5, rely=0.76, anchor=tk.CENTER)

# Start the main event loop.
root.mainloop()
