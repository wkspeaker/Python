import random
import math
import decimal
from sympy import *

piString = N(pi,400)

def generate_key_and_password(CodeLength, Segments):
    key = ""
    password = ""

    if Segments == 1:
        StartPosition = random.randint(1, 300 - CodeLength)
        FetchLength = CodeLength
        key += str(StartPosition) + "|" + str(FetchLength)
        password += str(piString)[StartPosition:StartPosition+FetchLength]
    else:
        segments = []
        total_length = CodeLength
        for i in range(Segments-1):
            segment_length = random.randint(1, total_length-1)
            segments.append(segment_length)
            total_length -= segment_length
        segments.append(total_length)

        StartPositions = []
        FetchLengths = []
        for segment_length in segments:
            StartPosition = random.randint(1, 300 - segment_length)
            FetchLength = segment_length
            StartPositions.append(StartPosition)
            FetchLengths.append(FetchLength)
            key += str(StartPosition) + "|" + str(FetchLength) + "|"
        
        for i in range(len(StartPositions)):
            password += str(piString)[StartPositions[i]:StartPositions[i]+FetchLengths[i]]
    
    return key, password

def calculate_password(key):
    key_parts = key.split("|")
    StartPositions = [int(pos) for pos in key_parts[::2] if pos]
    FetchLengths = [int(length) for length in key_parts[1::2] if length]

    password = ""
    for i in range(len(StartPositions)):
        password += str(piString)[StartPositions[i]:StartPositions[i]+FetchLengths[i]]

    return password

generate_method = ""
while generate_method != "3":
    generate_method = input("Choose password generation method (1 for CodeLength and Segments, 2 for Key, 3 to leave): ")

    if generate_method == "1":
        CodeLength = int(input("Enter the desired password length: "))
        Segments = int(input("Enter the number of segments: "))

        key, password = generate_key_and_password(CodeLength, Segments)
        print("Generated Key:", key)
        print("Generated Password:", password)

        #calculated_password = calculate_password(key)
        #print("Calculated Password:", calculated_password)

    elif generate_method == "2":
        key = input("Enter the key: ")

        password = calculate_password(key)
        print("Generated Password:", password)

    elif generate_method == "3":
        print("Leaving the program...")
        break

    else:
        print("Invalid input. Please choose either 1, 2, or 3 for the password generation method.")