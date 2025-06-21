from src import masks

card_number = int(input())
account_number = int(input())

print(masks.get_mask_card_number(card_number))
print(masks.get_mask_account(account_number))
