"""FastAPI dependencies (database, auth, tenant resolution)."""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.tenant import Tenant
from app.models.user import User

# This is a placeholder for actual Clerk auth integration.
# In a real implementation, this would verify the JWT token from Clerk.
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Gets the current user from the authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    
    # Placeholder: Extract user ID from token
    # For now, we'll just mock it. In production, use clerk-backend-api.
    token = auth_header.split(" ")[1]
    
    # MOCK implementation
    if token == "mock-token":
        # In a real app, query the user from DB based on clerk_user_id
        return User(id="mock-user-id", tenant_id="mock-tenant-id", role="ADMIN")
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )


async def get_current_tenant(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """Gets the tenant associated with the current user."""
    tenant = await db.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return tenant


def verify_internal_api_key(request: Request):
    """Verifies internal API key for n8n to FastAPI communication."""
    from app.config import settings
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != settings.N8N_INTERNAL_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal API key",
        )
