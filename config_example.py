from typing import Union, List

session_path = './session.pickle'
username, password = 'your username', 'your password'
debug = False
enable_comments = False

interests: List[Union[str, int]] = list()
interests.extend('nature italy landscape nofilter traveler'.split())
interests.extend([
    113396132004585,  # IT
    112483542097587,  # UK
    113019615379046,  # ES
    108100019211318,  # DE
])
