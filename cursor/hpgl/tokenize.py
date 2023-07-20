import re


def tokenize(hpgl: str) -> list[str]:
    """
    pass a full hpgl file in one line in here

    all of this is necessary because within a hpgl text command

    e.g. LB1234LB
    this should extract the label 1234LB

    """
    label_terminator = chr(3)

    commands = []

    split_by_label_terminator = [x for x in re.split(f"{label_terminator}", hpgl) if x]
    for command_batch in split_by_label_terminator:
        label_index = command_batch.find("LB")
        other_part = command_batch[:label_index]
        label_part = command_batch[label_index:]
        if label_index > 0:
            commands.extend([x for x in re.split(";", other_part) if x])
        else:
            commands.extend([x for x in re.split(";", command_batch) if x])

        if label_index != -1:
            commands.append(label_part)

    return commands
