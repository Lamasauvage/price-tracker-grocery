from database import SessionLocal, create_database
from models import Product, Price, GroceryShopping
from datetime import datetime
from sqlalchemy.orm import Session
from termgraph import termgraph as tg

# Create the database
create_database()


# Main function
def main():
    session = SessionLocal()

    menu_options = {
        "1": add_product,
        "2": update_price,
        "3": view_all_products,
        "4": price_history,
        "5": delete_product,
        "6": add_grocery_total,
        "7": show_grocery_shopping,
        "8": delete_grocery_ticket,
        "9": display_total_spent,
        "10": show_total_spent_chart,
        "11": exit_program
    }

    while True:
        choice = show_menu()
        if choice in menu_options:
            menu_options[choice](session)
        else:
            print("Invalid choice")
            continue


# Display the menu and return the user's choice
def show_menu():
    print("Welcome to Price Tracker")
    print("1. Add a new product")
    print("2. Update the price for an existing product")
    print("3. View all products")
    print("4. View price history for a product")
    print("5. Delete a product")
    print("6. Add a grocery shopping ticket")
    print("7. Show grocery shopping tickets")
    print("8. Delete a grocery shopping ticket")
    print("9. Display the total amount spent on groceries")
    print("10. Show a chart of the total amount spent on groceries")
    print("11. Exit")
    choice = input("Enter your choice : ")
    return choice


# Input to return to the main menu
def return_to_menu(message, cancel_keyword="return", optional=False, validate=None):
    while True:
        user_input = input(message + f" (or type '{cancel_keyword}' to go back to the main menu) : ")
        if user_input.lower() == cancel_keyword.lower():
            return None
        if optional and not user_input:
            return user_input
        if not optional and not user_input:
            print("Input cannot be empty, please try again.")
            continue
        if validate and not validate(user_input):
            print("Invalid input, please try again.")
            continue
        return user_input


# Add a new product (1)
def add_product(session):
    name = return_to_menu("Enter the name of the product", optional=False)
    if name is None:
        print("Adding product cancelled, returning to the main menu")
        return

    # Check if the product already exists
    existing_product = session.query(Product).filter(Product.name == name).first()
    if existing_product:
        print("Product already exists")
        return

    description = return_to_menu("Enter the description of the product (optional)", optional=True)
    if description is None:
        print("Adding product cancelled, returning to the main menu")
        return

    # Create a new product and add it to the database
    new_product = Product(name=name, description=description if description else None)
    session.add(new_product)
    session.commit()
    print("Product added successfully")

    # Define an initial price for the product
    initial_price = return_to_menu("Enter the price (€) :")
    if initial_price is None:
        print("Adding product cancelled, returning to the main menu")
        return
    try:
        initial_price = float(initial_price)
    except ValueError:
        print("Invalid price, enter a valid number.")
        return

    store_name = return_to_menu("Enter the store name :")
    if store_name is None:
        print("Adding product cancelled, returning to the main menu")
        return

    # Ask for the date
    price_date = None
    while True:
        date_input = return_to_menu("Enter the date (DD/MM/YYYY) :")
        if date_input is None:
            print("Adding product cancelled, returning to the main menu")
            return
        try:
            price_date = datetime.strptime(date_input, "%d/%m/%Y").date()
            break
        except ValueError:
            print("Invalid date format. Please enter a date in the format DD/MM/YYYY.")

    # Create a new price object and add it to the database
    new_price = Price(product_id=new_product.id, price=initial_price, store=store_name, date=price_date)
    session.add(new_price)
    session.commit()
    print("Price added successfully")


# Update the price for an existing product (2)
def update_price(session):
    name = return_to_menu("Enter the name of the product : ", optional=False)

    # Find product matching the name
    products = session.query(Product).filter(Product.name.like(f"%{name}%")).all()

    if not products:
        print("Product not found")
        return

    # Display matching products
    for i, product in enumerate(products, start=1):
        # Get the last price for the product
        price = session.query(Price).filter(Price.product_id == product.id).order_by(Price.date.desc()).first()
        if price:
            print(f"{i}. {product.name} - {product.description} - Last Price : {price.price}€ - Store : {price.store}")
        else:
            print(f"{i}. {product.name} - {product.description} - No price available")

    while True:
        product_choice = input("Enter the number of the product you want to update the price : ")
        try:
            product_choice = int(product_choice)
            if 1 <= product_choice <= len(products):
                selected_product = products[product_choice - 1]
                break
            else:
                print("Invalid choice, please enter a number from the list.")
        except ValueError:
            print("Invalid choice, please enter a number from the list.")

    # Update the price
    new_price_value = return_to_menu("Enter the new price (€) : ", validate=lambda x: x.replace(".", "", 1).isdigit())
    if new_price_value is None:
        print("Price update cancelled, returning to the main menu")
        return
    new_price_value = float(new_price_value)

    # Ask for the store name
    store_name = return_to_menu("Enter the store name : ", optional=False)
    if store_name is None:
        print("Price update cancelled, returning to the main menu")
        return

    # Ask for the date
    price_date = None
    while True:
        date_input = return_to_menu("Enter the date (DD/MM/YYYY): ", )
        if date_input is None:
            print("Price update cancelled, returning to the main menu")
            return
        try:
            price_date = datetime.strptime(date_input, "%d/%m/%Y").date()
            break
        except ValueError:
            print("Invalid date format. Please enter a date in the format DD/MM/YYYY.")

    # Create a new price object and add it to the database
    new_price = Price(product_id=selected_product.id, price=new_price_value, store=store_name, date=price_date)
    session.add(new_price)
    session.commit()
    print("Price updated successfully")


# View all products (3)
def view_all_products(session):
    products = session.query(Product).all()
    for product in products:
        print(f"--- {product.id}. {product.name} - {product.description} ---")
        last_price = session.query(Price).filter(Price.product_id == product.id).order_by(Price.date.desc()).first()
        if last_price:
            print(
                f"    Price : {last_price.price}€ - Store : {last_price.store} - Date : {last_price.date.strftime('%d/%m/%Y')}")
        else:
            print(f"{product.name} - {product.description}")

    if not products:
        print("No products available")


# View price history for a product (4)
def price_history(session):
    name = return_to_menu("Enter the name of the product : ")
    if name is None:
        print("Operation cancelled, returning to the main menu")
        return

    # Find the product
    product = session.query(Product).filter(Product.name.like(f"%{name}%")).first()
    if not product:
        print("Product not found")
        return

    # Display the price history for the product
    prices = session.query(Price).filter(Price.product_id == product.id).order_by(Price.date.asc()).all()
    if prices:
        for price in prices:
            print(
                f"Product : {product.name} - Price : {price.price}€ - Date : {price.date.strftime('%d/%m/%Y')} at {price.store}")
    else:
        print("No prices available")
    print("")


# Delete a product (5)
def delete_product(session):
    name = return_to_menu("Enter the name of the product you want to delete : ")
    if name is None:
        print("Operation cancelled, returning to the main menu")
        return

    products = session.query(Product).filter(Product.name.like(f"%{name}%")).all()
    if not products:
        print("Product not found")
        return

    # Display a numbered list of matching products
    print("Matching products :")
    for i, product in enumerate(products, start=1):
        print(f"{i}. {product.name} - {product.description} - ID : {product.id}")

    # Ask the user to choose a product to delete
    choice_text = return_to_menu("Enter the ID of the product you want to delete : ")
    if choice_text is None:
        print("Operation cancelled, returning to the main menu")
        return

    try:
        # Convert the user input to an integer
        choice_id = int(choice_text)
    except ValueError:
        print("Invalid choice")
        return

    # Validate the chosen ID against available product IDs
    if choice_id not in [product.id for product in products]:
        print("Invalid product ID, please select from the list.")
        return

    # Get the product object to delete
    product_to_delete = session.query(Product).filter_by(id=choice_id).first()

    # Confirm the deletion
    confirm = input(f"Are you sure you want to delete {product_to_delete.name} (Y/n) ? ")
    if confirm == "Y":
        # Delete the product
        session.delete(product_to_delete)
        session.commit()
        print(f"{product_to_delete.name} has been deleted.")
    else:
        print("Operation cancelled, returning to the main menu")


# Add a grocery shopping ticket (6)
def add_grocery_total(session):
    while True:
        total_price = return_to_menu("Enter the total cost of the recipe : ")
        if total_price is None:
            print("Adding grocery ticket cancelled, returning to the main menu")
            return
        try:
            total_price = float(total_price)
            break
        except ValueError:
            print("Invalid input, enter a valid number.")
            continue

    while True:
        shopping_date = return_to_menu("Enter the date of the shopping (DD/MM/YYYY) : ")

        if shopping_date is None:
            print("Shopping ticket cancel, returning to the main menu")
            return
        try:
            date_object = datetime.strptime(shopping_date, "%d/%m/%Y").date()
            break
        except ValueError:
            print("Invalid date format. Please enter a date in the format DD/MM/YYYY.")

    store_name = return_to_menu("Enter the store name : ")
    if store_name is None:
        print("Adding grocery ticket cancelled, returning to the main menu")
        return

    new_shopping = GroceryShopping(total_price=total_price, date=date_object, store=store_name)
    session.add(new_shopping)
    session.commit()
    print("Shopping added successfully")


# Show grocery shopping tickets (7)
def show_grocery_shopping(session):
    shopping = session.query(GroceryShopping).all()
    for shop in shopping:
        print(f"--- ID : {shop.id}. Total price : {shop.total_price}€ - Date : {shop.date.strftime('%d/%m/%Y')} at {shop.store} ---")
    if not shopping:
        print("No shopping tickets available")


# Delete a grocery shopping ticket (8)
def delete_grocery_ticket(session):
    shopping = session.query(GroceryShopping).all()
    for shop in shopping:
        print(f"--- ID : {shop.id}. Total price : {shop.total_price}€ - Date : {shop.date.strftime('%d/%m/%Y')} ---")
    if not shopping:
        print("No shopping ticket registered")
        return

    while True:
        choice = return_to_menu("Enter the ID of the grocery ticket you want to delete : ")
        if choice is None:
            print("Operation cancelled, returning to the main menu")
            return
        try:
            shopping_to_delete = session.query(GroceryShopping).filter_by(id=int(choice)).first()
            break
        except ValueError:
            print("Invalid ID. Please enter a valid numeric ID.")

    if shopping_to_delete:
        confirm = return_to_menu(f"Are you sure you want to delete ? (y/n) ? ")
        if confirm is None:
            print("Operation cancelled, returning to the main menu")
            return
        elif confirm.lower() == "y":
            session.delete(shopping_to_delete)
            session.commit()
            print("Grocery ticket deleted successfully")
        else:
            print("Operation cancelled")
    else:
        print("Ticket with the provided ID not found.")


# Display the total amount spent on groceries (9)
def display_total_spent(session):
    total_spent = 0
    shopping = session.query(GroceryShopping).all()
    for shop in shopping:
        total_spent += shop.total_price
    print(f"Total spent on groceries : {total_spent}€")


# Display a chart of the total amount spent on groceries (9)
def show_total_spent_chart(session: Session):
    shopping = session.query(GroceryShopping).order_by(GroceryShopping.date.asc()).all()

    if not shopping:
        print("No grocery data available")
        return

    # Extract the dates and total prices
    dates = [entry.date.strftime('%Y-%m-%d') for entry in shopping]
    prices = [entry.total_price for entry in shopping]

    data = [[price] for price in prices]

    args = {
        'title': 'Total spent on groceries',
        'width': 50,
        'no_labels': False,
        'format': '{:<5.2f}',
        'suffix': '€',
        'stacked': False,
        'vertical': False,
        'histogram': False,
        'different_scale': False,
        'calendar': False,
        'start_dt': None,
        'no_values': False,
        'reverse': False,
    }

    # Display the chart
    print("Total spent on groceries")
    tg.chart(data=data, labels=dates, args=args, colors='None')


# Exit the program (10)
def exit_program(session):
    session.close()
    print("Goodbye !")
    exit()


if __name__ == "__main__":
    main()