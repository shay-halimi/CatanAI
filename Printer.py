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
    def set_outfile(cls, path):
        cls.outfile = open(path, 'w')
        cls.outfile.write("")
        cls.outfile = open(path, 'a')

    @classmethod
    def close_outfile(cls):
        cls.outfile.close()

    @classmethod
    def printer(cls, *args, sep=' ', end='\n'):
        if cls.printer_on:
            if cls.outfile is not None:
                cls.outfile.write("".join(map(str, args)) + end)
            else:
                print("".join(map(str, args)), sep=sep, end=end)
