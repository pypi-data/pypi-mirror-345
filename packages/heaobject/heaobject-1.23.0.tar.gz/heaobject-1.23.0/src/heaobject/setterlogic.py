from collections.abc import Iterable, MutableSequence


def id_set_setter(attr: set[str], ids: Iterable[str] | None):
    """
    Setter logic for a list of ids. Duplicates and None ids are ignored.

    :param attr: the attribute to set (a set of ids).
    :param ids: the input ids (each can be None or a string).
    """
    if ids is None:
        attr.clear()
    elif not isinstance(ids, str):
        id_strs = [str(id_) for id_ in ids if id_ is not None]
        if any(group_id == '' for group_id in id_strs):
            raise ValueError('No ids can be the empty string')
        attr.clear()
        attr.update(id_ for id_ in id_strs)
    else:
        id_str = str(ids)
        if id_str == '':
            raise ValueError('No id can be the empty string')
        attr.clear()
        attr.add(id_str)


def id_set_adder(attr: set[str], id_: str):
    """
    Adder logic for a set of ids. Duplicates and None ids are ignored.

    :param attr: the attribute to set (a set of ids).
    :param id_: the input id (a non-empty string).
    """
    if id_ is None:
        return
    id_str = str(id_)
    if id_str == '':
        raise ValueError('No id can be the empty string')
    attr.add(id_str)


def id_set_remover(attr: set[str], id_: str):
    """
    Remover logic for a set of ids.

    :param attr: the attribute to set (a set of ids).
    :param id_: the input id (a non-empty string).
    :raise ValueError: if the id is not found in the set.
    """
    try:
        attr.remove(str(id_))
    except KeyError as e:
        raise ValueError(f'id {id_} not found') from e


def id_sequence_setter(attr: MutableSequence[str], ids: Iterable[str] | None):
    """
    Setter logic for a sequence of ids. None ids are ignored.

    :param attr: the attribute to set (a list of ids).
    :param ids: the input ids (each can be None or a string).
    """
    if ids is None:
        attr.clear()
    elif not isinstance(ids, str):
        id_strs = [str(id_) for id_ in ids if id_ is not None]
        if any(group_id == '' for group_id in id_strs):
            raise ValueError('No ids can be the empty string')
        attr.clear()
        attr.extend(id_ for id_ in id_strs)
    else:
        id_str = str(ids)
        if id_str == '':
            raise ValueError('No id can be the empty string')
        attr.clear()
        attr.append(id_str)


def id_sequence_adder(attr: MutableSequence[str], id_: str):
    """
    Adder logic for a sequence of ids. None ids are ignored.

    :param attr: the attribute to add to (a sequence of ids).
    :param id_: the input id (a non-empty string).
    """
    if id_ is None:
        return
    id_str = str(id_)
    if id_str == '':
        raise ValueError('No id can be the empty string')
    attr.append(id_str)


def id_sequence_remover(attr: MutableSequence[str], id_: str):
    """
    Remover logic for a sequence of ids.

    :param attr: the attribute to set (a set of ids).
    :param id_: the input id (a non-empty string).
    :raise ValueError: if the id is not found in the sequence.
    """
    try:
        attr.remove(str(id_))
    except KeyError as e:
        raise ValueError(f'id {id_} not found') from e
