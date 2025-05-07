from unitelabs.cdk import sila


class UnobservableCommandTest(sila.Feature):
    """Feature for testing unobservable commands."""

    def __init__(self):
        super().__init__(
            originator="org.silastandard",
            category="test",
            version="1.0",
        )

    @sila.UnobservableCommand()
    def command_without_parameters_and_responses(self) -> None:
        """
        Send nothing, get nothing.

        An unparametrized void command.
        """

    @sila.UnobservableCommand()
    @sila.Response(name="String Representation")
    def convert_integer_to_string(self, integer: int) -> str:
        """
        Convert an integer to a string.

        .. parameter:: An integer, e.g. 12345
        .. return:: The string representation of the given integer, e.g. '12345'
        """
        return str(integer)

    @sila.UnobservableCommand()
    @sila.Response(name="Joined Parameters")
    def join_integer_and_string(self, integer: int, string: str) -> str:
        """
        Concatenate an integer and a string parameter.

        .. parameter:: An integer, e.g. 123
        .. parameter:: A string, e.g. 'abc'
        .. return:: Both parameters joined as string (e.g. '123abc')
        """
        return f"{integer}{string}"

    @sila.UnobservableCommand()
    @sila.Response(name="First Character")
    @sila.Response(name="Remainder")
    def split_string_after_first_character(self, string: str) -> tuple[str, str]:
        """
        Split a given string after its first character.

        .. parameter:: A string, e.g. 'abcde'
        .. return:: The first character, e.g. 'a', or an empty string if the input was empty
        .. return:: The remainder, e.g. 'bcde', or an empty string if the input was shorter that two characters
        """
        return string[:1], string[1:]
