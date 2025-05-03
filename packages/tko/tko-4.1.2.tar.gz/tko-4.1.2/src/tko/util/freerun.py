import subprocess
from .text import Text, Token
from .raw_terminal import RawTerminal
from ..play.images import compilling
from .runner import Runner
from ..run.solver_builder import SolverBuilder
import random
import select
import sys

class Free:
    @staticmethod
    def free_run(solver: SolverBuilder, show_compilling:bool=True, to_clear: bool=True, wait_input:bool=True, header: Text = Text()) -> bool:

        if to_clear:
            Runner.clear_screen()
        if show_compilling:
            image = random.choice(list(compilling.keys()))
            for line in compilling[image].splitlines():
                print(Text().addf("y", line).center(RawTerminal.get_terminal_size(), Token(" ")))

        if show_compilling:
            Runner.clear_screen()
        solver.prepare_exec(free_run_mode=True)
        if solver.has_compile_error():
            exec, _ = solver.get_executable()
            print(exec.get_error_msg())
        else:
            exec, _ = solver.get_executable()
            cmd, folder = exec.get_command()
            if folder == "":
                folder = None
            if header.len() == 0:
                print(Text().center(RawTerminal.get_terminal_size(), Token("─")))
            else:
                print(header.center(RawTerminal.get_terminal_size(), Token("─")))
            answer = subprocess.run(cmd, cwd=folder, shell=True, text=True)
            if answer.returncode != 0 and answer.returncode != 1:
                print(Runner.decode_code(answer.returncode))
        solver.reset()
        to_run_again = False
        if wait_input:
            while select.select([sys.stdin], [], [], 0)[0]:
                sys.stdin.readline()
            print(Text().center(RawTerminal.get_terminal_size(), Token("─")))
            print(Text.format("Para [recompilar e] reexecutar digite: {y}", "<enter>"))
            print(Text.format("Para voltar para tela anterior digite: {y}", "q<enter>"))
            # clear buffer before get input

            valor = input()
            if valor != "n" and valor != "q":
                if to_clear:
                    Runner.clear_screen()
                to_run_again = True
        if to_clear:
            Runner.clear_screen()

        return to_run_again