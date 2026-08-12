from datetime import datetime
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.base_repository import BaseRepository
from app.services.customer_service import CustomerService
from app.core.config import Config

class OrderService:
    @staticmethod
    def get_settings():
        """Reads application settings."""
        return OrderRepository.get_settings()

    @staticmethod
    def get_gst_rate():
        """Helper to get default GST rate from settings."""
        return OrderRepository.get_gst_rate()

    @staticmethod
    def update_gst_rate(new_rate):
        """Updates the default GST rate configuration."""
        OrderRepository.update_setting('gst_rate', new_rate)

    @classmethod
    def calculate_order(cls, customer_data, items_data):
        """
        Calculates pricing, line totals, subtotal, GST, and grand total.
        items_data format: list of dicts: {'product_id': X, 'quantity': Y, 'discount_percentage': Z}
        customer_data format: dict: {'id': X, 'name': 'Name', 'discount_percentage': D, ...}
        
        Returns:
            dict containing calculated order structure + stock warnings
        """
        gst_rate = cls.get_gst_rate()
        subtotal = 0.0
        calculated_items = []
        has_warnings = False
        
        cust_discount = float(customer_data.get('discount_percentage', 0) or 0)
        
        for item in items_data:
            product_id = item.get('product_id')
            part_number = item.get('part_number')
            qty = float(item.get('quantity', 0) or 0)
            
            prod = None
            if product_id:
                prod = ProductRepository.get_by_id(product_id)
            if not prod and part_number:
                prod = ProductRepository.get_by_part_number(part_number)
            if not prod and part_number:
                from app.services.import_service import ImportService
                norm_p = ImportService.normalize_part_number(part_number)
                all_p = ProductRepository.get_all_billing_products()
                for p in all_p:
                    if ImportService.normalize_part_number(p['part_number']) == norm_p:
                        prod = ProductRepository.get_by_id(p['id'])
                        break
            if not prod and part_number:
                clean_pn = str(part_number).strip()
                new_pid = ProductRepository.save_product(clean_pn, part_name=clean_pn)
                prod = ProductRepository.get_by_id(new_pid)
                
            if not prod:
                raise ValueError(f"Product ID {product_id} / Part Number '{part_number}' not found in database.")
            
            if item.get('unit_price') is not None:
                price_per_unit = float(item['unit_price'])
            elif item.get('unit_price_100') is not None:
                price_per_unit = float(item['unit_price_100']) / 100.0
            elif prod['price_per_unit'] is not None:
                price_per_unit = float(prod['price_per_unit'])
            else:
                price_per_unit = float(prod['price_per_100_pcs'] or 0) / 100.0

            current_stock = float(prod.get('current_stock', 0) or 0)
            
            discount_pct = item.get('discount_percentage')
            if discount_pct is None or discount_pct == '':
                discount_pct = cust_discount
            else:
                discount_pct = float(discount_pct)
                
            discounted_unit_price = price_per_unit * (1 - (discount_pct / 100.0))
            line_total = qty * discounted_unit_price
            subtotal += line_total
            
            insufficient_stock = qty > current_stock
            if insufficient_stock:
                has_warnings = True
                
            calculated_items.append({
                "product_id": prod["id"],
                "part_number": prod["part_number"],
                "part_name": prod.get("part_name") or prod["part_number"],
                "quantity": qty,
                "current_stock": current_stock,
                "unit_price": price_per_unit,
                "unit_price_100": price_per_unit * 100.0,
                "discount_percentage": discount_pct,
                "gst_percentage": gst_rate,
                "line_total": round(line_total, 2),
                "insufficient_stock": insufficient_stock
            })
            
        gst_amount = subtotal * (gst_rate / 100.0)
        grand_total = subtotal + gst_amount
        
        return {
            "customer": {
                "name": customer_data.get('name'),
                "gst_number": customer_data.get('gst_number'),
                "payment_terms": customer_data.get('payment_terms'),
                "discount_percentage": cust_discount
            },
            "items": calculated_items,
            "subtotal": round(subtotal, 2),
            "gst_rate": gst_rate,
            "gst_amount": round(gst_amount, 2),
            "grand_total": round(grand_total, 2),
            "has_warnings": has_warnings
        }

    @classmethod
    def create_order(cls, customer_input, items_input):
        """
        Calculates and creates a persistent Order.
        Saves inline customers if they do not exist.
        """
        conn = BaseRepository.get_connection()
        cur = conn.cursor()
        
        # 1. Resolve customer
        customer_id = customer_input.get('id')
        customer_name = str(customer_input.get('name', '')).strip()
        discount_percentage = float(customer_input.get('discount_percentage', 0) or 0)
        gst_number = customer_input.get('gst_number')
        payment_terms = customer_input.get('payment_terms')
        
        if not customer_name:
            raise ValueError("Customer name is required.")
            
        cust = None
        if customer_id:
            cust = CustomerService.get_customer_by_id(customer_id)
        else:
            cust = CustomerService.get_customer_by_name(customer_name)
            
        if not cust:
            cust = CustomerService.create_customer(
                name=customer_name,
                discount_percentage=discount_percentage,
                gst_number=gst_number,
                payment_terms=payment_terms
            )
            customer_id = cust['id']
        else:
            customer_id = cust['id']
        
        calc = cls.calculate_order(cust, items_input)
        
        try:
            cur.execute("BEGIN IMMEDIATE TRANSACTION;")
            
            temp_order_num = f"ORD-TEMP-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            cur.execute(
                """INSERT INTO ORDERS (
                        order_number, customer_id, customer_name_snapshot, 
                        customer_gst_snapshot, customer_terms_snapshot, 
                        discount_percentage, subtotal, discount_amount, 
                        gst_amount, grand_total, gst_rate
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    temp_order_num, customer_id, customer_name,
                    gst_number or cust['gst_number'], payment_terms or cust['payment_terms'],
                    discount_percentage, calc['subtotal'], 0.0,
                    calc['gst_amount'], calc['grand_total'], calc['gst_rate']
                )
            )
            order_id = cur.lastrowid
            
            order_number = f"ORD-{datetime.now().year}-{order_id:05d}"
            cur.execute("UPDATE ORDERS SET order_number = ? WHERE id = ?", (order_number, order_id))
            
            for idx, item in enumerate(calc['items']):
                p_id = item.get('product_id')
                part_no = str(item.get('part_number', '') or '').strip()
                if not part_no:
                    part_no = f"PART-ITEM-{idx + 1}"
                part_name = str(item.get('part_name') or part_no).strip()

                p_row = None
                if p_id:
                    cur.execute("SELECT id FROM PRODUCTS WHERE id = ?", (p_id,))
                    p_row = cur.fetchone()
                if not p_row and part_no:
                    cur.execute("SELECT id FROM PRODUCTS WHERE part_number = ?", (part_no,))
                    p_row = cur.fetchone()

                if not p_row:
                    try:
                        cur.execute(
                            "INSERT INTO PRODUCTS (part_number, part_name, series, make) VALUES (?, ?, ?, ?)",
                            (part_no, part_name, None, 'WAGO')
                        )
                        p_id = cur.lastrowid
                    except Exception:
                        unique_pn = f"{part_no}-{datetime.now().strftime('%S%f')}"
                        cur.execute(
                            "INSERT INTO PRODUCTS (part_number, part_name, series, make) VALUES (?, ?, ?, ?)",
                            (unique_pn, part_name, None, 'WAGO')
                        )
                        p_id = cur.lastrowid
                else:
                    p_id = p_row['id']

                qty = float(item.get('quantity', 0.0) or 0.0)
                u_price = float(item.get('unit_price_100', 0.0) or 0.0)
                disc_p = float(item.get('discount_percentage', 0.0) or 0.0)
                gst_p = float(item.get('gst_percentage', 0.0) or 0.0)
                l_total = float(item.get('line_total', 0.0) or 0.0)

                cur.execute(
                    """INSERT INTO ORDER_ITEMS (
                            order_id, product_id, part_number_snapshot, part_name_snapshot, 
                            quantity, unit_price, discount_percentage, gst_percentage, line_total
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        order_id, p_id, part_no, part_name,
                        qty, u_price, disc_p, gst_p, l_total
                    )
                )
                
            conn.commit()
            return order_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()

    @classmethod
    def get_order_by_id(cls, order_id):
        """Retrieves order with associated items."""
        return OrderRepository.get_by_id(order_id)
