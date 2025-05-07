# -*- coding: utf-8 -*-
import csv
import random

veriler = []  # Global olarak tanımlanan veriler listesi

def csviAc(Class):
    global veriler
    file = ""
    if Class == "":
        raise ValueError("Class değeri boş olamaz!")
    print(f"Gelen Class: {Class}")  # << burası kritik

    if Class == "A1":
        file = r"C:\Users\hanif\Unity\takimlasma donemi\Assets\PythonFiles\A1.csv"
    elif Class == "A2":
        file = r"C:\Users\hanif\Unity\takimlasma donemi\Assets\PythonFiles\A2.csv"
    elif Class == "B1":
        file = r"C:\Users\hanif\Unity\takimlasma donemi\Assets\PythonFiles\B1.csv"

    if file == "":
        raise FileNotFoundError(f"Class değeri '{Class}' için bir dosya tanımlı değil!")

    if not veriler:
        with open(file, mode="r", encoding="utf-8", errors="replace") as file:
            reader = list(csv.reader(file))
            veriler = [item[0].split(';') for item in reader]

    return veriler


def soruBilgileriRastgele(Class):
    csviAc(Class)
    global veriler  # Global listeyi kullan

    index = random.randint(1, len(veriler) - 1)  # Rastgele bir indeks seç
    questionGroup = veriler.pop(index)  # Seçilen veriyi listeden sil
    slicedAnswer = questionGroup[1].split(" ")
    randomizedSlicedAnswer = questionGroup[1].split(" ")
    random.shuffle(randomizedSlicedAnswer)

    question = {
        "questionText": questionGroup[0],
        "questionAnswer": questionGroup[1],
        "slicedAnswer": randomizedSlicedAnswer,
        "notRandomizedSlicedAnswer": slicedAnswer,
        "Class" : Class
    }

    return question

def csvSayisi(Class):
    
    sayi = len(csviAc(Class))
    return sayi
