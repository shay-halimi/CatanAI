class Printer:
    printer_on = True
    outfile = None

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
    def print_to_outfile(cls, path):
        cls.outfile = path

    @classmethod
    def printer(cls, *args, sep=' ', end='\n', file=None):
        if cls.printer_on:
            if file is None:
                file = cls.outfile
            print("".join(map(str,args)), sep=sep, end=end, file=file)
