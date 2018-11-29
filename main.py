from fileServer import FileServer
from fileClient import FileClient
from utils import *
import sys

fileServer = FileServer()
fileClient = FileClient(fileServer.send_available_files)

while True:
    print_header("AVAILABLE COMMANDS")

    commands = ["List active downloads", "List available files", "Add file", "List shared files",
                "Broadcast available files", "Quit"]

    # if total_unread:
    #     commands[1] = "Send message (" + change_style(str(total_unread) + " unread messages", "green") + ")"

    for i, command in enumerate(commands):
        print("\t", change_style(str(i + 1) + ")", 'bold'), " ", command)

    option = input("\n" + change_style("Please enter your command", 'underline') + ": ")
    if option == "1":
        clear()
        enter_continue()
    elif option == "2":
        clear()
    elif option == "3":
        clear()
        enter_continue()
    elif option == "4":
        clear()
        print_header("DISCOVER NEW USERS")
        ip = input("\n" + change_style("Enter user IP for discovery", 'underline') + ": ")
    elif option == "5":
        clear()
        print_notification("Good bye " + server.username + " \n\n")
        sys.exit(0)
    else:
        clear()
        print_error("Invalid option")
