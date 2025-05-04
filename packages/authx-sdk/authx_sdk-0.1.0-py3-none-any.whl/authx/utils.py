# authx_sdk/utils.py

def normalize_scope(scopes: list[str]) -> str:
    """
    Normalizes a list of OAuth scopes into a single flattened scope_key.
    
    Example:
    ["https://www.googleapis.com/auth/gmail.readonly", 
     "https://www.googleapis.com/auth/userinfo.email"]
    
    → "wwwgoogleapiscomauthgmailreadonlywwwgoogleapiscomauthuserinfoemail"
    """
    stripped = [s.replace("https://", "").replace("/", "") for s in scopes]
    sorted_scope = sorted(stripped)
    return ''.join(sorted_scope)
