from src import widget

account_or_card_number = input()
date = input()

print(widget.mask_account_card(account_or_card_number))
print(widget.get_date(date))
