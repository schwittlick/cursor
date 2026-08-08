from cursor.hpgl import LB_TERMINATOR

LABEL = "LB"


def tokenizer(hpgl: str) -> list[str]:
    """
    Split a full HPGL file into one command per entry.

    Labels are why this is not a plain split on ";": everything between LB and the label
    terminator is text, and prose is full of semicolons and can contain "LB" itself. So
    the terminator is cut first, and only the part of each batch ahead of its label is
    split into commands -- the label is handed back whole.
    """
    commands = []

    for batch in hpgl.split(LB_TERMINATOR):
        if not batch:
            continue

        label_index = batch.find(LABEL)
        if label_index < 0:
            commands.extend([command for command in batch.split(";") if command])
            continue

        commands.extend([command for command in batch[:label_index].split(";") if command])
        commands.append(batch[label_index:])

    return commands
