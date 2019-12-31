import pandas as pd

data = [('Apple', 'Coles', 1.50),
        ('Apple', 'Woolworths', 1.60),
        ('Apple', 'IGA', 1.70),
        ('Banana', 'Coles', 0.50),
        ('Banana', 'Woolworths', 0.60),
        ('Banana', 'IGA', 0.70),
        ('Cherry', 'Coles', 5.00),
        ('Date', 'Coles', 2.00),
        ('Date', 'Woolworths', 2.10),
        ('Elderberry', 'IGA', 10.00)]
df = pd.DataFrame(data, columns=['Fruit', 'Shop', 'Price'])
table1 = df.pivot_table(columns='Shop', index='Fruit', values='Price', aggfunc='sum', fill_value=0)
print(table1)

table1 = df.pivot_table(columns='Shop', index='Fruit', values='Price', aggfunc='count', fill_value=0)
print(table1)
