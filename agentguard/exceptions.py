class AgentGuardError(Exception):
    """Base exception for AgentGuard SDK"""
    pass

class AgentGuardAuthError(AgentGuardError):
    """Invalid or missing token or master key"""
    pass

class AgentGuardCredentialError(AgentGuardError):
    """Credential not found or access denied"""
    pass

class AgentGuardMasterKeyError(AgentGuardError):
    """Wrong master key"""
    pass

class AgentGuardProxyError(AgentGuardError):
    """Proxy unreachable or bad gateway"""
    pass

class AgentGuardRateLimitError(AgentGuardError):
    """Too many requests"""
    pass
