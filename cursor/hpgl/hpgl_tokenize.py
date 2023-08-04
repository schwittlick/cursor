def tokenizer(hpgl: str) -> list[str]:
    """
    pass a full hpgl file in one line in here

    all of this is necessary because within a hpgl text command

    e.g. LB1234LB
    this should extract the label 1234LB

    """
    label_terminator = chr(3)

    commands = []

    split_by_label_terminator = [x for x in hpgl.split(label_terminator) if x]
    for command_batch in split_by_label_terminator:
        label_index = command_batch.find("LB")
        other_part = command_batch[:label_index]
        label_part = command_batch[label_index:]
        if label_index > 0:
            commands.extend([x for x in other_part.split(";") if x])
            commands.append(label_part)
        else:
            commands.extend([x for x in command_batch.split(";") if x])

    return commands


if __name__ == '__main__':
    print("LOL")