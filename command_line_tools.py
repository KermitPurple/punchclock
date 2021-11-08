def get_yes_no(prompt: str) -> bool:
    '''
    ask a yes or no question and prompt response
    :returns: true if yes false if no
    '''
    if prompt != '':
        print(prompt)
    while 1:
        response = input().lower().strip()
        if response == 'yes' or response == 'y':
            return True
        elif response == 'no' or response == 'n':
            return False
