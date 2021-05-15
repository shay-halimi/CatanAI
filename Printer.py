class Printer:
    printer_on = True
    outfile = None
    machine_selected = 0
    permitted_machines = []

    @classmethod
    def use_machine(cls, index):
        cls.machine_selected = index

    @classmethod
    def ret_to_def_machine(cls):
        cls.machine_selected = 0

    @classmethod
    def set_permitted_machines(cls, permitted_machines):
        cls.permitted_machines = permitted_machines

    @classmethod
    def is_on(cls):
        return cls.printer_on

    @classmethod
    def turn_on(cls):
        cls.printer_on = True

    @classmethod
    def turn_off(cls):
        cls.printer_on = False

    @classmethod
    def set_outfile(cls, path):
        cls.outfile = open(path, 'w')
        cls.outfile.write("")
        cls.outfile = open(path, 'a')

    @classmethod
    def close_outfile(cls):
        cls.outfile.close()

    @classmethod
    def printer(cls, *args, sep=' ', end='\n'):
        if cls.printer_on and cls.permitted_machines[cls.machine_selected]:
            if cls.outfile is not None:
                cls.outfile.write("".join(map(str, args)) + end)
            else:
                print("".join(map(str, args)), sep=sep, end=end)
