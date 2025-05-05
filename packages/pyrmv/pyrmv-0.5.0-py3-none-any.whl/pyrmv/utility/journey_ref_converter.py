def ref_upgrade(ref: str) -> str:
    """This function converts older journey refs to the newer ones.

    ### WARNING
    This function will be deprecated as soon as RMV updates their API

    ### Args:
        * ref (`str`): Old ref like this one: `2|#VN#1#ST#1700765441#PI#0#ZI#160749#TA#0#DA#241123#1S#3004646#1T#2228#LS#3006907#LT#2354#PU#80#RT#1#CA#S30#ZE#S1#ZB#      S1#PC#3#FR#3004646#FT#2228#TO#3006907#TT#2354#`

    ### Raises:
        * `KeyError`: Some required keys are not found in the ref provided

    ### Returns:
        * `str`: Ref of the new type
    """

    items = "|".join(ref.split("|")[1:]).strip("#").split("#")
    result = {items[i]: items[i + 1] for i in range(0, len(items), 2)}

    for required in ["VN", "ZI", "TA", "PU"]:
        if required not in result:
            raise KeyError(
                f"Required key {required} in the old journey ref is not found during conversion to the newer journey ref"
            )

    return "|".join([result["VN"], result["ZI"], result["TA"], result["PU"]])
