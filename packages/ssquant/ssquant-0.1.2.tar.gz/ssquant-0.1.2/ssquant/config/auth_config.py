"""
API认证配置文件

此文件用于存储API认证信息，避免在代码中硬编码敏感信息。
请在使用前填写您的用户名和密码，并确保不要将此文件提交到版本控制系统。
"""

# API认证信息
API_USERNAME = "13453145450"  # 请填写您的API用户名/手机号
API_PASSWORD = "songshu123"  # 请填写您的API密码

def get_api_auth():
    """
    获取API认证信息
    
    Returns:
        tuple: (username, password)
    """
    return API_USERNAME, API_PASSWORD 