import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import pypyodbc
import dvwstool

def login():
    entered_username = username_entry.get()
    entered_password = password_entry.get()

    try:
        db = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-GLNTNNB\SQLEXPRESS;Database=Company;Trusted_Connection=True;')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM login WHERE username=? AND password=?", (entered_username, entered_password))
        user = cursor.fetchone()

        if user:
            username, password, effect = user  # Kullanıcı bilgilerini al
            messagebox.showinfo("Başarılı", "Giriş başarılı!")
            open_main_menu(effect)  # Ana menüyü açarken etki değerini de iletebilirsiniz
        else:
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı veya şifre!")

        db.close()

    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", f"Veritabanı hatası oluştu: {str(e)}")

def open_main_menu(effect):
    login_frame.pack_forget()
    main_menu_frame.pack(fill="both", expand=True)

    if effect == "0":
        steganography_button.config(state="normal")  # Steganografi butonunu etkinleştir
    elif effect == "1":
        steganography_button.config(state="disabled")  # Steganografi butonunu devre dışı bırak
    else:
        # Farklı etki değerlerine göre burada farklı işlemler yapabilirsiniz
        pass

def go_back_to_main_menu(stego_window):
    stego_window.destroy()  # Stego penceresini kapat

    diploma_entry.delete(0, tk.END)  # Diploma ID giriş alanını temizle

def steganography_process():
    def start_steganography():
        selection = combobox.get()
        if selection == "Bireysel":
            process_individual()
        elif selection == "Bölüm":
            process_department()

    def process_individual():
        diploma_id = diploma_entry.get()
        if not diploma_id:
            error_label.config(text="LÜTFEN BİR DİPLOMA NUMARASI GİRİNİZ")
            return

        try:
            school_db = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-GLNTNNB\SQLEXPRESS;Database=School;Trusted_Connection=True;')
            school_cursor = school_db.cursor()

            school_cursor.execute("SELECT Bolum, Ad, Soyad, Tc, DiplomaNo FROM Student WHERE DiplomaNo=?", (diploma_id,))
            student_info = school_cursor.fetchone()

            if student_info:
                bolum, ad, soyad, tc, diploma_no = student_info

                key, hash_data = process_keys(bolum, ad, soyad, tc, diploma_no)

                company_db = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-GLNTNNB\SQLEXPRESS;Database=Company;Trusted_Connection=True;')
                company_cursor = company_db.cursor()

                company_cursor.execute("SELECT [Key] FROM KEYS WHERE [Key]=?", (key,))
                existing_key = company_cursor.fetchone()

                if existing_key:
                    error_label.config(text="BU ANAHTAR ZATEN KULLANILIYOR")
                else:
                    company_cursor.execute("INSERT INTO KEYS ([Key], HashData) VALUES (?, CONVERT(varbinary(max), ?))", (key, hash_data))

                    company_db.commit()
                    error_label.config(text="KAYIT TAMAMLANDI")
            else:
                error_label.config(text="ÖĞRENCİ BULUNAMADI")

            school_db.close()
            company_db.close()

        except Exception as e:
            error_label.config(text=f"Lütfen Geçerli Id Girin !")
            print(str(e))

    def process_department():
        department_name = diploma_entry.get()
        if not department_name:
            error_label.config(text="LÜTFEN BİR BÖLÜM ADI GİRİNİZ")
            return

        try:
            school_db = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-GLNTNNB\SQLEXPRESS;Database=School;Trusted_Connection=True;')
            school_cursor = school_db.cursor()

            school_cursor.execute("SELECT Bolum, Ad, Soyad, Tc, DiplomaNo FROM Student WHERE Bolum=?", (department_name,))
            students_info = school_cursor.fetchall()

            if students_info:
                company_db = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-GLNTNNB\SQLEXPRESS;Database=Company;Trusted_Connection=True;')
                company_cursor = company_db.cursor()

                for student_info in students_info:
                    bolum, ad, soyad, tc, diploma_no = student_info

                    key, hash_data = process_keys(bolum, ad, soyad, tc, diploma_no)

                    company_cursor.execute("SELECT [Key] FROM KEYS WHERE [Key]=?", (key,))
                    existing_key = company_cursor.fetchone()

                    if existing_key:
                        error_label.config(text=f"Daha önce kayıt mevcut fakat mevcut olmayanlar eklendi.")
                    else:
                        company_cursor.execute("INSERT INTO KEYS ([Key], HashData) VALUES (?, CONVERT(varbinary(max), ?))", (key, hash_data))
                        company_db.commit()
                        error_label.config(text="KAYIT TAMAMLANDI")

            else:
                error_label.config(text="BÖLÜM BULUNAMADI")

            school_db.close()
            company_db.close()

        except Exception as e:
            error_label.config(text=f"Lütfen Geçerli Bölüm Girin !")
            print(str(e))

    def process_keys(bolum, ad, soyad, tc, diploma_no):

        key = bolum[:2] + ad[0] + tc[:2] + ad[-1] + soyad[0] + diploma_no[:2] + soyad[-1]

        binary_data = dvwstool.metni_ikiliye_donustur(key)

        hash_data = dvwstool.sha256_hash(binary_data)

        cyrpt_data = dvwstool.aes_encrypt(hash_data)

        reed_solo = dvwstool.reed_solomon_kodlama(cyrpt_data)

        #stego =

        return key, hash_data

    stego_window = tk.Toplevel(root)
    stego_window.title("STEGANOGRAPHY PROCESS")
    stego_window.configure(bg="black")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = screen_width // 3
    window_height = screen_height // 2

    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    stego_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    stego_background_image = Image.open("stgbg.png")
    resized_stego_background_image = stego_background_image.resize((window_width, window_height))
    stego_photo = ImageTk.PhotoImage(resized_stego_background_image)
    stego_background = tk.Label(stego_window, image=stego_photo)
    stego_background.image = stego_photo
    stego_background.place(x=0, y=0, relwidth=1, relheight=1)

    combobox_label = tk.Label(stego_window, text="Type", fg="black", font=("Helvetica", 14))
    combobox_label.place(relx=0.5, rely=0.23, anchor=tk.CENTER)

    options = ["Bireysel", "Bölüm"]
    combobox = ttk.Combobox(stego_window, values=options, state="readonly", font=("Helvetica", 14))
    combobox.current(0)
    combobox.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

    diploma_id_label = tk.Label(stego_window, text="ID / FACULTY", fg="black", font=("Helvetica", 14))
    diploma_id_label.place(relx=0.5, rely=0.43, anchor=tk.CENTER)

    diploma_entry = tk.Entry(stego_window, width=30, font=("Helvetica", 14))
    diploma_entry.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    start_button = ttk.Button(stego_window, text="Start", command=start_steganography)
    start_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    back_button = ttk.Button(stego_window, text="Back", command=stego_window.destroy)
    back_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    error_label = tk.Label(stego_window, fg="black")
    error_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    def go_back_to_menu():
        stego_window.destroy()

    back_button = ttk.Button(stego_window, text="Back", command=go_back_to_menu)
    back_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

def security_process():
    def select_image():
        filename = filedialog.askopenfilename(initialdir="/", title="Resim Seç", filetypes=(("Resim Dosyaları", "*.jpg;*.png;*.jpeg"), ("Tüm Dosyalar", "*.*")))
        if not filename:
            messagebox.showerror("Hata", "Lütfen bir resim seçin!")
            return

        # Seçilen resmi işle
        messagebox.showinfo("Bilgi", f"Seçilen resim: {filename}")

    def start_security():
        filename = filedialog.askopenfilename(initialdir="/", title="Resim Seç", filetypes=(("Resim Dosyaları", "*.jpg;*.png;*.jpeg"), ("Tüm Dosyalar", "*.*")))
        if not filename:
            messagebox.showerror("Hata", "Lütfen bir resim seçin!")
            return
    # reed_cözme = dvwstool.reed_solomon_cozme(reed_solo)

    # decyrpt_data = dvwstool.aes_decrypt(reed_cözme)

        messagebox.showinfo("Bilgi", "Diploma güvenliği işlemi başarıyla tamamlandı!")

    start_security()

def close_window():
    root.destroy()

def resize_image(event):
    global resized_image
    new_width = event.width
    new_height = event.height
    resized_image = original_image.resize((new_width, new_height))
    photo = ImageTk.PhotoImage(resized_image)
    canvas.itemconfig(background, image=photo)
    canvas.image = photo
    canvas.coords(background, new_width // 2, new_height // 2)

root = tk.Tk()
root.title("Steganography ve Diploma Güvenliği Uygulaması")
root.attributes('-fullscreen', True) # Tam ekran yap
root.configure(bg="#E9DEC2")

# Giriş sayfası
login_frame = tk.Frame(root, bg="#E9DEC2")
login_frame.pack(fill="both", expand=True)

# Arkaplan resmini yükle
login_background_image = Image.open("log.png")  # Arka plan resmi dosyasının adını belirtin
resized_login_background_image = login_background_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
login_photo = ImageTk.PhotoImage(resized_login_background_image)
login_background = tk.Label(login_frame, image=login_photo)
login_background.image = login_photo
login_background.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

login_label = tk.Label(login_frame, text="LOGIN MENU", bg="#F0E1CB", fg="black", font=("Helvetica", 24))
login_label.place(relx=0.5, rely=0.44, anchor=tk.CENTER)

username_label = tk.Label(login_frame, text="USERNAME", bg="#ECDCC3", fg="black", font=("Helvetica", 14))
username_label.place(relx=0.41, rely=0.52, anchor=tk.CENTER)
username_entry = tk.Entry(login_frame, font=("Helvetica", 14))
username_entry.place(relx=0.525, rely=0.52, anchor=tk.CENTER)

password_label = tk.Label(login_frame, text="PASSWORD", bg="#E4D3B7", fg="black", font=("Helvetica", 14))
password_label.place(relx=0.41, rely=0.62, anchor=tk.CENTER)
password_entry = tk.Entry(login_frame, show="*", font=("Helvetica", 14))
password_entry.place(relx=0.525, rely=0.62, anchor=tk.CENTER)

login_button = ttk.Button(login_frame, text="Log In", command=login, width=20)
login_button.place(relx=0.5, rely=0.71, anchor=tk.CENTER)

exit_button_login = ttk.Button(login_frame, text="Exit", command=close_window, width=20)
exit_button_login.place(relx=0.5, rely=0.76, anchor=tk.CENTER)

# Ana menü
main_menu_frame = tk.Frame(root, bg="#E9DEC2")

# Arka plan resmini eklemek için Canvas
canvas = tk.Canvas(main_menu_frame)
canvas.pack(fill="both", expand=True)

# Arkaplan resmini yükle
original_image = Image.open("menü.png")  # Arka plan resmi dosyasının adını belirtin
resized_image = original_image
photo = ImageTk.PhotoImage(original_image)
background = canvas.create_image(0, 0, anchor=tk.CENTER, image=photo)

# Arkaplan resmini yeniden boyutlandır
canvas.bind("<Configure>", resize_image)

button_style = ttk.Style()
button_style.configure("Custom.TButton", font=("Helvetica", 14), background="#E9DEC2")

# Process Menü yazısı
diploma_label = tk.Label(main_menu_frame, text="PROCESS MENU ", bg="#F0E1CB", fg="black", font=("Helvetica", 24))
diploma_label.place(relx=0.5, rely=0.45, anchor=tk.CENTER)


steganography_button = ttk.Button(main_menu_frame, text="Steganography Process", command=steganography_process, style="Custom.TButton")
steganography_button.place(relx=0.5, rely=0.53, anchor=tk.CENTER)

# Diploma güvenliği işlemi için giriş bölümü
security_frame = tk.Frame(main_menu_frame, bg="#E9DEC2")
security_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

security_button = ttk.Button(main_menu_frame, text="Verification Process", command=security_process, style="Custom.TButton")
security_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

def go_back_to_login():
    main_menu_frame.pack_forget()
    login_frame.pack(fill="both", expand=True)
    username_entry.delete(0, tk.END)  # Kullanıcı adı giriş alanını temizle
    password_entry.delete(0, tk.END)  # Şifre giriş alanını temizle
    #diploma_entry.delete(0, tk.END)  # Diploma ID giriş alanını temizle

back_button = ttk.Button(main_menu_frame, text="Back ", command=go_back_to_login, style="Custom.TButton", width=20)
back_button.place(relx=0.5, rely=0.71, anchor=tk.CENTER)

exit_button_main = ttk.Button(main_menu_frame, text="Exit", command=close_window, style="Custom.TButton", width=20)
exit_button_main.place(relx=0.5, rely=0.76, anchor=tk.CENTER)

root.mainloop()
