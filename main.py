import multiprocessing
import subprocess


def run_comm_program():
    subprocess.run(["python", "path/to/your/first/program/first_program.py"])


def run_gui_program():
    subprocess.run(["python", "path/to/your/second/program/second_program.py"])


if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_comm_program)

    p2 = multiprocessing.Process(target=run_gui_program)

    p1.start()

    p2.start()

    p1.join()

    p2.join()
