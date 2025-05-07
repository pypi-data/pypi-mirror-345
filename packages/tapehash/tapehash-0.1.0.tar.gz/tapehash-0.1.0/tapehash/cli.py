from sys import argv, stdin, stdout
from .algos import tapehash1, tapehash2, tapehash3
from .work import work, check_difficulty, calculate_difficulty


def help_tapehash1():
    print('Use: command | tapehash1 OR tapehash1 --preimage {str} OR tapehash1 --file path/to/file')
    print('\t--from:hex - parse preimage as hexadecimal')
    print('\t--code_size {int} - set the code_size parameter (default=1024)')
    print('\t-cs {int} - set the code_size parameter (default=1024)')
    print('\t--to:raw - write the raw hash digest bytes to stdout')
    print('\t--difficulty - output the difficulty of the hash digest')
    print('\t--check {int} - outputs 1 if the hash digest meets the ' +
        'difficulty threshold; outputs 0 and exits with error code 2 '+
        'if it does not'
    )
    print('\nOnly 1 of --to:raw --difficulty --check can be used at a time')

def run_tapehash1() -> None:
    preimage = b''
    code_size = 20

    if not stdin.isatty():
        preimage = stdin.buffer.read()

    if len(argv) > 1:
        if '--help' in argv or '-h' in argv:
            return help_tapehash1()

        if '--preimage' in argv:
            idx = argv.index('--preimage')
            if len(argv) < idx + 2:
                print("must supply data after --preimage")
                exit(1)
            preimage = argv[idx+1].encode('utf-8')

        if '--file' in argv:
            idx = argv.index('--file')
            if len(argv) < idx + 2:
                print("must supply path after --file")
                exit(1)
            with open(argv[idx+1], 'rb') as f:
                preimage = f.read()

        if '--from:hex' in argv:
            preimage = bytes.fromhex(preimage.decode('utf-8'))

        if '--code_size' in argv:
            idx = argv.index('--code_size')
            if len(argv) < idx + 2:
                print("must supply integer after --code_size")
                exit(1)
            code_size = int(argv[idx+1])

        if '-cs' in argv:
            idx = argv.index('-cs')
            if len(argv) < idx + 2:
                print("must supply integer after -cs")
                exit(1)
            code_size = int(argv[idx+1])

        if '--to:raw' in argv:
            stdout.buffer.write(tapehash1(preimage, code_size))
            return

        if '--difficulty' in argv:
            diff = calculate_difficulty(tapehash1(preimage, code_size))
            print(diff)
            return

        if '--check' in argv:
            idx = argv.index('--check')
            if len(argv) < idx + 2:
                print("must supply integer after --check")
                exit(1)
            target = int(argv[idx+1])
            digest = tapehash1(preimage, code_size)
            if check_difficulty(digest, target):
                print(1)
                return
            else:
                print(0)
                exit(2)

    print(tapehash1(preimage, code_size).hex())

def help_tapehash2():
    print('Use: command | tapehash1 OR tapehash1 --preimage {str} OR tapehash2 --file path/to/file')
    print('\t--from:hex - parse preimage as hexadecimal')
    print('\t--tape_size_multiplier {int} - set the tape_size_multiplier' +
        ' parameter (default=1024)'
    )
    print('\t-tsm {int} - set the tape_size_multiplier parameter (default=1024)')
    print('\t--to:raw - write the raw hash digest bytes to stdout')
    print('\t--difficulty - output the difficulty of the hash digest')
    print('\t--check {int} - outputs 1 if the hash digest meets the ' +
        'difficulty threshold; outputs 0 and exits with error code 2 '+
        'if it does not'
    )
    print('\nOnly 1 of --to:raw --difficulty --check can be used at a time')

def run_tapehash2() -> None:
    preimage = b''
    tape_size_multiplier = 2

    if not stdin.isatty():
        preimage = stdin.buffer.read()

    if len(argv) > 1:
        if '--help' in argv or '-h' in argv:
            return help_tapehash2()

        if '--preimage' in argv:
            idx = argv.index('--preimage')
            if len(argv) < idx + 2:
                print("must supply data after --preimage")
                exit(1)
            preimage = argv[idx+1].encode('utf-8')

        if '--file' in argv:
            idx = argv.index('--file')
            if len(argv) < idx + 2:
                print("must supply path after --file")
                exit(1)
            with open(argv[idx+1], 'rb') as f:
                preimage = f.read()

        if '--from:hex' in argv:
            preimage = bytes.fromhex(preimage.decode('utf-8'))

        if '--tape_size_multiplier' in argv:
            idx = argv.index('--tape_size_multiplier')
            if len(argv) < idx + 2:
                print("must supply integer after --tape_size_multiplier")
                exit(1)
            tape_size_multiplier = int(argv[idx+1])

        if '-tsm' in argv:
            idx = argv.index('-tsm')
            if len(argv) < idx + 2:
                print("must supply integer after -tsm")
                exit(1)
            tape_size_multiplier = int(argv[idx+1])

        if '--to:raw' in argv:
            stdout.buffer.write(tapehash2(preimage, tape_size_multiplier))
            return

        if '--difficulty' in argv:
            diff = calculate_difficulty(tapehash2(preimage, tape_size_multiplier))
            print(diff)
            return

        if '--check' in argv:
            idx = argv.index('--check')
            if len(argv) < idx + 2:
                print("must supply integer after --check")
                exit(1)
            target = int(argv[idx+1])
            digest = tapehash2(preimage, tape_size_multiplier)
            if check_difficulty(digest, target):
                print(1)
                return
            else:
                print(0)
                exit(2)

    print(tapehash2(preimage, tape_size_multiplier).hex())

def help_tapehash3():
    print('Use: command | tapehash1 OR tapehash1 --preimage {str} OR tapehash3 --file path/to/file')
    print('\t--from:hex - parse preimage as hexadecimal')
    print('\t--code_size {int} - set the code_size parameter (default=1024)')
    print('\t-cs {int} - set the code_size parameter (default=1024)')
    print('\t--tape_size_multiplier {int} - set the tape_size_multiplier' +
        ' parameter (default=1024)'
    )
    print('\t-tsm {int} - set the tape_size_multiplier parameter (default=1024)')
    print('\t--to:raw - write the raw hash digest bytes to stdout')
    print('\t--difficulty - output the difficulty of the hash digest')
    print('\t--check {int} - outputs 1 if the hash digest meets the ' +
        'difficulty threshold; outputs 0 and exits with error code 2 '+
        'if it does not'
    )
    print('\nOnly 1 of --to:raw --difficulty --check can be used at a time')


def run_tapehash3() -> None:
    preimage = b''
    code_size = 64
    tape_size_multiplier = 2

    if not stdin.isatty():
        preimage = stdin.buffer.read()

    if len(argv) > 1:
        if '--help' in argv or '-h' in argv:
            return help_tapehash2()

        if '--preimage' in argv:
            idx = argv.index('--preimage')
            if len(argv) < idx + 2:
                print("must supply data after --preimage")
                exit(1)
            preimage = argv[idx+1].encode('utf-8')

        if '--file' in argv:
            idx = argv.index('--file')
            if len(argv) < idx + 2:
                print("must supply path after --file")
                exit(1)
            with open(argv[idx+1], 'rb') as f:
                preimage = f.read()

        if '--from:hex' in argv:
            preimage = bytes.fromhex(preimage.decode('utf-8'))

        if '--code_size' in argv:
            idx = argv.index('--code_size')
            if len(argv) < idx + 2:
                print("must supply integer after --code_size")
                exit(1)
            code_size = int(argv[idx+1])

        if '-cs' in argv:
            idx = argv.index('-cs')
            if len(argv) < idx + 2:
                print("must supply integer after -cs")
                exit(1)
            code_size = int(argv[idx+1])

        if '--tape_size_multiplier' in argv:
            idx = argv.index('--tape_size_multiplier')
            if len(argv) < idx + 2:
                print("must supply integer after --tape_size_multiplier")
                exit(1)
            tape_size_multiplier = int(argv[idx+1])

        if '-tsm' in argv:
            idx = argv.index('-tsm')
            if len(argv) < idx + 2:
                print("must supply integer after -tsm")
                exit(1)
            tape_size_multiplier = int(argv[idx+1])

        if '--to:raw' in argv:
            stdout.buffer.write(tapehash3(preimage, code_size, tape_size_multiplier))
            return

        if '--difficulty' in argv:
            diff = calculate_difficulty(tapehash3(preimage, code_size, tape_size_multiplier))
            print(diff)
            return

        if '--check' in argv:
            idx = argv.index('--check')
            if len(argv) < idx + 2:
                print("must supply integer after --check")
                exit(1)
            target = int(argv[idx+1])
            digest = tapehash1(preimage, code_size, tape_size_multiplier)
            if check_difficulty(digest, target):
                print(1)
                return
            else:
                print(0)
                exit(2)

    print(tapehash3(preimage, code_size, tape_size_multiplier).hex())

