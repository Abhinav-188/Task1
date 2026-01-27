"""
Electricity Bill System
A modular program to generate electricity bills with proper validation and computation
"""

from datetime import datetime, timedelta
import re

# Global storage for consumer records
consumers_db = {}


def validate_name(name):
    """
    Validate that name contains only alphabets and spaces
    Returns: (is_valid, error_message)
    """
    if not name or name.strip() == "":
        return False, "Name cannot be empty"
    
    # Check if name contains only alphabets and spaces
    if not re.match(r'^[A-Za-z\s]+$', name):
        return False, "Name must contain only alphabets (no numbers or special characters)"
    
    return True, ""


def validate_phone(phone):
    """
    Validate that phone number is exactly 10 digits
    Returns: (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number cannot be empty"
    
    # Remove any spaces
    phone = phone.strip()
    
    # Check if it contains only digits and is exactly 10 characters
    if not phone.isdigit():
        return False, "Phone number must contain only digits"
    
    if len(phone) != 10:
        return False, f"Phone number must be exactly 10 digits (current length: {len(phone)})"
    
    return True, ""


def validate_service_number(service_number):
    """
    Validate service number is unique
    Returns: (is_valid, error_message)
    """
    if not service_number or service_number.strip() == "":
        return False, "Service number cannot be empty"
    
    service_number = service_number.strip()
    
    if service_number in consumers_db:
        return False, f"Service number {service_number} already exists. Please enter a unique service number"
    
    return True, ""


def get_valid_input(prompt, validation_func):
    """
    Generic function to get valid input with validation
    Keeps prompting until valid input is received
    """
    while True:
        user_input = input(prompt).strip()
        is_valid, error_msg = validation_func(user_input)
        
        if is_valid:
            return user_input
        else:
            print(f" Error: {error_msg}")
            print("Please try again.\n")


def get_consumer_details():
    """
    Input function to accept consumer details with validation
    Returns: dictionary with consumer details
    """
    print("\n" + "="*60)
    print("ENTER CONSUMER DETAILS")
    print("="*60)
    
    # Get service number with validation
    service_number = get_valid_input(
        "Enter Service/Consumer Number: ",
        validate_service_number
    )
    
    # Get name with validation
    name = get_valid_input(
        "Enter Consumer Name: ",
        validate_name
    )
    
    # Get phone number with validation
    phone = get_valid_input(
        "Enter Phone Number (10 digits): ",
        validate_phone
    )
    
    # Get previous reading
    while True:
        try:
            prev_reading = int(input("Enter Previous Meter Reading: "))
            if prev_reading < 0:
                print(" Error: Reading cannot be negative. Please try again.\n")
                continue
            break
        except ValueError:
            print(" Error: Please enter a valid number.\n")
    
    # Get current reading
    while True:
        try:
            current_reading = int(input("Enter Current Meter Reading: "))
            if current_reading < 0:
                print(" Error: Reading cannot be negative. Please try again.\n")
                continue
            if current_reading < prev_reading:
                print(" Error: Current reading cannot be less than previous reading. Please try again.\n")
                continue
            break
        except ValueError:
            print(" Error: Please enter a valid number.\n")
    
    # Get previous bill pending (if any)
    while True:
        try:
            prev_bill_pending = float(input("Enter Previous Bill Pending Amount (0 if none): "))
            if prev_bill_pending < 0:
                print(" Error: Amount cannot be negative. Please try again.\n")
                continue
            break
        except ValueError:
            print(" Error: Please enter a valid amount.\n")
    
    consumer_data = {
        'service_number': service_number,
        'name': name,
        'phone': phone,
        'prev_reading': prev_reading,
        'current_reading': current_reading,
        'prev_bill_pending': prev_bill_pending,
        'bill_date': datetime.now()
    }
    
    return consumer_data


def calculate_bill(units_consumed):
    """
    Computation function to calculate bill based on units consumed
    Rate structure:
    - First 50 units: Rs 1.5 per unit
    - Next 50 units (51-100): Rs 2.5 per unit
    - Next 50 units (101-150): Rs 3.5 per unit
    - Above 150: Rs 4.5 per unit
    - Minimum charge if 0 units: Rs 25
    
    Returns: total bill amount
    """
    if units_consumed == 0:
        return 25.0  # Minimum charge
    
    bill = 0.0
    remaining_units = units_consumed
    
    # First 50 units at Rs 1.5
    if remaining_units > 0:
        units_in_slab = min(remaining_units, 50)
        bill += units_in_slab * 1.5
        remaining_units -= units_in_slab
    
    # Next 50 units (51-100) at Rs 2.5
    if remaining_units > 0:
        units_in_slab = min(remaining_units, 50)
        bill += units_in_slab * 2.5
        remaining_units -= units_in_slab
    
    # Next 50 units (101-150) at Rs 3.5
    if remaining_units > 0:
        units_in_slab = min(remaining_units, 50)
        bill += units_in_slab * 3.5
        remaining_units -= units_in_slab
    
    # Remaining units at Rs 4.5
    if remaining_units > 0:
        bill += remaining_units * 4.5
    
    return round(bill, 2)


def display_bill(consumer_data):
    """
    Output function to display the electricity bill
    """
    units_consumed = consumer_data['current_reading'] - consumer_data['prev_reading']
    current_bill = calculate_bill(units_consumed)
    
    # Calculate due date (15 days from bill date)
    due_date = consumer_data['bill_date'] + timedelta(days=15)
    
    # Calculate total without fine
    total_without_fine = current_bill + consumer_data['prev_bill_pending']
    
    # Calculate total with fine
    fine_amount = 150.0
    total_with_fine = total_without_fine + fine_amount
    
    # Display bill
    print("\n" + "="*70)
    print(" " * 20 + "ELECTRICITY BILL")
    print("="*70)
    print(f"Bill Date: {consumer_data['bill_date'].strftime('%d-%m-%Y %H:%M:%S')}")
    print(f"Service Number: {consumer_data['service_number']}")
    print(f"Consumer Name: {consumer_data['name']}")
    print(f"Phone Number: {consumer_data['phone']}")
    print("-"*70)
    print(f"Previous Meter Reading: {consumer_data['prev_reading']:>10} units")
    print(f"Current Meter Reading:  {consumer_data['current_reading']:>10} units")
    print(f"Units Consumed:         {units_consumed:>10} units")
    print("-"*70)
    print("BILLING DETAILS:")
    print(f"Current Bill Amount:    Rs. {current_bill:>10.2f}")
    
    if consumer_data['prev_bill_pending'] > 0:
        print(f"Previous Bill Pending:  Rs. {consumer_data['prev_bill_pending']:>10.2f}")
    
    print("-"*70)
    print(f"Total Amount (Pay by {due_date.strftime('%d-%m-%Y')}): Rs. {total_without_fine:>10.2f}")
    print(f"After Due Date (with fine Rs. 150):   Rs. {total_with_fine:>10.2f}")
    print("="*70)
    
    # Show rate structure
    print("\nRate Structure:")
    print("  • First 50 units:      Rs. 1.5 per unit")
    print("  • Next 50 units:       Rs. 2.5 per unit")
    print("  • Next 50 units:       Rs. 3.5 per unit")
    print("  • Above 150 units:     Rs. 4.5 per unit")
    print("  • Minimum charge:      Rs. 25.0 (if 0 units consumed)")
    print("  • Late payment fine:   Rs. 150.0")
    print("="*70)
    
    return consumer_data


def save_consumer(consumer_data):
    """
    Save consumer data to the database
    """
    consumers_db[consumer_data['service_number']] = consumer_data
    print(f"\n✓ Consumer record saved successfully!")


def view_all_consumers():
    """
    Display all registered consumers
    """
    if not consumers_db:
        print("\n No consumer records found.")
        return
    
    print("\n" + "="*70)
    print("ALL REGISTERED CONSUMERS")
    print("="*70)
    print(f"{'Service No':<15} {'Name':<25} {'Phone':<15} {'Units':<10}")
    print("-"*70)
    
    for service_num, data in consumers_db.items():
        units = data['current_reading'] - data['prev_reading']
        print(f"{service_num:<15} {data['name']:<25} {data['phone']:<15} {units:<10}")
    
    print("="*70)
    print(f"Total Consumers: {len(consumers_db)}")


def main():
    """
    Main function to orchestrate the electricity bill system
    """
    print("\n" + "="*70)
    print(" " * 15 + "ELECTRICITY BILL MANAGEMENT SYSTEM")
    print("="*70)
    
    while True:
        print("\n" + "-"*70)
        print("MENU:")
        print("1. Generate New Bill")
        print("2. View All Consumers")
        print("3. Exit")
        print("-"*70)
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            try:
                # Get consumer details
                consumer_data = get_consumer_details()
                
                # Display bill
                consumer_data = display_bill(consumer_data)
                
                # Save to database
                save_consumer(consumer_data)
                
            except KeyboardInterrupt:
                print("\n\n Operation cancelled by user.")
            except Exception as e:
                print(f"\n An error occurred: {e}")
        
        elif choice == '2':
            view_all_consumers()
        
        elif choice == '3':
            print("\n" + "="*70)
            print("Thank you for using Electricity Bill Management System!")
            print("="*70)
            break
        
        else:
            print("\n Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
