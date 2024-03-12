with open(file='invites.txt',
          mode='r',
          encoding='utf-8-sig') as file:
    ref_codes: list[str] = [row.strip() for row in file]