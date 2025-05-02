# api.py

import asyncio
import logging
import hashlib
import os
import io
import zipfile
import time
import json
import mimetypes
import math
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List, Optional
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Depends, Security, status, BackgroundTasks, Request, File, UploadFile, Query
from fastapi.security import SecurityScopes, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.responses import JSONResponse, StreamingResponse, Response

from .mpesa import initiate_stk_push, query_stk_status
from .validators import ProductValidator

from dotenv import load_dotenv

load_dotenv()

from .storage_node import StorageNode  # Import StorageNode
from .credit_manager import CreditManager
from .node import Node
from .product import Product
from .auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    get_current_user,
    authenticate_user,
    create_access_token,
    get_password_hash,
    add_credits_to_user,
    deduct_credits_from_user,
    get_user_credits,
)
from .database import async_session
from .db_models import User as DBUser
from .models import (
    Token,
    ProductIn,
    ProductOut,
    UserCredentials,
    User as UserModel,
    ImageManifest,
    CategorySuggestion,
)

from sqlalchemy.future import select
from .debug import router as debug_router
from .marketplace import router as marketplace_router




# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)

# Retrieve configuration from environment variables
### CHANGED: We now expect ADVERTISE_IP, not NODE_IP
ADVERTISE_IP = os.getenv('ADVERTISE_IP')
if not ADVERTISE_IP:
    raise ValueError("ADVERTISE_IP environment variable not set")
NODE_PORT = int(os.getenv('NODE_PORT', '8000'))
ENCRYPTION_PASSWORD = os.getenv("ENCRYPTION_PASSWORD")

# Initialize the CreditManager
credit_manager = CreditManager()

# Use lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting production node lifespan...")

        # Re-load environment in case they're set differently
        ADVERTISE_IP = os.getenv('ADVERTISE_IP')
        if not ADVERTISE_IP:
            raise ValueError("ADVERTISE_IP environment variable not set")
        NODE_PORT = int(os.getenv('NODE_PORT', '8000'))
        NODE_TCP_PORT = int(os.getenv('NODE_TCP_PORT', str(NODE_PORT + 500)))
        ENCRYPTION_PASSWORD = os.getenv("ENCRYPTION_PASSWORD")

        # Initialize the CreditManager
        credit_manager = CreditManager()

        # Create the single StorageNode
        ### CHANGED: We bind internally to 0.0.0.0, but advertise as ADVERTISE_IP
        app.state.node = StorageNode(
            ip="0.0.0.0",         # bind IP
            port=NODE_PORT,
            tcp_port=NODE_TCP_PORT,
            credit_manager=credit_manager,
            storage_dir="storage_chunks",
            cleanup_interval=60,
            republish_interval=3600,
            alpha=3,
            k=20,
            node_id=None,
            advertise_ip=ADVERTISE_IP,  # public or DNS
        )
        logger.info(f"Created StorageNode for ADVERTISE_IP: {ADVERTISE_IP}, Port: {NODE_PORT}")

        # Read bootstrap nodes from environment with enhanced ngrok support
        bootstrap_list = []
        raw_bootstrap = os.getenv("BOOTSTRAP_NODES", "").strip()

        if raw_bootstrap:
            logger.info(f"Processing bootstrap nodes from: {raw_bootstrap}")
            for segment in raw_bootstrap.split(","):
                segment = segment.strip()
                if not segment:
                    continue

                try:
                    # Ensure URL has protocol prefix
                    if not segment.startswith(('http://', 'https://')):
                        segment = 'https://' + segment.lstrip('/')

                    logger.debug(f"Processing URL: {segment}")
                    parsed_url = urlparse(segment)

                    # Extract hostname, removing any leading/trailing slashes
                    host = parsed_url.hostname
                    if not host:
                        logger.warning(f"Could not extract hostname from {segment}")
                        continue

                    # Use parsed port or default based on scheme
                    port = parsed_url.port
                    if port is None:
                        port = 443 if parsed_url.scheme == 'https' else 80

                    logger.info(f"Parsed bootstrap node - Host: {host}, Port: {port}")
                    bootstrap_list.append((host, port))

                except Exception as e:
                    logger.warning(f"Error processing bootstrap node '{segment}': {str(e)}")
                    continue

        logger.info(f"Final bootstrap nodes list: {bootstrap_list}")

        # Start the node (async)
        await app.state.node.start(bootstrap_nodes=bootstrap_list)

        if not app.state.node:
            logger.error("Critical: node is None after starting!")
            raise RuntimeError("StorageNode failed to initialize")

        logger.info(
            f"StorageNode started successfully. Node ID: {app.state.node.node_id}"
        )

        yield  # Run the application

    except Exception as e:
        logger.error("Error in node lifespan: %s", e, exc_info=True)
        raise

    finally:
        # On shutdown
        node = getattr(app.state, "node", None)
        if node is not None:
            logger.info(f"Shutting down node ID: {node.node_id}")
            try:
                await node.stop()
                logger.info("StorageNode shut down gracefully.")
            except Exception as e:
                logger.error("Error shutting down node: %s", e, exc_info=True)

# Declare the FastAPI application with lifespan
app = FastAPI(title="Network API", version="0.1.0", lifespan=lifespan)

# Include the debug router with a prefix if desired (or without one)
app.include_router(debug_router)
app.include_router(marketplace_router)

def check_node_initialized(request: Request):
    """Helper function to check if node is initialized"""
    if not hasattr(request.app.state, 'node') or request.app.state.node is None:
        logger.error("Node is not initialized!")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Node is not initialized. Please try again later."
        )
    return request.app.state.node

@app.post("/register", response_model=UserModel)
async def register_user(user_in: UserCredentials):
    """
    Endpoint to register a new user.
    """
    async with async_session() as session:
        # Check if username already exists
        result = await session.execute(
            select(DBUser).where(DBUser.username == user_in.username)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = get_password_hash(user_in.password)

        # Validate the scopes provided
        valid_scopes = set(
            [
                "products:write",
                "products:read",
                "credits:manage",
                "categories:write",
                "categories:read",
            ]
        )
        user_scopes = set(user_in.scopes)
        invalid_scopes = user_scopes - valid_scopes
        if invalid_scopes:
            raise HTTPException(
                status_code=400, detail=f"Invalid scopes: {invalid_scopes}"
            )

        scopes_str = (
            ",".join(user_scopes)
            if user_scopes
            else "products:write,products:read,credits:manage"
        )

        # Create new user
        new_user = DBUser(
            username=user_in.username,
            hashed_password=hashed_password,
            email=user_in.email,
            full_name=user_in.full_name,
            credits=100.0,  # Initial credits
            scopes=scopes_str,
            phone_number=user_in.phone_number,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return UserModel(
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            disabled=new_user.disabled,
            scopes=new_user.scopes.split(",") if new_user.scopes else [],
            credits=new_user.credits,
            phone_number=new_user.phone_number,
        )

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to obtain an access token.
    """
    scopes = form_data.scopes
    # Authenticate user using database
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    user_scopes = user.scopes.split(',') if user.scopes else []

    for scope in scopes:
        if scope not in user_scopes:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": "Bearer"},
            )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": scopes}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.post("/products", response_model=ProductOut)
async def create_product(
    request: Request,
    product_in: ProductIn,
    current_user: DBUser = Security(get_current_user, scopes=["products:write"]),
):
    """
    Endpoint to create (upload) a new product on the DHT-based network,
    now enforcing only approved categories and letting users specify
    how many days it stays on the network.

    Charges 1 credit per day of storage.
    """
    try:
        node = check_node_initialized(request)
        logger.debug(f"Starting product creation process for user {current_user.username}")

        # 1) Check category is approved
        categories_key = hashlib.sha1("categories".encode("utf-8")).hexdigest()
        categories_json = await node.find_value(categories_key)
        approved_categories = []
        if categories_json:
            approved_categories = json.loads(categories_json)
        
        product_category = product_in.core.category.strip()
        if product_category not in approved_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{product_category}' is not approved. Please choose from {approved_categories}.",
            )
        
        # 2) Determine how many days to store and compute required credits
        #    (default = 7 days if not specified)
        duration_days = product_in.extended.storage_duration_days or 7
        if duration_days <= 0:
            duration_days = 7  # Safeguard if user passes 0 or negative

        required_credits = float(duration_days)  # 1 credit per day

        # 3) Check if user has enough credits
        if not await deduct_credits_from_user(current_user.username, required_credits):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Need {required_credits} credits to store for {duration_days} days.",
            )

        # 4) Generate a product_id
        product_id = hashlib.sha1(product_in.core.name.encode("utf-8")).hexdigest()
        logger.debug(f"Generated product_id: {product_id}")

        # 5) Populate routing table with nodes close to product_id
        logger.debug(f"Finding nodes close to product_id {product_id}")
        await node.find_nodes(product_id)
        logger.debug("Successfully populated routing table with nearby nodes")

        # 6) Create a Product instance
        product = Product(
            product_id=product_id,
            core=product_in.core.dict(),
            extended=product_in.extended.dict(),
            image_refs=[],
        )

        # 7) Store product with a TTL = duration_days in seconds
        product_ttl_seconds = duration_days * 86400
        
        logger.debug(f"Storing product {product_id} with TTL of {product_ttl_seconds} seconds.")
        await node.store_product(product, ENCRYPTION_PASSWORD, ttl=product_ttl_seconds)
        logger.debug(f"Product {product_id} stored successfully with TTL={duration_days} days")

        # 8) Verify storage
        verification_product = await node.find_product(product_id, ENCRYPTION_PASSWORD)
        if not verification_product:
            logger.error(f"Product {product_id} could not be verified after storage")
            # Roll back credits if storage verification fails
            await add_credits_to_user(current_user.username, required_credits)
            raise HTTPException(
                status_code=500, detail="Product storage could not be verified"
            )
        logger.debug(f"Product {product_id} verified successfully")

        # 9) Index the product with retries
        try:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.debug(f"Calling index_product for {product_id} (attempt {attempt+1}/{max_retries})")
                    await node.index_product(product)
                    logger.debug(f"Product {product_id} indexed successfully on attempt {attempt+1}")
                    break
                except Exception as index_error:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to index '{product_id}' after {max_retries} attempts: {str(index_error)}")
                        raise
                    logger.warning(f"Index attempt {attempt+1} failed with error: {str(index_error)}, retrying...")
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
        except Exception as index_error:
            # Roll back storage and credits if indexing fails
            logger.error(f"Rolling back storage and credits for product {product_id} due to indexing failure")
            await node.delete_product(product_id, ENCRYPTION_PASSWORD)
            await add_credits_to_user(current_user.username, required_credits)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to index product: {str(index_error)}"
            )

        return ProductOut(
            product_id=product.product_id,
            core=product.core,
            extended=product.extended,
            image_refs=product.image_refs,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}", exc_info=True)
        # Attempt to refund credits if something unexpected goes wrong
        try:
            await add_credits_to_user(current_user.username, required_credits)
        except Exception as refund_error:
            logger.error(f"Failed to refund credits: {str(refund_error)}")
        raise HTTPException(status_code=500, detail=str(e))

async def retry_find_product(node, product_id, encryption_password, max_retries=3, delay=1):
    """
    Retry product retrieval multiple times with delay.
    """
    # Get the current routing table once before starting retries
    nodes = node.routing_table.get_all_nodes()
    
    # Prepare a separate list of dicts describing the nodes
    nodes_info = [
        {'node_id': n.node_id, 'ip': n.ip, 'port': n.port} 
        for n in nodes
    ]
    
    # Use that list in the log
    logger.debug(f"Current routing table: {nodes_info}")
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempting to retrieve product {product_id} (attempt {attempt + 1}/{max_retries})")
            product = await node.find_product(product_id, encryption_password)
            
            if product:
                logger.debug(f"Successfully retrieved product {product_id} on attempt {attempt + 1}")
                return product
            
            logger.warning(f"Product {product_id} not found, attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                logger.debug(f"Waiting {delay} seconds before next attempt")
                await asyncio.sleep(delay)
                
        except Exception as e:
            logger.error(f"Error in attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                logger.debug(f"Waiting {delay} seconds before next attempt")
                await asyncio.sleep(delay)
    
    return None

@app.get("/products/{product_id}", response_model=ProductOut)
async def get_product(
    request: Request,
    product_id: str,
    current_user: DBUser = Security(get_current_user, scopes=["products:read"]),
):
    """
    Endpoint to retrieve a product by its ID with retry mechanism and credit check.
    """
    try:
        # Check node initialization
        node = check_node_initialized(request)

        # Check credits first
        required_credits = 1.0
        logger.debug(f"Checking credits for user {current_user.username}")
        if not await deduct_credits_from_user(current_user.username, required_credits):
            logger.warning(f"Insufficient credits for user {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits to access this product.",
            )
        logger.debug(f"Successfully deducted {required_credits} credits from user {current_user.username}")

        # Try to retrieve the product with retries
        product = await retry_find_product(node, product_id, ENCRYPTION_PASSWORD)
        if not product:
            logger.warning(f"Product {product_id} not found after all retry attempts")
            raise HTTPException(status_code=404, detail="Product not found")

        logger.info(f"Product {product_id} successfully retrieved by user {current_user.username}")
        return ProductOut(
            product_id=product.product_id,
            core=product.core,
            extended=product.extended,
            image_refs=product.image_refs
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products", response_model=List[ProductOut])
async def search_products(
    request: Request,
    category: Optional[str] = Query(None, description="Category to filter products by"),
    shop_name: Optional[str] = Query(
        None, description="Shop name to filter products by"
    ),
    latitude: Optional[float] = Query(None, description="Latitude for seller location"),
    longitude: Optional[float] = Query(
        None, description="Longitude for seller location"
    ),
    radius_km: float = Query(
        10.0, description="Radius in kilometers for location filtering"
    ),
    current_user: DBUser = Security(get_current_user, scopes=["products:read"]),
):
    """
    Endpoint to search for products by category, shop name, or seller location.

    At least one of 'category', 'shop_name', or (latitude+longitude) must be provided.
    """
    node = check_node_initialized(request)

    if not category and not shop_name and (latitude is None or longitude is None):
        raise HTTPException(
            status_code=400,
            detail="At least one search parameter is required",
        )

    # Check if the user has enough credits
    required_credits = 1.0
    if not await deduct_credits_from_user(current_user.username, required_credits):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits to perform search.",
        )

    products = []
    product_ids = set()

    # Search by category
    if category:
        found_products = await node.search_products_by_attribute(
            "category", category.strip().lower(), ENCRYPTION_PASSWORD
        )
        for product in found_products:
            if product.product_id not in product_ids:
                products.append(product)
                product_ids.add(product.product_id)

    # Search by shop name
    if shop_name:
        found_products = await node.search_products_by_attribute(
            "shop_name", shop_name.strip().lower(), ENCRYPTION_PASSWORD
        )
        for product in found_products:
            if product.product_id not in product_ids:
                products.append(product)
                product_ids.add(product.product_id)

    # Search by seller location
    if latitude is not None and longitude is not None:
        bin_size = 0.1  # degrees, adjust this granularity as needed
        lat_bins = generate_bins(latitude, radius_km, bin_size)
        lon_bins = generate_bins(longitude, radius_km, bin_size)

        bins_to_search = [
            f"{lat_bin},{lon_bin}" for lat_bin in lat_bins for lon_bin in lon_bins
        ]

        for bin_key in bins_to_search:
            found_products = await node.search_products_by_attribute(
                "seller_location", bin_key, ENCRYPTION_PASSWORD
            )
            for product in found_products:
                if product.product_id not in product_ids:
                    products.append(product)
                    product_ids.add(product.product_id)

    # Remove duplicates
    unique_products = {product.product_id: product for product in products}.values()

    # Further filter products by precise distance
    if latitude is not None and longitude is not None:
        filtered_products = []
        for product in unique_products:
            prod_location = product.core.get("seller_location")
            if prod_location and len(prod_location) == 2:
                prod_lat, prod_lon = prod_location
                distance = haversine(latitude, longitude, prod_lat, prod_lon)
                if distance <= radius_km:
                    filtered_products.append(product)
        unique_products = filtered_products

    logger.info(f"User {current_user.username} searched for products")

    return [
        ProductOut(
            product_id=product.product_id,
            core=product.core,
            extended=product.extended,
            image_refs=product.image_refs,
        )
        for product in unique_products
    ]

def haversine(lat1, lon1, lat2, lon2):
    # Calculate the great-circle distance between two points on the Earth
    R = 6371.0  # Radius of Earth in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def generate_bins(center_coord, radius_km, bin_size):
    # Generate coordinate bins within the radius
    coord_radius = radius_km / 111.0  # Convert km to degrees (approx)
    min_coord = center_coord - coord_radius
    max_coord = center_coord + coord_radius

    bins = []
    curr_coord = round(min_coord / bin_size) * bin_size
    while curr_coord <= max_coord:
        bins.append(round(curr_coord, 2))
        curr_coord += bin_size

    return bins

@app.get("/credits/balance")
async def get_credit_balance(
    current_user: DBUser = Security(get_current_user, scopes=["credits:manage"]),
):
    """
    Endpoint to get the current credit balance for a user.
    """
    credits = await get_user_credits(current_user.username)
    return {"username": current_user.username, "credits": credits}

# Create a global transactions dictionary to store transaction details
transactions = {}  # Key: checkout_request_id, Value: transaction data

# Define a Pydantic model for the request body
class PurchaseCreditsRequest(BaseModel):
    amount: int  # Change from float to int
    phone_number: Optional[str] = None

@app.post("/credits/purchase")
async def purchase_credits(
    request: Request,
    background_tasks: BackgroundTasks,
    purchase_request: PurchaseCreditsRequest,
    current_user: DBUser = Security(get_current_user, scopes=["credits:manage"]),
):
    """
    Endpoint for users to purchase credits.
    Initiates an M-Pesa STK Push and schedules a background task to process it.
    """
    amount = purchase_request.amount
    phone_number = purchase_request.phone_number or current_user.phone_number

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero.")

    if not phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required.")

    try:
        # Start payment by initiating STK Push
        result = await initiate_stk_push(phone_number, amount)
        checkout_request_id = result.get('CheckoutRequestID')
        if not checkout_request_id:
            logger.error("No CheckoutRequestID received from M-Pesa")
            raise HTTPException(status_code=500, detail="Failed to initiate payment.")

        # Store transaction details
        transactions[checkout_request_id] = {
            "username": current_user.username,
            "amount": amount,
            "status": "pending",
            "phone_number": phone_number,
            "checkout_request_id": checkout_request_id,
            "start_time": time.time()
        }

        # Schedule background task to process payment
        background_tasks.add_task(process_payment_background, checkout_request_id)

        logger.info(f"User {current_user.username} initiated purchase of {amount} credits.")
        return {
            "message": "Payment initiated. Please complete the payment on your phone.",
            "checkout_request_id": checkout_request_id
        }
    except Exception as e:
        logger.error(f"Payment initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate payment.")

async def process_payment_background(checkout_request_id: str):
    transaction = transactions.get(checkout_request_id)
    if not transaction:
        logger.error(f"Transaction {checkout_request_id} not found.")
        return

    username = transaction["username"]
    amount = transaction["amount"]
    phone_number = transaction["phone_number"]

    try:
        polling_interval = 10  # seconds
        timeout = 300  # seconds
        start_time = time.time()
        while time.time() - start_time < timeout:
            await asyncio.sleep(polling_interval)
            status_result = await query_stk_status(checkout_request_id)
            if 'ResultCode' in status_result:
                result_code = status_result.get('ResultCode')
                if result_code == "0":
                    # Transaction successful
                    logger.info(f"Payment successful for {username}, amount {amount}")
                    await add_credits_to_user(username, amount)
                    transaction["status"] = "completed"
                    transaction["result_description"] = status_result.get('ResultDesc')
                    return
                elif result_code in ["1032"]:
                    # Transaction cancelled by user
                    logger.warning(f"Payment cancelled by user for {username}")
                    transaction["status"] = "cancelled"
                    transaction["result_description"] = status_result.get('ResultDesc')
                    return
                elif result_code in ["1", "2", "3", "4"]:
                    # Transaction failed
                    logger.error(f"Payment failed for {username}: {status_result.get('ResultDesc')}")
                    transaction["status"] = "failed"
                    transaction["result_description"] = status_result.get('ResultDesc')
                    return
                else:
                    # Other ResultCodes
                    logger.info(f"Unhandled ResultCode {result_code} for {username}")
                    transaction["status"] = "error"
                    transaction["result_description"] = status_result.get('ResultDesc')
                    return
            elif 'errorCode' in status_result:
                error_code = status_result.get('errorCode')
                error_message = status_result.get('errorMessage')
                if error_code == "500.001.1001" and error_message == "The transaction is being processed":
                    # Transaction is still being processed
                    logger.info(f"Payment pending for {username} - transaction is being processed.")
                    continue
                else:
                    # Some other error occurred
                    logger.error(f"Payment processing error for {username}: {error_message}")
                    transaction["status"] = "error"
                    transaction["error_message"] = error_message
                    return
            else:
                logger.error(f"Unrecognized response from M-Pesa for {username}: {status_result}")
                transaction["status"] = "error"
                transaction["error_message"] = "Unrecognized response from M-Pesa"
                return
        # Timeout
        logger.warning(f"Payment processing timed out for {username}")
        transaction["status"] = "timeout"
    except Exception as e:
        logger.error(f"Payment processing error for {username}: {str(e)}")
        transaction["status"] = "error"
        transaction["error_message"] = str(e)

@app.get("/credits/purchase/status")
async def get_purchase_status(
    request: Request,
    checkout_request_id: str,
    current_user: DBUser = Security(get_current_user, scopes=["credits:manage"]),
):
    """
    Endpoint for users to check the status of their credit purchase.
    """
    transaction = transactions.get(checkout_request_id)
    if not transaction or transaction["username"] != current_user.username:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    return {
        "status": transaction["status"],
        "amount": transaction["amount"],
        "phone_number": transaction["phone_number"],
        "result_description": transaction.get("result_description"),
        "error_message": transaction.get("error_message"),
    }

@app.post("/categories/suggest")
async def suggest_category(
    request: Request,
    suggestion: CategorySuggestion,
    current_user: DBUser = Security(get_current_user, scopes=["categories:write"]),
):
    """
    Endpoint to allow users to suggest a new category.
    The suggestion must be unique (i.e., not currently in the categories list).
    """
    node = check_node_initialized(request)
    category_name = suggestion.category_name.strip()
    logger.info(f"User '{current_user.username}' is suggesting category '{category_name}'")

    try:
        # First, ensure it doesn't already exist locally
        categories_key = hashlib.sha1("categories".encode("utf-8")).hexdigest()
        categories_json = await node.find_value(categories_key)

        if categories_json:
            current_categories = json.loads(categories_json)
            if category_name in current_categories:
                # Already exists; reject immediately
                raise HTTPException(
                    status_code=400,
                    detail=f"Category '{category_name}' already exists in the network."
                )

        # If it doesn't exist, proceed to suggest to validator nodes
        success = await node.suggest_category(category_name)

        if success:
            logger.info(f"Category '{category_name}' was approved and added to the categories list.")
            return {"message": f"Category '{category_name}' has been approved and added."}
        else:
            logger.info(f"Category '{category_name}' was not approved.")
            return {"message": f"Category '{category_name}' was not approved."}

    except asyncio.CancelledError:
        logger.warning("Request was cancelled or timed out.")
        return JSONResponse(
            status_code=503,
            content={"message": "Request was cancelled or timed out."}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suggesting category '{category_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while suggesting the category."
        )

@app.get("/categories")
async def get_categories(request: Request):
    """
    Endpoint to retrieve the list of available categories.
    """
    node = check_node_initialized(request)

    try:
        categories_key = hashlib.sha1("categories".encode("utf-8")).hexdigest()
        categories_json = await node.find_value(categories_key)

        if categories_json:
            categories = json.loads(categories_json)
            logger.debug(f"Retrieved categories: {categories}")
            logger.info("Categories successfully retrieved.")
            return {"categories": categories}
        else:
            logger.warning("No categories found in the network.")
            return {"categories": []}

    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve categories.")

@app.get("/debug/network")
async def debug_network(request: Request):
    """Get network debug information."""
    node = check_node_initialized(request)
    return {
        "node_id": node.node_id,
        "advertise_ip": node.advertise_ip,
        "port": node.port,
        "routing_table_size": len(node.routing_table.get_all_nodes()),
        "pending_requests": len(node.pending_requests),
    }

@app.get("/debug/routing-table")
async def debug_routing_table(request: Request):
    """Get routing table information."""
    node = check_node_initialized(request)

    nodes = node.routing_table.get_all_nodes()
    return {
        "total_nodes": len(nodes),
        "nodes": [{"node_id": n.node_id, "ip": n.ip, "port": n.port} for n in nodes],
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/debug/network-health")
async def network_health(request: Request):
    """Check network health and connectivity."""
    node = check_node_initialized(request)

    nodes = node.routing_table.get_all_nodes()
    health_status = {
        "total_nodes": len(nodes),
        "node_status": []
    }

    for n in nodes:
        try:
            ping_result = await node.ping_node(n)
            health_status["node_status"].append({
                "node_id": n.node_id,
                "ip": n.ip,
                "port": n.port,
                "responsive": ping_result
            })
        except Exception as e:
            health_status["node_status"].append({
                "node_id": n.node_id,
                "ip": n.ip,
                "port": n.port,
                "responsive": False,
                "error": str(e)
            })

    return health_status

@app.get("/debug/node-status")
async def node_status(request: Request):
    """
    Debug endpoint to check node status
    """
    node = getattr(request.app.state, "node", None)
    try:
        return {
            "node_initialized": node is not None,
            "node_id": node.node_id if node else None,
            "ip": node.advertise_ip if node else None,
            "port": node.port if node else None,
            "routing_table_size": len(node.routing_table.get_all_nodes()) if node else 0,
            "is_running": hasattr(node, "_running") and node._running if node else False,
        }
    except Exception as e:
        logger.error(f"Error checking node status: {str(e)}", exc_info=True)
        return {"node_initialized": False, "error": str(e)}

@app.post("/products/{product_id}/image", response_model=ProductOut)
async def upload_product_image(
    request: Request,
    product_id: str,
    image: UploadFile = File(...),
    current_user: DBUser = Security(get_current_user, scopes=["products:write"]),
):
    """
    Upload an image associated with a product. The image will remain on the network
    for the same duration specified for the product.
    """
    try:
        node = check_node_initialized(request)
        logger.debug(f"Processing image upload for product {product_id}")

        # Retrieve existing product
        existing_product = await node.find_product(product_id, ENCRYPTION_PASSWORD)
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Determine how many days were originally requested.
        # If not present, default to 7.
        stored_days = existing_product.extended.get("storage_duration_days", 7)
        if not isinstance(stored_days, int) or stored_days <= 0:
            stored_days = 7

        # The user must pay 2 credits again? Or keep it as is? 
        # Here, per your existing approach, we require 2 credits to upload an image.
        # (We can keep it or adjust if you want a different cost.)
        required_credits = 2.0
        if not await deduct_credits_from_user(current_user.username, required_credits):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits to upload image.",
            )

        # Read the image data
        image_data = await image.read()
        file_hash = hashlib.sha256(image_data).hexdigest()

        # Calculate the same TTL as the product's
        product_ttl_seconds = stored_days * 86400
        
        # Store the image file with the same TTL
        await node.storage_service.store_file(
            file_hash, image_data, ttl=product_ttl_seconds
        )
        logger.debug(f"Image stored with TTL={stored_days} days (product-based).")

        # Append the info to the product
        if not existing_product.image_refs:
            existing_product.image_refs = []
        image_manifest = ImageManifest(
            file_hash=file_hash,
            file_name=image.filename,
            chunk_hashes=[],
        )
        existing_product.image_refs.append(image_manifest)

        # Re-store the updated product record (with references to the new image)
        await node.store_product(existing_product, ENCRYPTION_PASSWORD, ttl=product_ttl_seconds)

        return ProductOut(
            product_id=existing_product.product_id,
            core=existing_product.core,
            extended=existing_product.extended,
            image_refs=existing_product.image_refs,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}/image")
async def get_product_image(
    request: Request,
    product_id: str,
    current_user: DBUser = Security(get_current_user, scopes=["products:read"]),
):
    """
    Retrieve a single image associated with a product.
    (CHANGED) Now deducts 1 credit from the user.
    """
    # (CHANGED) Deduct 1 credit from the user before proceeding
    required_credits = 1.0
    if not await deduct_credits_from_user(current_user.username, required_credits):
        return JSONResponse(
            {"error": "Insufficient credits to retrieve product image."},
            status_code=status.HTTP_402_PAYMENT_REQUIRED
        )

    node = request.app.state.node
    if not node:
        return JSONResponse({"error": "Node not initialized"}, status_code=503)

    product = await node.find_product(product_id, ENCRYPTION_PASSWORD)
    if not product:
        return JSONResponse({"error": "Product not found"}, status_code=404)
    if not product.image_refs:
        return JSONResponse({"error": "Product has no image"}, status_code=404)

    image_manifest = product.image_refs[0]
    file_hash = image_manifest.file_hash

    try:
        image_data = await node.storage_service.retrieve_file_from_network(file_hash)
        if not image_data:
            return JSONResponse({"error": "Failed to retrieve image"}, status_code=500)
    except Exception as e:
        node.logger.error(f"Error retrieving image: {e}", exc_info=True)
        return JSONResponse({"error": "Failed to retrieve image"}, status_code=500)

    content_type, _ = mimetypes.guess_type(image_manifest.file_name)
    if content_type is None:
        content_type = "application/octet-stream"

    return Response(content=image_data, media_type=content_type)

@app.get("/products/{product_id}/images")
async def get_all_product_images(
    request: Request,
    product_id: str,
    current_user: DBUser = Security(get_current_user, scopes=["products:read"]),
):
    """
    Retrieve all images associated with a product as a single ZIP file.
    Deducts 1 credit from the user to allow retrieval.
    """
    # (CHANGED) Deduct 1 credit from the user
    required_credits = 1.0
    if not await deduct_credits_from_user(current_user.username, required_credits):
        return JSONResponse(
            {"error": "Insufficient credits to retrieve images."},
            status_code=status.HTTP_402_PAYMENT_REQUIRED
        )

    node = request.app.state.node
    if not node:
        return JSONResponse({"error": "Node not initialized"}, status_code=503)

    product = await node.find_product(product_id, ENCRYPTION_PASSWORD)
    if not product:
        return JSONResponse({"error": "Product not found"}, status_code=404)

    if not product.image_refs:
        return JSONResponse({"error": "No images found for this product"}, status_code=404)

    # Prepare an in-memory ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        # Loop through each image manifest, retrieve its file bytes, and write to the ZIP
        for idx, image_manifest in enumerate(product.image_refs, start=1):
            file_hash = image_manifest.file_hash
            try:
                image_data = await node.storage_service.retrieve_file_from_network(file_hash)
                if not image_data:
                    continue  # Or raise an error if you prefer
            except Exception as e:
                node.logger.error(f"Error retrieving image: {e}", exc_info=True)
                continue

            # Use either the original filename or a fallback name
            filename_in_zip = image_manifest.file_name or f"image_{idx}.dat"
            zipf.writestr(filename_in_zip, image_data)

    zip_buffer.seek(0)

    # Stream the ZIP file back to the client
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="images_{product_id}.zip"'}
    )

@app.get("/routing-table")
async def get_routing_table(request: Request):
    """
    Endpoint to retrieve the nodes in the routing table.
    """
    node = check_node_initialized(request)

    nodes = node.routing_table.get_all_nodes()
    return {
        "node_id": node.node_id,
        "total_nodes": len(nodes),
        "nodes": [
            {
                "node_id": n.node_id,
                "ip": n.ip,
                "port": n.port,
                "tcp_port": n.tcp_port,
                "is_unresponsive": n.is_unresponsive,
            }
            for n in nodes
        ],
    }