import secrets
import os

def generate_production_keys():
    print("🔐 Generating Production Keys...")
    print("=" * 50)
    
    # Generate secret key
    secret_key = secrets.token_hex(32)
    
    print("✅ Generated SECRET_KEY:")
    print(secret_key)
    print()
    
    # Update .env file
    env_content = f"""# Production Environment Variables
OPENAI_API_KEY=your_actual_openai_key_here
FLASK_ENV=production
SECRET_KEY={secret_key}

# Research Configuration
RESEARCH_SOURCES=3
MAX_CONTENT_LENGTH=2500
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Updated .env file with production settings")
    print()
    print("📝 Next steps:")
    print("1. Replace 'your_actual_openai_key_here' with your real OpenAI API key")
    print("2. Your Flask app is now production-ready!")
    print("3. Never commit .env to version control")

if __name__ == "__main__":
    generate_production_keys()