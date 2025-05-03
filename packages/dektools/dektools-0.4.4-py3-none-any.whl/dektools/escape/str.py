import re
import codecs


def str_escape_wrap(s, escape='\\'):
    count = 0
    for x in reversed(s):
        if x != escape:
            break
        count += 1
    if count:
        wrap = not count % 2
        return s[:-((count + 1) // 2)], wrap
    return s, True


def str_escape_one_type(s, prefix, suffix, escape='\\'):
    return re.sub(
        f'{re.escape(prefix)}(({re.escape(escape)})+){re.escape(suffix)}',
        lambda x: prefix + len(x.group(1)) // len(escape) // 2 * escape + suffix, s
    )


def str_escaped(s):
    return codecs.getdecoder("unicode_escape")(s.encode('utf-8'))[0]


def str_split(s, sep):
    for x in s.split(sep):
        x = x.strip()
        if x:
            yield x


def str_custom_escaped_split(s, delim, escaped='\\'):
    ret = []
    current = []
    itr = iter(s)
    for ch in itr:
        if ch == escaped:
            try:
                # skip the next character; it has been escaped!
                current.append(escaped)
                current.append(next(itr))
            except StopIteration:
                pass
        elif ch == delim:
            # split! (add current to the list and reset it)
            ret.append(''.join(current))
            current = []
        else:
            current.append(ch)
    ret.append(''.join(current))
    return ret


def str_custom_escaped(s, mapping=None, escaped='\\'):
    mapping = {} if mapping is None else mapping
    r = ""
    cursor = 0
    length = len(s)
    while cursor < length:
        c = s[cursor]
        if c == escaped:
            cursor += 1
            c = s[cursor]
            r += mapping.get(c, c)
        else:
            r += c
        cursor += 1
    return r


def str_special_escape(s, escape='\\'):
    r = ""
    escaping = False
    for x in s:
        if not escaping and x == escape:
            escaping = True
        else:
            r += x
            escaping = False
    return r
