class CSV:
    """creates or appends to an existing csv file with dict as an input

    Args:
        filename (str): filename with filepath 
        delimiter (str, optional): can be anything as long as it is not used anywhere else in the file. Defaults to ','.
        headers (bool, optional): is it a new file or if should be appended. Defaults to True.
    """

    def __init__(self, file_object, delimiter=',') -> None:
        """
        Initializes a CSV object.

        Args:
            file_object (file object): File object to read/write CSV data from/to.
            delimiter (str, optional): Delimiter character to separate values in the CSV file. Default is ','.
        """
        self.file_object = file_object
        self.delimiter = delimiter
        # self.kwargs = kwargs

    def write_header(self, headers):
        """
        Writes the headers to the CSV file.

        Args:
            headers (list): List of header strings to be written to the CSV file.
        """
        header = self.delimiter.join(head for head in headers)
        self.file_object.write(f'{header}\n')

    def write_line(self, read_write=False, **kwargs):
        """
        Writes a line of data to the CSV file.

        Args:
            read_write (bool, optional): If True, reads the headers from the file and writes only specified values in the order they appear. If False, writes all keyword arguments as separate values. Default is False.
            **kwargs: Keyword arguments with data to be written to the CSV file.
        """
        if not read_write:
            line = self.delimiter.join(str(value) for key, value in kwargs.items())
            self.file_object.write(f'{line}\n')
        else:
            headers = self.get_headers(self.file_object.read())
            # print(a.split('\n')[0].split(','))
            line = self.delimiter.join(str(kwargs[head]) for head in headers)
            self.file_object.write(f'{line}\n')
            pass

    def get_headers(self, text):
        """
        Gets the headers from the CSV file.

        Args:
            text (str): String representation of the CSV file.

        Returns:
            headers (list): List of header strings from the CSV file.
        """
        return text.split('\n')[0].split(',')


if __name__ == '__main__':
    test = {
        'col-1': 1,
        'col-2': 2,
        'col-3': 3,
    }
    test1 = {
        'col-1': 4,
        'col-2': 5,
        'col-3': 6,
    }

    with open('test.csv', 'r+') as f:
        csv = CSV(f)
        # csv.write_header(test1)
        csv.write_line(read_write=True, **test)
        # csv.write_line(**test1)
