# -*- coding: utf-8 -*-

import re
import time

Digits = '01234567890'

BlockFlags = {
    'numeric':            1 << 0,
    'varcapacity':        1 << 1,
    'multihost':          1 << 2,
    'masteronslave':      1 << 3,
    'dependsubtask':      1 << 4,
    'skipthumbnails':     1 << 5,
    'skipexistingfiles':  1 << 6,
    'checkrenderedfiles': 1 << 7,
    'slavelostignore':    1 << 8,
    'appendedtasks':      1 << 9,
    'suspendnewtasks':    1 << 10
}

JobFlags = {
	# First 32 flags are reserved for af::Node (zombie, hidden, ...)
    'ppapproval':     1 << 32,
    'maintenance':    1 << 33,
    'ignorenimby':    1 << 34,
    'ignorepaused':   1 << 35,
    'appendedblocks': 1 << 36
}


def checkBlockFlag(i_flags, i_name):
    if i_name not in BlockFlags:
        print('AFERROR: block flag "%s" does not exist.' % i_name)
        print('Existing flags are: ' + str(BlockFlags))
        return False
    return i_flags & BlockFlags[i_name]


def setBlockFlag(i_flags, i_name):
    if i_name not in BlockFlags:
        print('AFERROR: block flag "%s" does not exist.' % i_name)
        print('Existing flags are: ' + str(BlockFlags))
        return i_flags
    elif i_name == 'appendedtasks':
        print('AFERROR: block flag "%s" is read-only.' % i_name)
        return i_flags
    return i_flags | BlockFlags[i_name]

def checkJobFlag(i_flags, i_name):
    if i_name not in JobFlags:
        print('AFERROR: block flag "%s" does not exist.' % i_name)
        print('Existing flags are: ' + str(BlockFlags))
        return False
    return i_flags & BlockFlags[i_name]

def setJobFlag(i_flags, i_name):
    if i_name not in JobFlags:
        print('AFERROR: job flag "%s" does not exist.' % i_name)
        print('Existing flags are: ' + str(JobFlags))
        return i_flags
    elif i_name == 'appendedblocks':
        print('AFERROR: job flag "%s" is read-only.' % i_name)
        return i_flags
    return i_flags | BlockFlags[i_name]


def fillNumbers(i_pattern, i_start, i_end):
    """Fill numeric block command pattern with start and end frame numbers
    """
    cmd = ''
    frame = i_start
    for split in re.split('(@#{1,}@)', i_pattern):
        if re.match('@#{1,}@', split) is None:
            cmd += split
            continue
        pad = len(split) - 2
        pad = '%0' + str(pad) + 'd'
        pad = pad % frame
        cmd += pad
        if frame == i_start:
            frame = i_end
        else:
            frame = i_start

    return cmd


def filterFileName(filename):
    """Replace "bad" characters in filename on "_":

    :param str filename:
    """
    chars = ' ~`!@#$%^&*()+[]{};:\'",<>/?\\|'
    newfilename = filename
    for c in chars:
        newfilename = newfilename.replace(c, '_')
    return newfilename


def splitPathsDifference(path_a, path_b):
    """Split paths searching for difference, return equal part before
    difference, difference length, part after difference

    :param str path_a:
    :param str path_b:
    """
    part_1 = path_a
    part_2 = ''
    diflength = 0

    len_a = len(path_a)
    len_b = len(path_b)
    len_min = len_a
    if len_min > len_b:
        len_min = len_b

    if len_min < 1:
        return part_1, diflength, part_2

    len_begin = -1
    for c in range(len_min):
        if path_a[c] == path_b[c]:
            continue
        len_begin = c
        break

    if len_begin < 1:
        return part_1, diflength, part_2

    len_end = -1
    for c in range(len_min):
        if path_a[len_a - c - 1] == path_b[len_b - c - 1]:
            continue
        len_end = c
        break

    if len_end < 1:
        return part_1, diflength, part_2

    for c in range(len_begin):
        if path_a[len_begin - c] in Digits:
            continue
        len_begin = len_begin - c + 1
        break

    for c in range(len_end):
        if path_a[len_a - len_end + c] in Digits:
            continue
        len_end -= c
        break

    diflength = 1
    if len_a == len_b:
        diflength = len_a - len_begin - len_end

    part_1 = path_a[0:len_begin]
    part_2 = path_a[len_a - len_end:len_a]

    return part_1, diflength, part_2


def patternFromPaths(path_a, path_b):
    """Return Afanasy pattern based on paths difference (the best way):

    :param str path_a:
    :param str path_b:
    """
    path = path_a

    part_1, padding, part_2 = splitPathsDifference(path_a, path_b)

    if padding < 1:
        return path

    path = part_1 + '@' + '#' * padding + '@' + part_2

    return path


def patternFromStdC(path, verbose=False):
    """Return Afanasy pattern from C printf formatting (%04d):

    :param str path:
    :param bool verbose:
    """
    pos = 0
    while pos < len(path):
        posp = path[pos:].find('%')
        if posp == -1:
            return path

        posd = path[pos + posp:].find('d')
        if posd == -1:
            return path

        pattern = None
        if posd == 1:
            pattern = '@#@'
        else:
            digits = path[pos + posp + 1:pos + posp + posd]
            if verbose:
                print('digits = "%s"' % digits)

            digits_ok = True

            for d in digits:
                if d not in Digits:
                    digits_ok = False
                    break

            if digits_ok:
                number = int(digits)
                pattern = '@' + '#' * number + '@'
                if verbose:
                    print('number = %d' % number)

        if pattern is not None:
            if verbose:
                print('pattern = "%s"' % pattern)
            path = path[:pos + posp] + pattern + path[pos + posp + posd + 1:]
            pos = pos + posp + len(pattern)
        else:
            if verbose:
                print('No pattern.')
            pos += posp + posd
    return path


def patternFromDigits(path, verbose=False):
    """Return Afanasy pattern searching fo "#" characters:

    :param str path:
    :param bool verbose:
    """
    pos = 0
    posd = 0
    while pos < len(path):
        posd = path[pos:].find('#')
        if posd == -1:
            break
        # Check if it is an already formatted pattern:
        if pos + posd > 0 and path[pos + posd - 1] == '@':
            cab = path[pos + posd:].find('@')
            if cab != -1:
                # Shift and continue:
                pos = pos + posd + cab
                continue
        posd += pos
        pos = posd
        # Shift to the last #:
        for d in path[posd:]:
            if d != '#':
                break
            pos += 1
        if verbose:
            print('path[%d:%d] = "%s"' % (posd, pos, path[posd:pos]))
        path = path[:posd] + '@' + path[posd:pos] + '@' + path[pos:]
        pos += 2
    return path


def patternFromFile(path):
    """Return Afanasy pattern searching for digits before last "."

    :param str path:
    """
    pos = path.rfind('.')
    if pos < 1:
        return path
    pos_ext = pos
    pos -= 1
    while pos >= 0:
        if not path[pos] in Digits:
            break
        pos -= 1
    pos += 1
    if pos == pos_ext:
        return path

    return path[:pos] + '@' + '#' * (pos_ext - pos) + '@' + path[pos_ext:]


def timeWaitFromHM(i_hours, i_minutes):
    hours = max(0,min(i_hours,23))
    minutes = max(0,min(i_minutes,59))
    now_sec = int(time.time())
    now_day = int((now_sec - time.timezone) / (24*3600)) * (24*3600) + time.timezone
    sec = now_sec % 60
    wait_sec = now_day + (hours * 3600) + (minutes * 60) + sec
    if wait_sec <= now_sec:
        wait_sec += (24*3600)

    return wait_sec
