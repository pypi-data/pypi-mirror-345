import os
import stat

def set_mode(filename, mode_str):
    mode = 0

    for i, permissions in enumerate(reversed(mode_str.split(','))):
        if 'u' in permissions:
            if '+' in permissions:
                if 'r' in permissions:
                    mode |= stat.S_IRUSR
                if 'w' in permissions:
                    mode |= stat.S_IWUSR
                if 'x' in permissions:
                    mode |= stat.S_IXUSR
            elif '-' in permissions:
                if 'r' in permissions:
                    mode &= ~stat.S_IRUSR
                if 'w' in permissions:
                    mode &= ~stat.S_IWUSR
                if 'x' in permissions:
                    mode &= ~stat.S_IXUSR
        elif 'g' in permissions:
            if '+' in permissions:
                if 'r' in permissions:
                    mode |= stat.S_IRGRP
                if 'w' in permissions:
                    mode |= stat.S_IWGRP
                if 'x' in permissions:
                    mode |= stat.S_IXGRP
            elif '-' in permissions:
                if 'r' in permissions:
                    mode &= ~stat.S_IRGRP
                if 'w' in permissions:
                    mode &= ~stat.S_IWGRP
                if 'x' in permissions:
                    mode &= ~stat.S_IXGRP
        elif 'o' in permissions:
            if '+' in permissions:
                if 'r' in permissions:
                    mode |= stat.S_IROTH
                if 'w' in permissions:
                    mode |= stat.S_IWOTH
                if 'x' in permissions:
                    mode |= stat.S_IXOTH
            elif '-' in permissions:
                if 'r' in permissions:
                    mode &= ~stat.S_IROTH
                if 'w' in permissions:
                    mode &= ~stat.S_IWOTH
                if 'x' in permissions:
                    mode &= ~stat.S_IXOTH

    os.chmod(filename, mode)