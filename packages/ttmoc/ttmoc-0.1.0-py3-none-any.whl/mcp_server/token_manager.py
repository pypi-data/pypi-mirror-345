#!/usr/bin/env python3
import time
import logging
import traceback
from typing import Optional, Dict, Any, Callable
from azure.identity import ChainedTokenCredential, AzureCliCredential, InteractiveBrowserCredential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenManager:
    """
    Manages Azure AD token acquisition and caching, similar to the TypeScript implementation.
    Handles token refresh and provides thread-safe access to valid tokens.
    """
    
    def __init__(self, credential: ChainedTokenCredential, scope: str, allow_dev_token: bool = False):
        """
        Initialize the token manager.
        
        Args:
            credential: The Azure credential to use for token acquisition
            scope: The scope to request for the token
            allow_dev_token: Whether to allow fallback to dev token
        """
        self.credential = credential
        self.scope = scope
        self.allow_dev_token = allow_dev_token
        self.current_token = None
        self.token_expires_at = 0
        self.refresh_in_progress = False
    
    async def refresh_token(self) -> Dict[str, Any]:
        """
        Refresh the token using the credential.
        
        Returns:
            Dict containing the token and expiration
        """
        if self.refresh_in_progress:
            logger.debug("Token refresh already in progress, waiting...")
            # Simple wait and retry approach
            for _ in range(10):  # Try 10 times with a small delay
                time.sleep(0.5)
                if not self.refresh_in_progress and self.current_token:
                    return {
                        "token": self.current_token,
                        "expires_at": self.token_expires_at
                    }
            
            # If we still don't have a token after waiting
            logger.warning("Timeout waiting for token refresh")
        
        self.refresh_in_progress = True
        
        try:
            logger.info(f"Refreshing token for scope: {self.scope}")
            
            # Try different scopes in sequence if the primary one fails
            scopes_to_try = [
                self.scope,
                "https://graph.microsoft.com/.default",
                "https://management.azure.com/.default",
                ""  # Empty scope as last resort
            ]
            
            # Remove duplicates while preserving order
            unique_scopes = []
            for scope in scopes_to_try:
                if scope not in unique_scopes:
                    unique_scopes.append(scope)
            
            # Try each scope in sequence
            last_error = None
            for scope in unique_scopes:
                try:
                    if not scope:
                        logger.info("Trying with empty scope as last resort")
                    else:
                        logger.info(f"Trying to get token with scope: {scope}")
                    
                    token_response = self.credential.get_token(scope)
                    
                    if token_response and token_response.token:
                        logger.info(f"Successfully acquired token with scope: {scope}")
                        logger.info(f"Token expires in: {(token_response.expires_on - time.time()) / 60:.1f} minutes")
                        
                        self.current_token = token_response.token
                        self.token_expires_at = token_response.expires_on
                        
                        return {
                            "token": self.current_token,
                            "expires_at": self.token_expires_at
                        }
                except Exception as e:
                    last_error = e
                    logger.warning(f"Failed to get token with scope {scope}: {str(e)}")
            
            # If we get here, all scope attempts failed
            if self.allow_dev_token:
                logger.warning("All token acquisition attempts failed, using dev_token")
                self.current_token = "dev_token"
                self.token_expires_at = time.time() + 3600  # 1 hour expiry for dev token
                
                return {
                    "token": self.current_token,
                    "expires_at": self.token_expires_at
                }
            
            # Re-raise the last error if we can't use dev token
            if last_error:
                raise last_error
            else:
                raise Exception("Failed to acquire token with all scopes")
            
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            logger.error(traceback.format_exc())
            
            if self.allow_dev_token:
                logger.warning("Using development token after error - INSECURE")
                self.current_token = "dev_token"
                self.token_expires_at = time.time() + 3600  # 1 hour expiry for dev token
                
                return {
                    "token": self.current_token,
                    "expires_at": self.token_expires_at
                }
            raise
        finally:
            self.refresh_in_progress = False
    
    async def get_token(self) -> Dict[str, Any]:
        """
        Get a valid token, refreshing if necessary.
        
        Returns:
            Dict containing the token and expiration
        """
        # If we have a valid token that's not about to expire (5 min buffer), return it
        current_time = time.time()
        if self.current_token and self.token_expires_at > current_time + 300:
            logger.debug(f"Using cached token, valid for {(self.token_expires_at - current_time) / 60:.1f} more minutes")
            return {
                "token": self.current_token,
                "expires_at": self.token_expires_at
            }
        
        # Otherwise, refresh the token
        return await self.refresh_token()
    
    async def get_valid_token(self) -> str:
        """
        Get just the token string.
        
        Returns:
            The token string
        """
        token_info = await self.get_token()
        return token_info["token"]


def create_default_credential(tenant_id: Optional[str] = None) -> ChainedTokenCredential:
    """
    Create a default credential chain that tries Azure CLI first, then interactive browser.
    
    Args:
        tenant_id: Optional tenant ID to use for authentication
        
    Returns:
        A ChainedTokenCredential instance
    """
    try:
        # Use chained credential to try CLI first, then interactive browser
        credential = ChainedTokenCredential(
            AzureCliCredential(),
            InteractiveBrowserCredential(tenant_id=tenant_id)
        )
        logger.info("Azure credentials initialized successfully")
        return credential
    except Exception as e:
        logger.error(f"Error initializing Azure credentials: {str(e)}")
        logger.error(traceback.format_exc())
        raise
