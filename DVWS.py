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
        db = pypyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=Company;Trusted_Connection=True;')
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

    # Enable or disable the steganography button based on the effect value.
    if effect == "0":
        steganography_button.config(state="normal")
    elif effect == "1":
        steganography_button.config(state="disabled")
    else:

        pass

def go_back_to_main_menu(stego_window):

    # Destroy the steganography window.
    stego_window.destroy()

    # Clear the diploma entry field.
    diploma_entry.delete(0, tk.END)

def steganography_process():
    def start_steganography():

        # Get the selected value from the combobox.
        selection = combobox.get()
        if selection == "Bireysel":
            process_individual() # Start individual processing.
        elif selection == "Bölüm":
            process_department() # Start department processing.

    def process_individual():

        # Get the diploma number.
        diploma_id = diploma_entry.get()
        if not diploma_id:
            error_label.config(text="LÜTFEN BİR DİPLOMA NUMARASI GİRİNİZ")
            return

        try:
            # Establish a connection to the school database.
            school_db = pypyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=School;Trusted_Connection=True;')
            school_cursor = school_db.cursor()

            # Retrieve student information from the database.
            school_cursor.execute("SELECT Bolum, Ad, Soyad, Tc, DiplomaNo FROM Student WHERE DiplomaNo=?", (diploma_id,))
            student_info = school_cursor.fetchone()

            if student_info:

                # Extract student information.
                bolum, ad, soyad, tc, diploma_no = student_info

                # Perform main processes.
                key, hash_data, reed_solo = main_processes(bolum, ad, soyad, tc, diploma_no)

                # Create the file name for the diploma.
                diploma_adi_jpg = f"{diploma_id}.jpg"

                # Establish a connection to the company database.
                company_db = pypyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=Company;Trusted_Connection=True;')

                company_cursor = company_db.cursor()

                # Check if the key already exists in the KEYS table.
                company_cursor.execute("SELECT [Key] FROM KEYS WHERE [Key]=?", (key,))

                existing_key = company_cursor.fetchone()

                if existing_key:
                    # If the key already exists, show an error message.
                    error_label.config(text="BU ANAHTAR ZATEN KULLANILIYOR")
                else:

                    # Insert the new key and hash data into the KEYS table.
                    company_cursor.execute("INSERT INTO KEYS ([Key], HashData) VALUES (?, CONVERT(varbinary(max), ?))", (key, hash_data))

                    company_db.commit()

                    # Perform the wavelet transform and hide the data in the image.
                    dvwstool.wavelet_transform(os.path.join("Diplomalar", diploma_adi_jpg), reed_solo.hex(), 'Gizlenenler')

                    # Show a success message.
                    error_label.config(text="KAYIT TAMAMLANDI")
            else:

                # If no student information is found, show an error message.
                error_label.config(text="ÖĞRENCİ BULUNAMADI")

            # Close the database connections.
            school_db.close()
            company_db.close()

        except Exception as e:
            # If an exception occurs, show an error message.
            error_label.config(text=f"Lütfen Geçerli Id Girin !")

    def process_department():

        # Get the department name from the entry field.
        department_name = diploma_entry.get()
        if not department_name:
            # If no department name is entered, show an error message.
            error_label.config(text="LÜTFEN BİR BÖLÜM ADI GİRİNİZ")
            return

        try:
            # Establish a connection to the school database.
            school_db = pypyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=School;Trusted_Connection=True;')
            school_cursor = school_db.cursor()

            # Retrieve student information from the database for the specified department.
            school_cursor.execute("SELECT Bolum, Ad, Soyad, Tc, DiplomaNo FROM Student WHERE Bolum=?", (department_name,))
            students_info = school_cursor.fetchall()

            if students_info:
                # Establish a connection to the company database.
                company_db = pypyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=Company;Trusted_Connection=True;')
                company_cursor = company_db.cursor()

                for student_info in students_info:

                    # Extract student information.
                    bolum, ad, soyad, tc, diploma_no = student_info

                    # Perform main processes.
                    key, hash_data, reed_solo = main_processes(bolum, ad, soyad, tc, diploma_no)
                    diploma_id = student_info[4]

                    # Create the file name for the diploma.
                    diploma_adi_jpg = f"{diploma_id}.jpg"

                    # Check if the key already exists in the KEYS table.
                    company_cursor.execute("SELECT [Key] FROM KEYS WHERE [Key]=?", (key,))
                    existing_key = company_cursor.fetchone()

                    if existing_key:
                        # If the key already exists, show an error message.
                        error_label.config(text=f"Daha önce kayıt mevcut fakat mevcut olmayanlar eklendi.")
                    else:
                        # Insert the new key and hash data into the KEYS table.
                        company_cursor.execute("INSERT INTO KEYS ([Key], HashData) VALUES (?, CONVERT(varbinary(max), ?))", (key, hash_data))
                        company_db.commit()

                        # Perform the wavelet transform and hide the data in the image.
                        dvwstool.wavelet_transform(os.path.join("Diplomalar", diploma_adi_jpg), reed_solo.hex(), 'Gizlenenler')

                        # Show a success message.
                        error_label.config(text="KAYIT TAMAMLANDI")

            else:
                # If no students are found for the department, show an error message.
                error_label.config(text="BÖLÜM BULUNAMADI")

            # Close the database connections.
            school_db.close()
            company_db.close()

        except Exception as e:
            # If an exception occurs, show an error message.
            error_label.config(text=f"Lütfen Geçerli Bölüm Girin !")

    def main_processes(bolum, ad, soyad, tc, diploma_no):

        # Generate a key based on student information.
        key = bolum[:2] + ad[0] + tc[:2] + ad[-1] + soyad[0] + diploma_no[:2] + soyad[-1]

        # Convert the key to binary.
        binary_data = dvwstool.convert_to_binary(key)

        # Generate a SHA-256 hash of the binary data.
        hash_data = dvwstool.sha256_hash(binary_data)

        # Encrypt the hash data using AES.
        cyrpt_data = dvwstool.aes_encrypt(hash_data)

        # Encode the encrypted data using Reed-Solomon coding.
        reed_solo = dvwstool.reed_solomon_encode(cyrpt_data)

        return key, hash_data , reed_solo

    # Create a new top-level window for the steganography process.
    stego_window = tk.Toplevel(root)
    stego_window.title("STEGANOGRAPHY PROCESS")
    stego_window.configure(bg="black")

    # Get the screen dimensions.
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the window size and position.
    window_width = screen_width // 3
    window_height = screen_height // 2

    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    stego_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Load and set the background image.
    stego_background_image = Image.open("stgbg.png")
    resized_stego_background_image = stego_background_image.resize((window_width, window_height))
    stego_photo = ImageTk.PhotoImage(resized_stego_background_image)
    stego_background = tk.Label(stego_window, image=stego_photo)
    stego_background.image = stego_photo
    stego_background.place(x=0, y=0, relwidth=1, relheight=1)

    # Create and place the combobox label.
    combobox_label = tk.Label(stego_window, text="Type", bg="#1B1B1D", fg="white", font=("Helvetica", 14))
    combobox_label.place(relx=0.5, rely=0.27, anchor=tk.CENTER)

    # Create and place the combobox.
    options = ["Bireysel", "Bölüm"]
    combobox = ttk.Combobox(stego_window, values=options, state="readonly", font=("Helvetica", 11))
    combobox.current(0)
    combobox.place(relx=0.5, rely=0.34, anchor=tk.CENTER)

    # Create and place the diploma ID label.
    diploma_id_label = tk.Label(stego_window, text="ID / FACULTY", bg="#1B1B1D", fg="white", font=("Helvetica", 14))
    diploma_id_label.place(relx=0.5, rely=0.48, anchor=tk.CENTER)

    # Create and place the diploma entry field.
    diploma_entry = tk.Entry(stego_window, width=20, font=("Helvetica", 14))
    diploma_entry.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

    # Create and place the start button.
    start_button = ttk.Button(stego_window, text="Start", command=start_steganography)
    start_button.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

    # Create and place the error label.
    error_label = tk.Label(stego_window, fg="black")
    error_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    # Function to go back to the main menu.
    def go_back_to_menu():
        stego_window.destroy()

    # Create and place the back button.
    back_button = ttk.Button(stego_window, text="Back", command=go_back_to_menu)
    back_button.place(relx=0.5, rely=0.79, anchor=tk.CENTER)

    # Function to show the help window.
    def show_help():
        help_window = tk.Toplevel(stego_window)
        help_window.title("Help")
        help_window.geometry("400x400")
        help_window.configure(bg="#1B1B1D")

        help_label = tk.Label(help_window, text="How To Use The Steganography Process \n\n 1.Firstly, select the type of concealment you wish to\n perform from the dropdown menu."
                                                " If you're performing\n concealment on an individual's diploma image, choose \n 'ID' and enter the student ID."
                                                " If you intend to encrypt the \n data of students belonging to a specific department \n collectively,"
                                                " select 'Faculty'.\n\n"
                                                "2.Depending on your selection, enter the required ID \n or department name into the text box."
                                                " If you chose 'ID',\n enter the necessary ID. If you selected 'Faculty',\n enter the department name.\n\n"
                                                "3.Click on the 'Start' button to execute the command.\n\n"
                                                "4.To return to the main menu, click on the 'Back' button.",
                                                bg="#1B1B1D", fg="#ADFF2F", font=("Helvetica", 12))
        help_label.pack(expand=True, fill="both")

    # Create and place the help button.
    help_button = ttk.Button(stego_window, text="Help", command=show_help)
    help_button.place(relx=0.5, rely=0.72, anchor=tk.CENTER)

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
        company_db = pypyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=Company;Trusted_Connection=True;')
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
            school_db = pypyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=School;Trusted_Connection=True;')
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
button_style.configure("Custom.TButton", font=("Helvetica", 14), background="#1B1B1D")

# Add a button to start the steganography process.
diploma_label = tk.Label(main_menu_frame, text="PROCESS MENU ", bg="#1B1B1D", fg="white", font=("Helvetica", 24))
diploma_label.place(relx=0.5, rely=0.30, anchor=tk.CENTER)

# Add a button to start the steganography process.
steganography_button = ttk.Button(main_menu_frame, text="Steganography Process", command=steganography_process, style="Custom.TButton")
steganography_button.place(relx=0.5, rely=0.43, anchor=tk.CENTER)

# Create a frame for the security process and add a button.
security_frame = tk.Frame(main_menu_frame, bg="#1B1B1D")
security_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

security_button = ttk.Button(main_menu_frame, text="Verification Process", command=security_process, style="Custom.TButton")
security_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

# Add a button for the help process.
help_button = ttk.Button(main_menu_frame, text="Help Verification", command=lambda: help_process(), style="Custom.TButton")
help_button.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

def help_process():

    # Function to create a help window with instructions.
    help_window = tk.Toplevel(root)
    help_window.title("Help")
    help_window.geometry("300x150")
    help_window.configure(bg="#1B1B1D")

    help_label = tk.Label(help_window, text="How To Use Security Process\n\n1.Click the 'Verification Process' button.\n\n2. Select the image of the diploma.\n\n3. Confirm.", bg="#1B1B1D", fg="#ADFF2F", font=("Helvetica", 12))
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
