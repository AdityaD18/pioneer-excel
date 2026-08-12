from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.core.logger import app_logger

class InventoryService:
    """Service handling stock levels, inventory math, and reorder status calculations."""

    @staticmethod
    def calculate_reorder_metrics(stock_val, purc_val, sales_val, reorder_val=0.0, min_reorder_val=0.0, nett_raw=None, shortfall_raw=None, order_to_place_raw=None):
        """Calculates derived inventory metrics based on stock, pending orders, and reorder levels."""
        if nett_raw is not None:
            nett_val = nett_raw
        else:
            nett_val = stock_val + purc_val - sales_val
            
        if shortfall_raw is not None:
            shortfall_val = shortfall_raw
        else:
            shortfall_val = max(0.0, reorder_val - nett_val)
            
        if order_to_place_raw is not None:
            order_to_place_val = order_to_place_raw
        else:
            order_to_place_val = max(shortfall_val, min_reorder_val) if shortfall_val > 0 else 0.0
            
        return {
            "nett_available": nett_val,
            "shortfall": shortfall_val,
            "order_to_place": order_to_place_val
        }

    @classmethod
    def update_product_stock(cls, product_id, new_stock_qty):
        """Updates stock quantity for a product."""
        app_logger.info(f"Updating stock for product ID {product_id} to {new_stock_qty} PCS.")
        InventoryRepository.update_stock(product_id, new_stock_qty)

    @classmethod
    def get_reorder_status_sheet(cls, search_query=None, only_reorder=False):
        """Retrieves stock group reorder status sheet records."""
        return InventoryRepository.get_stock_sheet(search_kw=search_query, only_reorder=only_reorder)

    @classmethod
    def verify_stock_availability(cls, line_items, safety_buffer=0.0):
        """
        Audits requested billing line items against database inventory after applying a safety stock buffer.
        Returns detailed stock status dictionary with item-level verification flags.
        """
        audit_results = []
        has_insufficient = False
        
        for item in line_items:
            part_number = item.get('part_number', '')
            req_qty = float(item.get('quantity', 0.0))
            
            # Fetch inventory details
            inv = InventoryRepository.get_stock_sheet(search_kw=part_number)
            current_stock = 0.0
            if inv:
                closing = float(inv[0].get('Closing Stock', 0.0) or 0.0)
                nett = float(inv[0].get('Nett Available', 0.0) or 0.0)
                current_stock = max(closing, nett)
                
            effective_available = max(0.0, current_stock - safety_buffer)
            is_insufficient = req_qty > effective_available
            if is_insufficient:
                has_insufficient = True
                
            audit_results.append({
                "part_number": part_number,
                "requested_qty": req_qty,
                "current_stock": current_stock,
                "safety_buffer": safety_buffer,
                "effective_available": effective_available,
                "shortfall": max(0.0, req_qty - effective_available),
                "is_insufficient": is_insufficient
            })
            
        return {
            "has_insufficient_stock": has_insufficient,
            "items": audit_results
        }

