import argparse


class ArgStoreWithFlag(argparse.Action):
    """
    Custom argparse action to store an argument value and set a flag indicating
    whether the argument was set by the user or is using the default value.

    Usage:
    ------
    parser.add_argument('--example', type=str, default='default_value',
                        action=arg_store_with_flag.ArgStoreWithFlag,
                        help="An example argument")

    After parsing:
    --------------
    - If '--example' is provided by the user, `args.example` will contain the
      provided value, and `args.example_set_flag` will be True.
    - If '--example' is not provided by the user and uses the default value,
      `args.example` will be 'default_value', and `args.example_set_flag` will be False.
    """
    # def __init__(self, option_strings, dest, **kwargs):
    #     dest_set = dest + '_set_flag'
    #     super(ArgStoreWithFlag, self).__init__(option_strings, dest, **kwargs)
    #     self.dest_set = dest_set
    #
    # def __call__(self, parser, namespace, values, option_string=None):
    #     setattr(namespace, self.dest, values)
    #     setattr(namespace, self.dest_set, True)


    def __call__(self, parser, namespace, values, option_string=None):
        """
        Store the argument value and set the flag in the namespace.

        Parameters:
        -----------
        parser : argparse.ArgumentParser
            The parser object invoking this action.
        namespace : argparse.Namespace
            The namespace object where the argument value and flag will be stored.
        values : Any
            The value to be assigned to the argument.
        option_string : str, optional
            The option string that was used to invoke this action.
        """
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest + '_set_flag', True)
