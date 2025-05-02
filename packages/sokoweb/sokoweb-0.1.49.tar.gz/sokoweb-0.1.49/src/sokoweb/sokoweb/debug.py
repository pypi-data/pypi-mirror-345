from fastapi import APIRouter, Request
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger("debug-proofs")

# This endpoint is for debugging only.
@router.get("/debug/proof")
async def debug_proof(request: Request):
    """
    Debug endpoint to simulate a bandwidth proof.
    This will generate a proof for a dummy session (e.g. serving 1MB of data)
    and then verify & award credits. Check the logs for detailed output.
    """
    session_id = "test_session_123"
    bytes_served = 1000000  # 1MB

    # Get the node from the application state
    node = request.app.state.node
    proof_manager = node.proof_of_bandwidth_manager
    proof = await proof_manager.generate_proof(session_id, bytes_served)

    verified = await proof_manager.verify_and_award(proof)
    if verified:
        logger.info("Proof simulation complete: Credits awarded.")
        return {"message": "Proof simulation complete: Credits awarded."}
    else:
        logger.error("Proof simulation failed.")
        return {"message": "Proof simulation failed."}