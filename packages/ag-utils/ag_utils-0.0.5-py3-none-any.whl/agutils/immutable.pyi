

class Immutable:
    """Used to block changing the value of fields after initialization. Also prevents inheritance and instantiation.

        ```python
            class Config(Immutable):
                param = value
        ```
        The following examples will cause an error
        ```python

            ### ValueError
            Config.param = new_value

            ### TypeError
            Config()
            ChildConfig(Config):...
        ```
    """
