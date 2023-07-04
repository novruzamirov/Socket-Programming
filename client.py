# Novruz Amirov
# Student ID: 150200903
# BLG 433E - Socket Programming Project

# In order to be able to run the program successively, you need to have installed PySimpleGUI library in Python.
# If you do not have it, you can install it using pip, by writing "pip install PySimpleGUI"
# After you get the message "Successfully installed PySimpleGUI-4.60.4", (the version is not that important, it will automatically download the last version)
# Run python3 client.py to run the program, and make a fun of a Game)

import PySimpleGUI as sg
import socket
import hashlib
import struct
import threading
import os

# Layout for Simple Graphical User Interface
layout = [
    [sg.Text("USER: ", visible = False, key = '-USER_TEXT-'), sg.Text("", visible = False, key = '-USER-')],
    [sg.Text("NOTIFICATION: ", visible = False, key = '-NOTIFICATION_TEXT-'), sg.Text("", visible = False, key = '-NOTIFICATION-')],
    [sg.Text("TO PLAY THE GAME CONNECTION TO THE SERVER IS REQUIRED", key = '-CONNECTION_TEXT-')],
    [sg.Text("Your Choice:", visible = False, key = '-CHOICE-')],
    [sg.Text("What is your Guess for the Answer", visible = False)],
    [sg.Text("CAN NOT CONNECT TO THE SERVER", visible = False, key = '-CONNECTION_ERROR-')],
    [sg.Text("THE NUMBER OF LETTERS: ", visible = False, key = '-NUM_OF_LETTERS_TEXT-'), sg.Text("", visible = False, key = '-NUM_OF_LETTERS-')],
    [sg.Text("THE QUESTION: ", visible = False, key = '-QUESTION_TEXT-'), sg.Text("", visible = False, key = '-QUESTION-')],
    [sg.Text("THE INFORMATION: ", visible = False, key = '-INFORMATION_TEXT-'), sg.Text("", visible = False, key = '-INFORMATION-')],
    [sg.Text("THE LETTER FROM WORD: ", visible = False, key = '-LETTER_WORD_TEXT-'), sg.Text("", visible = False, key = '-LETTER_WORD-')],
    [sg.Text("THE POSITION OF LETTER: ", visible = False, key = '-POSITION_LETTER_TEXT-'), sg.Text("", visible = False, key = '-POSITION_LETTER-')],
    [sg.Text("THE REMAINING TIME: ", visible = False, key = '-REMAINING_TIME_TEXT-'), sg.Text("", visible = False, key = '-REMAINING_TIME-')],
    [sg.Text("THE OVERALL SCORE: ", visible = False, key = '-OVERALL_SCORE_TEXT-'), sg.Text("", visible = False, key = '-OVERALL_SCORE-')],
    [sg.Button("CONNECT TO THE SERVER", key = '-CONNECTION_BUTTON-')],
    [sg.Button("00: TO START THE GAME", visible = False, key = '00')],
    [sg.Button("01: TO EXIT THE GAME", visible = False, key ='01')],
    [sg.Button("02: TO FETCH THE QUESTION", visible = False, key = '02')],
    [sg.Button("03: TO GET A LETTER", visible = False, key = '03')],
    [sg.Button("04: TO TAKE A GUESS", visible = False, key = '04'), sg.Input(visible = False, key = 'answer-guess')],
    [sg.Button("05: TO GET THE REMAINING TIME", visible = False, key = '05')],
    [sg.Input(visible = False)]
]

#Creating Window for GUI:
window = sg.Window("CLIENT-SERVER COMMUNICATION WITH A SIMPLE AUTHENTICATION PROTOCOL", layout)

# Part 1 -> Authentication Mechanism
serverName = "160.75.154.126" # given IPv4 address for the assignment
serverPort = 2022 # given port number for the assignment

# creation of the socket:
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_server():
    clientSocket.connect((serverName, serverPort)) # connecting to the server
    msg = "Start_Connection" 
    clientSocket.send(msg.encode()) # to initiate the protocol

    randomHex = clientSocket.recv(1024).decode("utf-8") 
    hexKey = "3F7AA4FA59945E475E4290A8982C0EB6"
    hex = randomHex + hexKey 

    key_digested = hashlib.sha1(hex.encode()).digest() # unsigned char with the size of 20 bytes
    key_hexdigested = hashlib.sha1(hex.encode()).hexdigest() # converting byte stream to hex (40 bytes)
    student_id = "#150200903" # the student number with '#' symbol
    final_key = key_hexdigested + student_id # 50 bytes total (40bytes hex + 10bytes student id) key

    clientSocket.send(final_key.encode())
    received_message = clientSocket.recv(1024).decode("utf-8")
    print(received_message)

    # we do not need to send 'Y' to start the game, that is why I commented them.
    # answer = 'Y'
    # clientSocket.send(answer.encode())

    update_messages_false()
    window['-NOTIFICATION_TEXT-'].update(visible = True)
    window['-NOTIFICATION-'].update(visible = True)
    window['-NOTIFICATION-'].update(received_message)

    # Threading for Asynchronous Communication
    # HINT: Use different threads for incoming/outgoing data. (from PDF)
    thread_receiving = threading.Thread(target=client_accepts)
    thread_receiving.start()


# to make all elements on the UI invisible 
def update_messages_false():
    window['-NOTIFICATION-'].update(visible = False)
    window['-NOTIFICATION_TEXT-'].update(visible = False)
    window['-CONNECTION_TEXT-'].update(visible = False)
    window['-CHOICE-'].update(visible = False)
    window['-CONNECTION_ERROR-'].update(visible = False)
    window['-NUM_OF_LETTERS_TEXT-'].update(visible = False)
    window['-NUM_OF_LETTERS-'].update(visible = False)
    window['-QUESTION_TEXT-'].update(visible = False)
    window['-QUESTION-'].update(visible = False)
    window['-INFORMATION_TEXT-'].update(visible = False)
    window['-INFORMATION-'].update(visible = False)
    window['-LETTER_WORD_TEXT-'].update(visible = False)
    window['-LETTER_WORD-'].update(visible = False)
    window['-POSITION_LETTER_TEXT-'].update(visible = False)
    window['-POSITION_LETTER-'].update(visible = False)
    window['-REMAINING_TIME_TEXT-'].update(visible = False)
    window['-REMAINING_TIME-'].update(visible = False)
    window['-OVERALL_SCORE_TEXT-'].update(visible = False)
    window['-OVERALL_SCORE-'].update(visible = False)


# If the problem occurs while decoding for the given encoding type on the packets coming from
# server this method will try to use other decode() methods after getting an error from decode(encoding_type)
# For most cases, this method should not work because the server sends the encoding type correctly
def decoding_problem(encoded_message):
    try:
        return encoded_message.decode()

    except:
        try:
            return encoded_message.decode("ISO-8859-1")

        except:
            return "Could not able to decode the message!" 


# Function to accept the messages from server, and display it according to packet type
# Server-Side Packets:
def client_accepts():
    while True:
        result = clientSocket.recv(1024)
        packet_type = struct.unpack('B', result[0:1]) # first byte of packet
        encoding_type = struct.unpack('B', result[1:2]) # can or can not be used according to packet type
        encoding_utf = "utf-8" # if enc. type is 0, then utf-8, otherwise utf-16 (as written in pdf)

        if(encoding_type[0] == 1):
            encoding_utf = "utf-16" 

        if(packet_type[0] == 0): # Information 
            try:
                size_of_payload = struct.unpack('<H', result[2:4])[0] # little-endian (because of int16)

                # utf-8 can use up to 2 bytes, while utf-16 can use up to 4 bytes
                if encoding_type[0] == 0:
                    size_of_payload *= 2

                elif encoding_type[0] == 1:
                    size_of_payload *= 4
                    
                payload = result[4 : 4 + size_of_payload].decode(encoding_utf)

                # Setting every Text file as invisible, and make the necessary ones visible
                update_messages_false()
                window['-INFORMATION_TEXT-'].update(visible = True)
                window['-INFORMATION-'].update(visible = True)
                window['-INFORMATION-'].update(payload)
                
                print("\nThe Information: ", payload)

            except:
                print("\nThe Information: ", decoding_problem(result[4:-1]))

        elif(packet_type[0] == 1): # Question
            try:
                size_of_payload = struct.unpack('<H', result[2:4])[0] # little-endian (because of int16)

                # utf-8 can use up to 2 bytes, while utf-16 can use up to 4 bytes
                if encoding_type[0] == 0:
                    size_of_payload *= 2

                elif encoding_type[0] == 1:
                    size_of_payload *= 4

                payload_part1 = struct.unpack('<H', result[4:6])[0]
                print("\nLength of the word: ", payload_part1)
                payload_part2 = result[6:6+size_of_payload].decode(encoding_utf)
                print("The Question text: ", payload_part2)

                # Setting every Text file as invisible, and make the necessary ones visible
                update_messages_false()
                window['-NUM_OF_LETTERS_TEXT-'].update(visible = True)
                window['-NUM_OF_LETTERS-'].update(visible = True)
                window['-NUM_OF_LETTERS-'].update(payload_part1)

                window['-QUESTION_TEXT-'].update(visible = True)
                window['-QUESTION-'].update(visible = True)
                window['-QUESTION-'].update(payload_part2)

            except:
                print("The Question text: ", decoding_problem(result[6:-1]))

        elif(packet_type[0] == 2): # the Letter from Word 
            try:
                pos_of_letter = struct.unpack('b', result[2:3])
                letter = struct.unpack('c', result[3:4])
                print("\nPosition of letter: ", pos_of_letter[0])
                print("The Letter: ", letter[0].decode("utf-8"))

                update_messages_false()
                window['-QUESTION_TEXT-'].update(visible = True)
                window['-QUESTION-'].update(visible = True)
                window['-NUM_OF_LETTERS_TEXT-'].update(visible = True)
                window['-NUM_OF_LETTERS-'].update(visible = True)
                # window['-NUM_OF_LETTERS-'].update(visible = True)

                window['-LETTER_WORD_TEXT-'].update(visible = True)
                window['-LETTER_WORD-'].update(letter[0].decode("utf-8"))
                window['-LETTER_WORD-'].update(visible = True)

                window['-POSITION_LETTER_TEXT-'].update(visible = True)
                window['-POSITION_LETTER-'].update(pos_of_letter[0])
                window['-POSITION_LETTER-'].update(visible = True)

            except:
                print("\nThe Letter from Word: ", decoding_problem(letter[0]))

        elif(packet_type[0] == 3): # the Remaining Time
            try:
                rem_time = struct.unpack('<H', result[4:6]) # little-endian (because of int16)
                print("\nRemaining Time: ", rem_time[0], " seconds")

                window['-REMAINING_TIME_TEXT-'].update(visible = True)
                window['-REMAINING_TIME-'].update(visible = True)
                window['-REMAINING_TIME-'].update(rem_time[0])

            except:
                print("Could not handle with Remaining time Message from Server")

        elif(packet_type[0] == 4): # End of the Game
            try:
                overall_score = struct.unpack('<H', result[2:4])
                rem_time = struct.unpack('<H', result[4:6]) # little-endian (because of int16)
                print("\nOverall Score: ", overall_score[0])
                print("Remaining Time in seconds: ", rem_time[0])
                print("The End of Game\n")

                update_messages_false()
                window['-NOTIFICATION_TEXT-'].update(visible = True)
                window['-NOTIFICATION-'].update(visible = True)
                window['-NOTIFICATION-'].update("THE END OF THE GAME!!!")
                window['-OVERALL_SCORE_TEXT-'].update(visible = True)
                window['-OVERALL_SCORE-'].update(visible = True)
                window['-OVERALL_SCORE-'].update(overall_score[0])
                window['-REMAINING_TIME_TEXT-'].update(visible = True)
                window['-REMAINING_TIME-'].update(visible = True)
                window['-REMAINING_TIME-'].update(rem_time[0])
                
            except:
                print("Could not able to handle with the End of Game server packet")

# Client-Side Packets (6 different packets can be sent by client)
def user_interface():
    while True:
        event, values = window.read()

        # if window is closed then stop the program
        if event == sg.WIN_CLOSED:
            os._exit(0)

        if event == "-CONNECTION_BUTTON-":
            try:
                connect_server()
                window['-CONNECTION_TEXT-'].update(visible = False)
                window['-CONNECTION_BUTTON-'].update(visible = False)
                window['00'].update(visible = True)
                window['01'].update(visible = True)
                window['02'].update(visible = True)
                window['03'].update(visible = True)
                window['04'].update(visible = True)
                window['answer-guess'].update(visible = True)
                window['05'].update(visible = True)

            except:
                window['-CONNECTION_ERROR-'].update(visible = True)
                print("Connection could not be Established")
                break

        if event == '00': # to Start the Game
            try:
                sender = struct.pack('b', 0)
                clientSocket.send(sender)
                print("Instruction 00 sended to server")

            except:
                print("Could not send the Start the Game message")

        if event == '01': # to Terminate the Game
            try:
                sender = struct.pack('b', 1)
                clientSocket.send(sender)
                print("Instruction 01 sended to server")

            except:
                print("Could not send the Terminate the Game message")

        if event == '02': # Fetch the (next) Question
            try:
                sender = struct.pack('b', 2)
                clientSocket.send(sender)
                print("Instruction 02 sended to server")

            except:
                print("Could not send Fetch the Question message")

        if event == '03': # To buy a Letter
            try:
                sender = struct.pack('b', 3)
                clientSocket.send(sender)
                print("Instruction 03 sended to server")

            except:
                print("Could not send Buy a Letter message")

        if event == '05': # to Get the Remaining Time
            try:
                sender = struct.pack('b', 5)
                clientSocket.send(sender)
                print("Instruction 05 sended to server")

            except:
                print("Could not send Get the Remaining Time message")

        # only in this part, we will send a Payload in addition to Instruction_type
        if event == '04': # To Take A Guess
            try:
                response = layout[18][1].get()
                sended_response = "04" + response
                packed_result =  struct.pack('{}s'.format(len(sended_response)), sended_response.encode())
                packed_result = struct.pack('B{}s'.format(len(response)), 4, response.encode())
                clientSocket.send(packed_result)
                print("The Guess was sended Successfully: ")

            except:
                print("Could not send Take a Guess message")

user_interface()


# Threading for Asynchronous Communication
# HINT: Use different threads for incoming/outgoing data. (from PDF)
thread_interface = threading.Thread(target=user_interface)
thread_interface.start()

window.close()