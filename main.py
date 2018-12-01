from fileServer import FileServer
from fileClient import FileClient
from utils import *
import sys

fileServer = FileServer()
fileClient = FileClient(fileServer.send_available_files)

while True:
    print_header("AVAILABLE COMMANDS")

    commands = [
        "Share new file",
        "List active connections",
        "List available files",
        "List shared files",
        "Broadcast available files",
        "Quit"
    ]

    for i, command in enumerate(commands):
        print("\t", change_style(str(i + 1) + ")", 'bold'), " ", command)

    option = input("\n" + change_style("Please enter your command", 'underline') + ": ")
    if option == "1":
        clear()
        print_header("SHARE NEW FILE")
        filepath = input("\n" + change_style("Enter absolute file path", 'underline') + ": ")
        filename = os.path.basename(filepath)
        if fileServer.add_file(filepath):
            print("\n\n")
            print("\t" + change_style(filename, "bold") + change_style(" is added successfully", "green"))
        else:
            print("\n\n")
            print("\t" + change_style(filename, "bold") + change_style(" is not valid file", "red"))
        enter_continue()
    elif option == "2":
        clear()
        enter_continue()
    elif option == "3":
        for file in fileClient.available_files:
            print(file.name)
        clear()
    elif option == "4":
        clear()
        print_header("SHARED FILES")
        print('-' * 86)
        print('| {0:s} | {1:s}| {2:s}|'.format("NAME".ljust(30), "CHUNK SIZE".ljust(12), "CHECKSUM".ljust(36)))
        print('-' * 86)
        for file in fileServer.shared_files.values():
            print('| {0:s} | {1:s}| {2:s}|'.format(change_style(file.name.ljust(30), 'bold'),
                                                   change_style(str(file.chunk_size).ljust(12), 'green'),
                                                   file.checksum.ljust(36)))
        print('-' * 86)
        enter_continue()
    elif option == "5":
        clear()
        print_notification("Good bye \n\n")
        sys.exit(0)
    else:
        clear()
        print_error("Invalid option")
