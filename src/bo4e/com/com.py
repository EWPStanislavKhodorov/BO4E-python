import attr


@attr.s(auto_attribs=True, kw_only=True, frozen=True)
class COM:
    """
    abstract base class for all components
    """
